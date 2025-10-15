import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from bson import ObjectId
from app.config import settings
from celery import Celery
from datetime import datetime
from app.services.parser import ContractParser
from app.services.scoring import ContractScorer
from app.utils.pdf_extractor import PDFExtractor

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


celery_app = Celery(
    "contract_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

mongodb_client = None
db = None
fs_bucket = None


@app.on_event("startup")
async def startup_db_client():
    global mongodb_client, db, fs_bucket
    mongodb_client = AsyncIOMotorClient(settings.MONGO_URL)
    db = mongodb_client[settings.MONGO_DB]
    fs_bucket = AsyncIOMotorGridFSBucket(db)

@app.on_event("shutdown")
async def shutdown_db_client():
    if mongodb_client:
        mongodb_client.close()


# Celery task for async processing
@celery_app.task(name="process_contract")
def process_contract_task(contract_id: str, file_path: str):
    """Background task to process contract"""
    from pymongo import MongoClient
    
    # Sync MongoDB connection for Celery
    sync_client = MongoClient(settings.MONGO_URL)
    sync_db = sync_client[settings.MONGO_DB]
    
    try:
        # Update status to processing
        sync_db.contracts.update_one(
            {"_id": ObjectId(contract_id)},
            {
                "$set": {
                    "status": "processing",
                    "progress": 10,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Extract text from PDF
        extractor = PDFExtractor()
        pdf_text = extractor.extract_text(file_path)
        
        sync_db.contracts.update_one(
            {"_id": ObjectId(contract_id)},
            {"$set": {"progress": 30}}
        )
        
        # Parse contract using LLM
        parser = ContractParser()
        parsed_data = parser.parse_contract(pdf_text)
        
        sync_db.contracts.update_one(
            {"_id": ObjectId(contract_id)},
            {"$set": {"progress": 60}}
        )
        
        # Calculate scores
        scorer = ContractScorer()
        score_result = scorer.calculate_score(parsed_data)
        
        # Prepare final data
        contract_data = {
            **parsed_data,
            "overall_score": score_result["overall_score"],
            "category_scores": score_result["category_scores"],
            "missing_fields": score_result["missing_fields"],
            "confidence_levels": score_result["confidence_levels"]
        }
        
        # Update contract with results
        sync_db.contracts.update_one(
            {"_id": ObjectId(contract_id)},
            {
                "$set": {
                    "status": "completed",
                    "progress": 100,
                    "parsed_data": contract_data,
                    "completed_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
    except Exception as e:
        # Update with error status
        sync_db.contracts.update_one(
            {"_id": ObjectId(contract_id)},
            {
                "$set": {
                    "status": "failed",
                    "error": str(e),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        raise
    
    finally:
        sync_client.close()


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An internal error occurred."},
    )


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def say_hello():
    return {"message": "Hello"}


@app.post("/contracts/upload")
async def upload_contract():
    return {"message": "Contract uploaded successfully."}


@app.get("/contracts/{contract_id}/status")
async def get_contract_status(contract_id: str):
    return {"contract_id": contract_id, "status": "active"}


@app.get("/contracts/{contract_id}")
async def get_contract_data(contract_id: str):
    return {"contract_id": contract_id, "status": "executed"}


@app.get("/contracts")
async def get_all_contracts():
    return [
        {"contract_id": "1", "status": "executed"},
        {"contract_id": "2", "status": "active"},
    ]


@app.get("/contracts/{contract_id}/download")
async def download_contract(contract_id: str):
    return {"message": f"Contract {contract_id} downloaded successfully."}

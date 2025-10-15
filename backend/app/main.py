import os
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from bson import ObjectId
from app.config import settings
from celery import Celery
from datetime import datetime
from app.services.parser import ContractParser
from app.services.scoring import ContractScorer
from app.utils.pdf_extractor import PDFExtractor
from app.models.contract import ContractResponse, ContractStatus, ProcessingStatus
from typing import List


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
    print("Connecting to MongoDB...")
    global mongodb_client, db, fs_bucket
    try:
        mongodb_client = AsyncIOMotorClient(settings.MONGO_URL)
        db = mongodb_client[settings.MONGO_DB]
        fs_bucket = AsyncIOMotorGridFSBucket(db)
        print("Connected to MongoDB!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise e


@app.on_event("shutdown")
async def shutdown_db_client():
    if mongodb_client:
        try:
            print("Closing MongoDB connection...")
            mongodb_client.close()
        except Exception as e:
            print(f"Error closing MongoDB connection: {e}")


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
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        # Extract text from PDF
        extractor = PDFExtractor()
        pdf_text = extractor.extract_text(file_path)

        sync_db.contracts.update_one(
            {"_id": ObjectId(contract_id)}, {"$set": {"progress": 30}}
        )

        # Parse contract using LLM
        parser = ContractParser()
        parsed_data = parser.parse_contract(pdf_text)

        sync_db.contracts.update_one(
            {"_id": ObjectId(contract_id)}, {"$set": {"progress": 60}}
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
            "confidence_levels": score_result["confidence_levels"],
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
                    "updated_at": datetime.utcnow(),
                }
            },
        )

    except Exception as e:
        # Update with error status
        sync_db.contracts.update_one(
            {"_id": ObjectId(contract_id)},
            {
                "$set": {
                    "status": "failed",
                    "error": str(e),
                    "updated_at": datetime.utcnow(),
                }
            },
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


@app.post("/contracts/upload", response_model=ContractResponse)
async def upload_contract(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        return JSONResponse(
            status_code=400,
            content={"message": "Only PDF files are supported."},
        )

    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        return JSONResponse(
            status_code=400,
            content={
                "message": f"File size exceeds the maximum allowed size of {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
            },
        )

    await file.seek(0)
    try:
        file_id = await fs_bucket.upload_from_stream(
            filename=file.filename,
            source=file.file,
            metadata={
                "contentType": file.content_type,
                "uploaded_at": datetime.utcnow(),
            },
        )
        contract_doc = {
            "filename": file.filename,
            "file_id": str(file_id),
            "file_size": len(contents),
            "status": "pending",
            "progress": 0,
            "uploaded_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db.contracts.insert_one(contract_doc)
        contract_id = str(result.inserted_id)
        folder = "/tmp"
        os.makedirs(folder, exist_ok=True)
        # Save temporary file for processing
        temp_file = os.path.join(folder, f"{contract_id}.pdf")
        with open(temp_file, "wb") as f:
            f.write(contents)

        # Trigger background processing
        process_contract_task.delay(contract_id, temp_file)

        return ContractResponse(
            contract_id=contract_id,
            filename=file.filename,
            status=ContractStatus.pending,
            message="Contract uploaded successfully and is pending processing.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/contracts/{contract_id}/status", response_model=ProcessingStatus)
async def get_contract_status(contract_id: str):
    try:
        contract = await db.contracts.find_one({"_id": ObjectId(contract_id)})
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        return ProcessingStatus(
            contract_id=contract_id,
            status=contract["status"],
            progress=contract["progress"],
            error=contract.get("error"),
            updated_at=contract["updated_at"],
        )
    except Exception as e:
        if "not found" in str(e).lower():
            raise
        raise HTTPException(status_code=500, detail=str(e))


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


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def say_hello():
    return {"message": "Hello"}

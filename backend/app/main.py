from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db():
    print("Starting up...")

@app.on_event("shutdown")
async def shutdown_db():
    print("Shutting down...")


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
    return [{"contract_id": "1", "status": "executed"}, {"contract_id": "2", "status": "active"}]

@app.get("/contracts/{contract_id}/download")
async def download_contract(contract_id: str):
    return {"message": f"Contract {contract_id} downloaded successfully."}



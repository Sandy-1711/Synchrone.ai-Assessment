from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from bson import ObjectId
from typing import Optional


class ContractStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class ContractResponse(BaseModel):
    contract_id: str
    filename: str
    status: ContractStatus
    message: str

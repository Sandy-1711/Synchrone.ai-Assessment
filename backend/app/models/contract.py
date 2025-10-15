from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from bson import ObjectId
from typing import Optional, List


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


class ProcessingStatus(BaseModel):
    contract_id: str
    status: ContractStatus
    progress: int = 0
    error: Optional[str] = None
    updated_at: datetime


class ContractListItem(BaseModel):
    contract_id: str
    filename: str
    status: str
    uploaded_at: datetime
    progress: int = 0
    overall_score: Optional[float] = None
    file_size: Optional[int] = None


class ContractListResponse(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
    items: List[ContractListItem]

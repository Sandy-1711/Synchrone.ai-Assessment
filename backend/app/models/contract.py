from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from bson import ObjectId
from typing import Optional, List, Dict, Tuple, Any


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
    status: ContractStatus
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


class ContractData(BaseModel):
    contract_id: str
    filename: str
    uploaded_at: datetime
    completed_at: Optional[datetime] = None
    overall_score: float
    category_scores: Dict[str, float]
    party_identification: Dict[str, Any]
    account_information: Dict[str, Any]
    financial_details: Dict[str, Any]
    payment_structure: Dict[str, Any]
    revenue_classification: Dict[str, Any]
    sla_terms: Dict[str, Any]
    missing_fields: List[str]
    confidence_levels: Dict[str, str]

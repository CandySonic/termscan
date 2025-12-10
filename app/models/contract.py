"""
Pydantic models for contract analysis
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum


class ContractType(str, Enum):
    """Supported contract types"""
    EMPLOYMENT = "employment"
    SERVICE = "service"
    SALE = "sale"
    LEASE = "lease"
    PARTNERSHIP = "partnership"
    INVESTMENT = "investment"
    LOAN = "loan"
    LICENSING = "licensing"
    NDA = "nda"
    GENERAL = "general"


class FlagSeverity(str, Enum):
    """Severity levels for flagged issues"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class FlagCategory(str, Enum):
    """Categories of Islamic compliance issues"""
    RIBA = "riba"
    GHARAR = "gharar"
    MAYSIR = "maysir"
    HARAM_INDUSTRY = "haram_industry"
    DHULM = "dhulm"
    TADLIS = "tadlis"
    OTHER = "other"


# Request Models

class ContractAnalyzeRequest(BaseModel):
    """Request to analyze a contract"""
    text: str = Field(..., min_length=50, max_length=100000, description="Contract text to analyze")
    type: ContractType = Field(default=ContractType.GENERAL, description="Type of contract")
    language: str = Field(default="en", description="Language of the contract (ISO 639-1)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "This Employment Agreement is entered into between Company X and Employee Y...",
                "type": "employment",
                "language": "en"
            }
        }


class ContractUploadRequest(BaseModel):
    """Request to upload a contract file (PDF/DOCX)"""
    type: ContractType = Field(default=ContractType.GENERAL)
    language: str = Field(default="en")


# Response Models

class ContractFlag(BaseModel):
    """A flagged issue in the contract"""
    severity: FlagSeverity
    category: FlagCategory
    clause: str = Field(..., description="The problematic clause or text")
    explanation: str = Field(..., description="Why this is problematic")
    suggestion: str = Field(..., description="How to fix it")
    reference: Optional[str] = Field(None, description="Scholarly reference")


class ContractScores(BaseModel):
    """Compliance scores for a contract"""
    overall: int = Field(..., ge=0, le=100, description="Overall compliance score")
    riba_free: int = Field(..., ge=0, le=100, description="Freedom from interest/usury")
    gharar_free: int = Field(..., ge=0, le=100, description="Clarity and certainty")
    halal_industry: int = Field(..., ge=0, le=100, description="Permissible business activity")
    fair_terms: int = Field(..., ge=0, le=100, description="Fairness and balance")
    transparency: int = Field(..., ge=0, le=100, description="Disclosure and honesty")


class ContractAnalysis(BaseModel):
    """Full contract analysis result"""
    id: str = Field(..., description="Unique analysis ID")
    status: Literal["pending", "processing", "completed", "failed"] = "completed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    contract_type: ContractType
    
    summary: str = Field(..., description="Brief overall assessment")
    scores: ContractScores
    flags: List[ContractFlag] = Field(default_factory=list)
    positive_aspects: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    scholarly_notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "contract_abc123",
                "status": "completed",
                "created_at": "2024-01-15T10:30:00Z",
                "contract_type": "employment",
                "summary": "This contract is largely compliant with Islamic principles with minor issues.",
                "scores": {
                    "overall": 85,
                    "riba_free": 100,
                    "gharar_free": 70,
                    "halal_industry": 100,
                    "fair_terms": 85,
                    "transparency": 80
                },
                "flags": [
                    {
                        "severity": "warning",
                        "category": "gharar",
                        "clause": "Bonus subject to company discretion",
                        "explanation": "Ambiguous bonus terms may constitute gharar",
                        "suggestion": "Specify clear bonus criteria and amounts",
                        "reference": "Sahih Muslim 1513"
                    }
                ],
                "positive_aspects": [
                    "Clear salary terms with no interest",
                    "Fair termination notice period"
                ],
                "recommendations": [
                    "Clarify bonus calculation method",
                    "Add dispute resolution clause"
                ],
                "scholarly_notes": "Analysis based on majority scholarly opinion."
            }
        }


class ContractSubmitResponse(BaseModel):
    """Response when submitting a contract for analysis"""
    id: str
    status: Literal["pending", "processing"] = "processing"
    message: str = "Contract submitted for analysis"
    estimated_seconds: int = 30


class ScoreOnlyResponse(BaseModel):
    """Quick score response"""
    id: str
    scores: ContractScores
    quick_summary: str


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    code: str

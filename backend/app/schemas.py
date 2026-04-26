from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

DocumentType = Literal["RFP", "SOW", "Contract", "Proposal", "General Requirement Note", "Unknown"]
RiskLevel = Literal["High", "Medium", "Low", "Unknown"]

class DocumentClassification(BaseModel):
    document_type: DocumentType = Field(
        default="Unknown",
        description="The type of document, e.g., RFP, SOW, Contract, Proposal, General Requirement Note",
    )
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score between 0 and 1")

class ExtractedEntities(BaseModel):
    client_name: Optional[str] = Field(None, description="Name of the client if mentioned")
    timeline: Optional[str] = Field(None, description="Project timeline or duration")
    deliverables: List[str] = Field(default_factory=list, description="List of deliverables")
    technologies: List[str] = Field(default_factory=list, description="List of technologies, tools, or platforms mentioned")
    stakeholders: List[str] = Field(default_factory=list, description="Key stakeholders or roles")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies or prerequisites")

class RiskFlag(BaseModel):
    risk_level: RiskLevel = Field(default="Unknown", description="High, Medium, Low, or Unknown")
    description: str = Field(description="Description of the risk (e.g., missing acceptance criteria)")
    section: Optional[str] = Field(None, description="The section of the document where this risk applies")

class RiskAssessment(BaseModel):
    risks: List[RiskFlag] = Field(default_factory=list, description="List of identified risks")
    overall_risk_score: RiskLevel = Field(default="Unknown", description="Overall risk level")

class DocumentSummary(BaseModel):
    business_summary: str = Field(description="A concise summary of the document for non-technical teams")
    technical_summary: Optional[str] = Field(None, description="A technical summary if applicable")

class DocumentAnalysisResult(BaseModel):
    file_name: str
    document_classification: Optional[DocumentClassification] = None
    extracted_entities: Optional[ExtractedEntities] = None
    risk_assessment: Optional[RiskAssessment] = None
    summary: Optional[DocumentSummary] = None
    similar_projects: List[Dict[str, Any]] = Field(default_factory=list, description="List of similar past projects")

class JobResponse(BaseModel):
    job_id: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: Literal["processing", "completed", "failed"]
    current_step: Optional[str] = None
    progress: int = Field(default=0, ge=0, le=100)
    message: Optional[str] = None
    result: Optional[DocumentAnalysisResult] = None
    error: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

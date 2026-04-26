from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DocumentClassification(BaseModel):
    document_type: str = Field(description="The type of document, e.g., RFP, SOW, Contract, Proposal, General Requirement")
    confidence: float = Field(description="Confidence score between 0 and 1")

class ExtractedEntities(BaseModel):
    client_name: Optional[str] = Field(None, description="Name of the client if mentioned")
    timeline: Optional[str] = Field(None, description="Project timeline or duration")
    deliverables: List[str] = Field(default_factory=list, description="List of deliverables")
    technologies: List[str] = Field(default_factory=list, description="List of technologies, tools, or platforms mentioned")
    stakeholders: List[str] = Field(default_factory=list, description="Key stakeholders or roles")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies or prerequisites")

class RiskFlag(BaseModel):
    risk_level: str = Field(description="High, Medium, or Low")
    description: str = Field(description="Description of the risk (e.g., missing acceptance criteria)")
    section: Optional[str] = Field(None, description="The section of the document where this risk applies")

class RiskAssessment(BaseModel):
    risks: List[RiskFlag] = Field(default_factory=list, description="List of identified risks")
    overall_risk_score: str = Field(description="Overall risk level: High, Medium, or Low")

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

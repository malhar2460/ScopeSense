from typing import TypedDict, Optional, Dict, Any, List
from langgraph.graph import StateGraph, END

from app.schemas import (
    DocumentAnalysisResult,
    DocumentClassification,
    ExtractedEntities,
    RiskAssessment,
    DocumentSummary
)
from app.modules.classifier import DocumentClassifier
from app.modules.extractor import EntityExtractor
from app.modules.risk_analyzer import RiskAnalyzer
from app.modules.summarizer import DocumentSummarizer
from app.modules.retriever import DocumentRetriever

# Define State
class GraphState(TypedDict):
    file_name: str
    text: str
    classification: Optional[DocumentClassification]
    extracted: Optional[ExtractedEntities]
    risks: Optional[RiskAssessment]
    summary: Optional[DocumentSummary]
    similar_projects: List[Dict[str, Any]]
    final_result: Optional[DocumentAnalysisResult]

# Node Functions
async def classify_node(state: GraphState):
    classifier = DocumentClassifier()
    result = await classifier.classify(state["text"])
    return {"classification": result}

async def extract_node(state: GraphState):
    extractor = EntityExtractor()
    result = await extractor.extract(state["text"])
    return {"extracted": result}

async def analyze_risk_node(state: GraphState):
    analyzer = RiskAnalyzer()
    result = await analyzer.analyze(state["text"])
    return {"risks": result}

async def summarize_node(state: GraphState):
    summarizer = DocumentSummarizer()
    result = await summarizer.summarize(state["text"])
    return {"summary": result}

async def retrieve_node(state: GraphState):
    retriever = DocumentRetriever()
    result = await retriever.find_similar_projects(state["text"])
    return {"similar_projects": result}

def compile_result_node(state: GraphState):
    result = DocumentAnalysisResult(
        file_name=state["file_name"],
        document_classification=state.get("classification"),
        extracted_entities=state.get("extracted"),
        risk_assessment=state.get("risks"),
        summary=state.get("summary"),
        similar_projects=state.get("similar_projects", [])
    )
    return {"final_result": result}

# Build Graph
def build_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("classify", classify_node)
    workflow.add_node("extract", extract_node)
    workflow.add_node("analyze_risk", analyze_risk_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("compile", compile_result_node)

    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "extract")
    workflow.add_edge("extract", "analyze_risk")
    workflow.add_edge("analyze_risk", "summarize")
    workflow.add_edge("summarize", "retrieve")
    workflow.add_edge("retrieve", "compile")
    workflow.add_edge("compile", END)

    return workflow.compile()

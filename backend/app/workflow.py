from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from app.schemas import (
    DocumentAnalysisResult,
    DocumentClassification,
    ExtractedEntities,
    RiskAssessment,
    DocumentSummary
)
from app.modules.extractor import EntityExtractor
from app.modules.classifier import DocumentClassifier
from app.modules.risk_analyzer import RiskAnalyzer
from app.modules.retriever import DocumentRetriever
from app.modules.summarizer import DocumentSummarizer

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
    classifier = DocumentClassifier()
    extractor = EntityExtractor()
    analyzer = RiskAnalyzer()
    summarizer = DocumentSummarizer()
    retriever = DocumentRetriever()

    async def classify_node(state: GraphState):
        result = await classifier.classify(state["text"])
        return {"classification": result}

    async def extract_node(state: GraphState):
        result = await extractor.extract(state["text"])
        return {"extracted": result}

    async def analyze_risk_node(state: GraphState):
        result = await analyzer.analyze(state["text"])
        return {"risks": result}

    async def summarize_node(state: GraphState):
        result = await summarizer.summarize(state["text"])
        return {"summary": result}

    async def retrieve_node(state: GraphState):
        result = await retriever.find_similar_projects(state["text"])
        return {"similar_projects": result}

    workflow = StateGraph(GraphState)

    workflow.add_node("classify", classify_node)
    workflow.add_node("extract", extract_node)
    workflow.add_node("analyze_risk", analyze_risk_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("compile", compile_result_node)

    # These tasks are independent and can run in parallel for faster throughput.
    workflow.add_edge(START, "classify")
    workflow.add_edge(START, "extract")
    workflow.add_edge(START, "analyze_risk")
    workflow.add_edge(START, "summarize")
    workflow.add_edge(START, "retrieve")

    workflow.add_edge("classify", "compile")
    workflow.add_edge("extract", "compile")
    workflow.add_edge("analyze_risk", "compile")
    workflow.add_edge("summarize", "compile")
    workflow.add_edge("retrieve", "compile")
    workflow.add_edge("compile", END)

    return workflow.compile()

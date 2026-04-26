import hashlib
import math
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List

import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings


TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9\-_/]{1,}")


@dataclass(frozen=True)
class DemoProject:
    project_name: str
    summary: str
    content: str
    sector: str
    document_type: str


DEMO_PROJECTS: List[DemoProject] = [
    DemoProject(
        project_name="Civic Service Portal Modernization",
        summary="Government portal consolidation program with compliance-heavy workflows and SLA monitoring.",
        content=(
            "RFP for city service portal modernization including permitting, complaints, and appointment workflows. "
            "Required integrations include GIS systems, ERP billing, and state identity validation services. "
            "Program risk factors include compressed timeline, security review windows, and acceptance criteria gaps."
        ),
        sector="Public Sector",
        document_type="RFP",
    ),
    DemoProject(
        project_name="State Analytics & Reporting Platform",
        summary="Data platform procurement focused on governance, auditability, and secure reporting.",
        content=(
            "Request for proposal for analytics platform with strict compliance controls, automated audit trails, "
            "role-based access, and executive reporting dashboards. Required technologies include cloud data warehousing, "
            "ETL orchestration, and enterprise identity integration."
        ),
        sector="Public Sector",
        document_type="RFP",
    ),
    DemoProject(
        project_name="Insurance Claims Workflow Rebuild",
        summary="SOW for phased portal migration with API integration and automated document intake.",
        content=(
            "Statement of work for redesigning claims intake and review workflows. Includes React frontend, "
            "FastAPI backend services, PostgreSQL, and secure document processing. Risks include dependency on third-party APIs "
            "and undefined acceptance criteria for edge-case claims."
        ),
        sector="Insurance",
        document_type="SOW",
    ),
    DemoProject(
        project_name="Managed Services Renewal and SLA Restructure",
        summary="Contract renewal initiative centered on support ownership, penalties, and response SLAs.",
        content=(
            "Contract amendment defining escalation ownership, response-time commitments, penalty clauses, and service credits. "
            "High-risk clauses include legal indemnity language, security incident obligations, and performance penalties."
        ),
        sector="Enterprise IT",
        document_type="Contract",
    ),
    DemoProject(
        project_name="Healthcare Contact Center Transformation",
        summary="Multi-phase proposal with stakeholder training, platform migration, and governance controls.",
        content=(
            "Proposal for contact center modernization using cloud telephony, CRM integration, workflow automation, "
            "and analytics dashboards. Includes phased rollout, change management, and KPI tracking."
        ),
        sector="Healthcare",
        document_type="Proposal",
    ),
    DemoProject(
        project_name="University ERP and Student Services Integration",
        summary="Integration-heavy delivery program spanning ERP, identity, and student-facing service portals.",
        content=(
            "Program to integrate ERP records, identity systems, and student service workflows. Requires secure APIs, "
            "data synchronization pipelines, and compliance with institutional privacy obligations."
        ),
        sector="Education",
        document_type="SOW",
    ),
]


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "")).strip()


class HashingEmbeddingFunction(EmbeddingFunction[Documents]):
    """Deterministic, offline-safe embedding function for Chroma collections."""

    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    def __call__(self, input: Documents) -> Embeddings:
        return [self._embed(text) for text in input]

    def _embed(self, text: str) -> List[float]:
        tokens = TOKEN_PATTERN.findall((text or "").lower())
        vector = [0.0] * self.dimensions
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.sha1(token.encode("utf-8")).hexdigest()
            hash_int = int(digest, 16)
            index = hash_int % self.dimensions
            sign = 1.0 if ((hash_int >> 8) & 1) == 0 else -1.0
            weight = 1.0 + min(len(token), 12) / 12.0
            vector[index] += sign * weight

        norm = math.sqrt(sum(value * value for value in vector))
        if norm > 0:
            vector = [value / norm for value in vector]
        return vector


class DocumentRetriever:
    def __init__(self):
        self.persist_path = os.getenv(
            "CHROMA_PERSIST_DIR",
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma")),
        )
        self.collection_name = os.getenv("CHROMA_COLLECTION_NAME", "scopesense_similar_projects")
        self.max_results = max(1, int(os.getenv("SIMILAR_PROJECTS_TOP_K", "3")))
        self.minimum_similarity = float(os.getenv("SIMILARITY_MIN_SCORE", "0.12"))

        self.embedding_function = HashingEmbeddingFunction(dimensions=384)
        self.client = chromadb.PersistentClient(path=self.persist_path)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"},
        )

        self._seed_if_needed()

    def _seed_if_needed(self) -> None:
        if self.collection.count() > 0:
            return

        ids: List[str] = []
        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        for index, project in enumerate(DEMO_PROJECTS):
            ids.append(f"demo-project-{index + 1}")
            documents.append(normalize_text(project.content))
            metadatas.append(
                {
                    "project_name": project.project_name,
                    "summary": project.summary,
                    "sector": project.sector,
                    "document_type": project.document_type,
                    "seed_source": "builtin_demo",
                }
            )

        self.collection.add(ids=ids, documents=documents, metadatas=metadatas)

    @staticmethod
    def _distance_to_similarity(distance: float) -> float:
        # For cosine distance, similarity is approximately (1 - distance).
        similarity = 1.0 - float(distance)
        return max(0.0, min(1.0, similarity))

    async def find_similar_projects(self, text: str) -> List[Dict[str, Any]]:
        query_text = normalize_text(text)
        if not query_text:
            return []

        if self.collection.count() == 0:
            self._seed_if_needed()

        query_response = self.collection.query(
            query_texts=[query_text],
            n_results=min(self.max_results, max(1, self.collection.count())),
            include=["distances", "metadatas"],
        )

        metadatas = (query_response.get("metadatas") or [[]])[0]
        distances = (query_response.get("distances") or [[]])[0]
        candidates: List[Dict[str, Any]] = []

        for metadata, distance in zip(metadatas, distances):
            similarity_score = round(self._distance_to_similarity(distance), 2)
            candidates.append(
                {
                    "project_name": metadata.get("project_name", "Unnamed Project"),
                    "similarity_score": similarity_score,
                    "summary": metadata.get("summary", "No summary available."),
                    "sector": metadata.get("sector", "Unknown"),
                    "document_type": metadata.get("document_type", "Unknown"),
                }
            )

        high_confidence = [item for item in candidates if item["similarity_score"] >= self.minimum_similarity]
        if high_confidence:
            return high_confidence[: self.max_results]

        # Keep demo UX stable by returning nearest neighbors even when confidence is low.
        return candidates[: min(2, len(candidates))]

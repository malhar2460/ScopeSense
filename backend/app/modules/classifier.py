from app.schemas import DocumentClassification
from app.modules.base_llm import StructuredGroqClient, cleaned_excerpt

ALLOWED_TYPES = {"RFP", "SOW", "Contract", "Proposal", "General Requirement Note", "Unknown"}

class DocumentClassifier:
    def __init__(self):
        self.client = StructuredGroqClient(DocumentClassification, temperature=0.0)

    async def classify(self, text: str) -> DocumentClassification:
        excerpt = cleaned_excerpt(text, 5000)
        prompt = f"""
        You are classifying a procurement document.
        Return only:
        - document_type: one of [RFP, SOW, Contract, Proposal, General Requirement Note, Unknown]
        - confidence: decimal from 0 to 1

        Classification rules:
        - Use "Unknown" when the document is too short or ambiguous.
        - Prefer the closest business document type over "Unknown" when clear signals exist.

        Document text:
        {excerpt}
        """

        try:
            result = await self.client.invoke(prompt)
            normalized_type = result.document_type if result.document_type in ALLOWED_TYPES else "Unknown"
            normalized_confidence = max(0.0, min(1.0, float(result.confidence or 0.0)))
            return DocumentClassification(document_type=normalized_type, confidence=normalized_confidence)
        except Exception:
            return DocumentClassification(document_type="Unknown", confidence=0.0)

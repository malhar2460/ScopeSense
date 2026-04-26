from app.schemas import DocumentSummary
from app.modules.base_llm import StructuredGroqClient, cleaned_excerpt


def fallback_business_summary(text: str) -> str:
    compact = cleaned_excerpt(text, 450)
    if not compact:
        return "No readable business content was detected in the document."
    return compact


def fallback_technical_summary(text: str) -> str:
    lower_text = (text or "").lower()
    technical_markers = ["api", "database", "cloud", "security", "integration", "architecture", "deployment", "kubernetes"]
    if any(marker in lower_text for marker in technical_markers):
        return "Technical constraints and platform details are present but could not be fully structured."
    return None

class DocumentSummarizer:
    def __init__(self):
        self.client = StructuredGroqClient(DocumentSummary, temperature=0.15)

    async def summarize(self, text: str) -> DocumentSummary:
        excerpt = cleaned_excerpt(text, 8500)
        prompt = f"""
        Summarize this procurement document for two audiences.

        Output requirements:
        - business_summary: 80-140 words for non-technical stakeholders
        - technical_summary: 60-120 words focused on architecture, integrations, stack, and constraints
        - If technical details are absent, return technical_summary as null

        Document text:
        {excerpt}
        """

        try:
            result = await self.client.invoke(prompt)
            return result
        except Exception:
            return DocumentSummary(
                business_summary=fallback_business_summary(text),
                technical_summary=fallback_technical_summary(text),
            )

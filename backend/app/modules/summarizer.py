import os
from langchain_groq import ChatGroq
from app.schemas import DocumentSummary

class DocumentSummarizer:
    def __init__(self):
        self.llm = ChatGroq(
            model="qwen-2.5-32b", 
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.3
        )
        self.structured_llm = self.llm.with_structured_output(DocumentSummary)

    async def summarize(self, text: str) -> DocumentSummary:
        prompt = f"""
        Provide a concise business summary and a technical summary of the following document.
        The business summary should highlight the main purpose, goals, and key deliverables for non-technical teams.
        The technical summary should highlight the specific technologies, architectural constraints, and technical scope.

        Document Text (first 6000 chars):
        {text[:6000]}
        """
        
        try:
            result = await self.structured_llm.ainvoke(prompt)
            return result
        except Exception as e:
            print(f"Summarization Error: {e}")
            return DocumentSummary(business_summary="Error generating summary.", technical_summary=None)

import os
from langchain_groq import ChatGroq
from app.schemas import DocumentClassification
from langchain_core.prompts import PromptTemplate

class DocumentClassifier:
    def __init__(self):
        # We will use qwen-2.5-32b or similar via Groq
        # Note: Groq's exact model ID for Qwen might vary, usually "qwen-2.5-32b"
        self.llm = ChatGroq(
            model="qwen-2.5-32b", 
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.1
        )
        self.structured_llm = self.llm.with_structured_output(DocumentClassification)

    async def classify(self, text: str) -> DocumentClassification:
        prompt = f"""
        Analyze the following document text and classify it into one of the following categories:
        - RFP (Request for Proposal)
        - SOW (Statement of Work)
        - Contract
        - Proposal
        - General Requirement Note

        Document Text (first 2000 chars):
        {text[:2000]}
        """
        
        try:
            result = await self.structured_llm.ainvoke(prompt)
            return result
        except Exception as e:
            print(f"Classification Error: {e}")
            return DocumentClassification(document_type="Unknown", confidence=0.0)

import os
from langchain_groq import ChatGroq
from app.schemas import ExtractedEntities
from langchain_core.prompts import PromptTemplate

class EntityExtractor:
    def __init__(self):
        self.llm = ChatGroq(
            model="qwen-2.5-32b", 
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.1
        )
        self.structured_llm = self.llm.with_structured_output(ExtractedEntities)

    async def extract(self, text: str) -> ExtractedEntities:
        prompt = f"""
        Extract the following entities from the document text:
        - Client Name
        - Timeline or duration
        - Deliverables
        - Technologies or platforms mentioned
        - Stakeholders or key roles
        - Dependencies or prerequisites

        Document Text (first 5000 chars):
        {text[:5000]}
        """
        
        try:
            result = await self.structured_llm.ainvoke(prompt)
            return result
        except Exception as e:
            print(f"Extraction Error: {e}")
            return ExtractedEntities()

import os
from langchain_groq import ChatGroq
from app.schemas import RiskAssessment
from langchain_core.prompts import PromptTemplate

class RiskAnalyzer:
    def __init__(self):
        self.llm = ChatGroq(
            model="qwen-2.5-32b", 
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.2
        )
        self.structured_llm = self.llm.with_structured_output(RiskAssessment)

    async def analyze(self, text: str) -> RiskAssessment:
        prompt = f"""
        Act as a senior technical project manager. Analyze the following document text and identify potential risks.
        Look for:
        - Missing or vague acceptance criteria.
        - Unclear timelines or impossible deadlines.
        - Missing owners or stakeholders.
        - Ambiguous scope statements or technical dependencies that are undefined.

        Document Text (first 6000 chars):
        {text[:6000]}
        """
        
        try:
            result = await self.structured_llm.ainvoke(prompt)
            return result
        except Exception as e:
            print(f"Risk Analysis Error: {e}")
            return RiskAssessment(overall_risk_score="Unknown", risks=[])

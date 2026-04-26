from app.schemas import RiskAssessment, RiskFlag
from app.modules.base_llm import StructuredGroqClient, cleaned_excerpt


def normalize_risk_level(level: str) -> str:
    value = (level or "").strip().lower()
    if value == "high":
        return "High"
    if value == "medium":
        return "Medium"
    if value == "low":
        return "Low"
    return "Unknown"


def fallback_risk_level(text: str) -> str:
    lower_text = (text or "").lower()
    high_markers = ["penalty", "breach", "termination", "legal", "non-compliance", "indemnity", "security incident"]
    medium_markers = ["timeline", "dependency", "assumption", "approval", "scope change"]

    if any(marker in lower_text for marker in high_markers):
        return "High"
    if any(marker in lower_text for marker in medium_markers):
        return "Medium"
    return "Low"

class RiskAnalyzer:
    def __init__(self):
        self.client = StructuredGroqClient(RiskAssessment, temperature=0.1)

    async def analyze(self, text: str) -> RiskAssessment:
        excerpt = cleaned_excerpt(text, 8000)
        prompt = f"""
        Act as a senior delivery manager and identify procurement/project risks.

        Requirements:
        - Return up to 8 high-signal risks.
        - Each risk should include risk_level, description, and optional section.
        - Use only High, Medium, Low for risk levels.
        - If no specific risks are found, return an empty list and overall_risk_score as Low.

        Risk dimensions:
        - Missing acceptance criteria
        - Ambiguous ownership
        - Unclear dependencies
        - Unrealistic timelines
        - Security/compliance obligations that are under-specified

        Document text:
        {excerpt}
        """

        try:
            result = await self.client.invoke(prompt)
            normalized_risks = [
                RiskFlag(
                    risk_level=normalize_risk_level(risk.risk_level),
                    description=risk.description.strip(),
                    section=(risk.section.strip() if risk.section else None),
                )
                for risk in result.risks
                if risk.description and risk.description.strip()
            ]

            overall = normalize_risk_level(result.overall_risk_score)
            if overall == "Unknown":
                overall = fallback_risk_level(text)

            return RiskAssessment(risks=normalized_risks, overall_risk_score=overall)
        except Exception:
            return RiskAssessment(overall_risk_score=fallback_risk_level(text), risks=[])

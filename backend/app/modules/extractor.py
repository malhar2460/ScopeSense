from app.schemas import ExtractedEntities
from app.modules.base_llm import StructuredGroqClient, cleaned_excerpt

class EntityExtractor:
    def __init__(self):
        self.client = StructuredGroqClient(ExtractedEntities, temperature=0.05)

    async def extract(self, text: str) -> ExtractedEntities:
        excerpt = cleaned_excerpt(text, 7000)
        prompt = f"""
        Extract entities from this procurement document text.

        Output constraints:
        - Include only values that are explicitly present in the text.
        - Keep lists concise and deduplicated.
        - If uncertain, return null for fields or [] for lists.

        Extract:
        - client_name
        - timeline
        - deliverables
        - technologies
        - stakeholders
        - dependencies

        Document text:
        {excerpt}
        """

        try:
            result = await self.client.invoke(prompt)

            # Normalize list fields to remove duplicates while preserving order.
            result.deliverables = list(dict.fromkeys(result.deliverables))
            result.technologies = list(dict.fromkeys(result.technologies))
            result.stakeholders = list(dict.fromkeys(result.stakeholders))
            result.dependencies = list(dict.fromkeys(result.dependencies))

            return result
        except Exception:
            return ExtractedEntities()

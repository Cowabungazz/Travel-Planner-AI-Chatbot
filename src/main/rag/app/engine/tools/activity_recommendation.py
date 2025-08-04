from llama_index.core.tools import FunctionTool

from app.api.services.bmg.api_client import fetch_from_bmg
from app.api.services.bmg.products import get_city_uuid, get_products_with_details

# TODO: limit the number of activities retrieved and the number of response tokens
class ActivityRecommendation:

    @classmethod
    def _capitalize_words(cls, s: str) -> str:
        """ Capitalizes each word in a string """
        return " ".join(word.capitalize() for word in s.split())

    @classmethod
    async def recommend_activities(cls, country: str, city: str):
        """
        Get the list of products
        """
        country = cls._capitalize_words(country)
        city = cls._capitalize_words(city)

        data = await fetch_from_bmg("/v2/config")
        city_uuid = await get_city_uuid(data, country, city)

        if city_uuid is None:
            return "City not found"

        products_with_details = await get_products_with_details(city_uuid)
        if not products_with_details:
            return "No products available for this city"

        return {"activities": products_with_details}

def get_tools(**kwargs):
    return [FunctionTool.from_defaults(ActivityRecommendation.recommend_activities)]
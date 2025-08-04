from typing import Optional
import logging
import asyncio
from typing import List, Dict
from app.api.services.bmg.api_client import fetch_from_bmg
from app.api.routers.basket.models import Activity


logger = logging.getLogger("uvicorn")

async def get_city_uuid(data, country: str, city: str) -> Optional[str]:
    for continent in data['locations']['data']:
        for c in continent['countries']['data']:
            if c['name'] == country:
                for state in c['states']['data']:
                    for c in state['cities']['data']:
                        if c['name'] == city:
                            city_uuid = c['uuid']
                            return city_uuid
    return None


async def get_product_list(city_uuid: str) -> List[Dict]:
    """ Fetches the list of products for a given city UUID """
    products = await fetch_from_bmg("/v2/products", {"city": city_uuid})
    return products if products else []


async def get_product_details(uuid: str) -> Activity:
    """ Fetches product details given a UUID """
    data = await fetch_from_bmg(f"/v2/products/{uuid}")

    # Handle potential missing fields safely
    photos = data.get("photos", [])
    photoUrls = [f"{data.get('photosUrl', '')}{photo['paths']['original']}" for photo in photos]

    return {
        "uuid": data.get("uuid"),
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "highlights": data.get("highlights", []),
        "additionalInfo": data.get("additionalInfo", ""),
        "priceExcludes": data.get("priceExcludes", ""),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "address": data.get("address", ""),
        "minPax": data.get("minPax"),
        "maxPax": data.get("maxPax"),
        "basePrice": data.get("basePrice"),
        "currency": {
            "code": data.get("currency", {}).get("code", ""),
            "symbol": data.get("currency", {}).get("symbol", "")
        },
        "typeName": data.get("typeName", ""),
        "photoUrls": photoUrls,
        "businessHoursFrom": data.get("businessHoursFrom", ""),
        "businessHoursTo": data.get("businessHoursTo", ""),
        "averageDelivery": data.get("averageDelivery"),
        "hotelPickup": data.get("hotelPickup", False),
        "airportPickup": data.get("airportPickup", False),
    }

async def get_products_with_details(city_uuid: str) -> List[Activity]:
    """ Fetches product list and their details in parallel """
    products = await get_product_list(city_uuid)
    product_uuids = [p["uuid"] for p in products]

    # Fetch product details concurrently
    product_details = await asyncio.gather(*[get_product_details(uuid) for uuid in product_uuids])

    return product_details
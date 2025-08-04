import os
import httpx
import logging
from fastapi import HTTPException

logger = logging.getLogger("uvicorn")

BMG_BASE_URL = os.getenv("BMG_BASE_URL")
BMG_API_KEY = os.getenv("BMG_API_KEY")

async def fetch_from_bmg(endpoint: str, params=None):
    """ Generic function to fetch data from BMG API """
    if not BMG_BASE_URL or not BMG_API_KEY:
        raise HTTPException(status_code=500, detail="Server misconfiguration: Missing BMG_BASE_URL or BMG_API_KEY")

    url = f"{BMG_BASE_URL}{endpoint}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers={
                "X-Authorization": BMG_API_KEY,
                "Accept": "application/json"
            },
            params=params
        )

    if response.status_code != 200:
        logger.error(f"Failed to fetch data: {response.status_code} - {response.text}")
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")

    return response.json().get("data")

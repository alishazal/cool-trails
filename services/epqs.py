import httpx, asyncio

async def epqs(lat, lon):
    base = "https://epqs.nationalmap.gov/v1/json?"
    url = f"{base}x={lon}&y={lat}&units=m&wkid=4326"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=10)
        return r.json()["value"]

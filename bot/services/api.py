import httpx
from app.config import settings


async def upload_receipt(token: str, file_bytes: bytes, filename: str) -> dict | None:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{settings.API_URL}/receipts/upload",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": (filename, file_bytes, "image/jpeg")},
        )
        return r.json() if r.status_code == 200 else None


async def get_summary(token: str, from_date: str, to_date: str) -> dict | None:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{settings.API_URL}/analytics/summary",
            headers={"Authorization": f"Bearer {token}"},
            params={"from": from_date, "to": to_date},
        )
        return r.json() if r.status_code == 200 else None

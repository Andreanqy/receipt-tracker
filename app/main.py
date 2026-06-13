from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.receipts import router as receipts_router
from app.services.s3 import s3_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    await s3_service.init_bucket()
    yield


app = FastAPI(title="Receipt Tracker API", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(receipts_router)

@app.get("/")
def read_root():
    return {"status": "alive", "project": "receipt-tracker"}
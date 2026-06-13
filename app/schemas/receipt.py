from pydantic import BaseModel
from uuid import UUID


class ReceiptUploadResponse(BaseModel):
    id: UUID
    status: str

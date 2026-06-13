from pydantic import BaseModel, ConfigDict
from uuid import UUID
#from datetime import datetime
#from decimal import Decimal
#from typing import List, Optional

#class ItemResponse(BaseModel):
#    id: UUID
#    name: str
#    price: Decimal
#    quantity: int

#    model_config = ConfigDict(from_attributes=True)

#class ReceiptResponse(BaseModel):
#    id: UUID
#    user_id: UUID
#    total_sum: Decimal
#    created_at: datetime
#    qr_raw_data: Optional[str] = None
#    file_path: str
#    items: str[ItemResponse]

#    model_config = ConfigDict(from_attributes=True)

class ReceiptUploadResponse(BaseModel):
    id: UUID
    status: str
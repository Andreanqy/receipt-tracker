from uuid import uuid4

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.receipt import Receipt, ReceiptStatus
from app.services.s3 import s3_service
from app.schemas.receipt import ReceiptUploadResponse

router = APIRouter(prefix="/receipts", tags=["Receipts"])


@router.post("/upload", response_model=ReceiptUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_receipt(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The file must be an image",
        )

    file_extension = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
    receipt_id = uuid4()
    object_name = f"{current_user.id}/{receipt_id}.{file_extension}"

    try:
        filepath = await s3_service.upload_file(file, object_name)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file to storage",
        )

    receipt = Receipt(
        id=receipt_id,
        user_id=current_user.id,
        total_sum=0,
        filepath=filepath,
        status=ReceiptStatus.PROCESSING,
    )
    db.add(receipt)
    await db.commit()
    await db.refresh(receipt)

    return ReceiptUploadResponse(id=receipt.id, status=receipt.status.value)

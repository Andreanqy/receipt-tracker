import aioboto3
from fastapi import UploadFile
from app.config import settings

class S3Service:
    def __init__(self):
        self.session = aioboto3.Session()
        self.bucket_name = settings.MINIO_BUCKET_NAME
    
    def _endpoint_url(self) -> str:
        endpoint = settings.MINIO_ENDPOINT
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        return f"http://{endpoint}"

    async def _get_client(self):
        return self.session.client(
            "s3",
            endpoint_url=self._endpoint_url(),
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
        )
    
    async def init_bucket(self):
        async with await self._get_client() as client:
            try:
                await client.head_bucket(Bucket=self.bucket_name)
            except Exception:
                await client.create_bucket(Bucket=self.bucket_name)
    
    async def download_file(self, object_name: str) -> bytes:
        async with await self._get_client() as client:
            response = await client.get_object(Bucket=self.bucket_name, Key=object_name)
            async with response["Body"] as stream:
                return await stream.read()

    async def upload_file(self, file: UploadFile, object_name: str) -> str:
        async with await self._get_client() as client:
            filecontent = await file.read()
            await client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=filecontent,
                ContentType=file.content_type
            )
            return f"{self.bucket_name}/{object_name}"

s3_service = S3Service()
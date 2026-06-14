import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException
from app.config import settings

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


async def save_file(file: UploadFile, folder: str = "avatars") -> str:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, "Faqat jpg, png, webp")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(413, f"Max {settings.MAX_UPLOAD_SIZE_MB}MB")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTS:
        ext = ".jpg"

    filename = f"{folder}/{uuid.uuid4().hex}{ext}"

    if settings.USE_SPACES:
        return await _upload_to_spaces(content, filename, file.content_type)
    else:
        return await _save_local(content, filename)


async def _save_local(content: bytes, filename: str) -> str:
    path = os.path.join(settings.MEDIA_ROOT, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    async with aiofiles.open(path, "wb") as f:
        await f.write(content)
    return f"/media/{filename}"


async def _upload_to_spaces(content: bytes, key: str, content_type: str) -> str:
    import boto3
    from botocore.config import Config

    s3 = boto3.client(
        "s3",
        region_name=settings.DO_SPACES_REGION,
        endpoint_url=settings.DO_SPACES_ENDPOINT,
        aws_access_key_id=settings.DO_SPACES_KEY,
        aws_secret_access_key=settings.DO_SPACES_SECRET,
        config=Config(signature_version="s3v4"),
    )
    s3.put_object(
        Bucket=settings.DO_SPACES_BUCKET,
        Key=key,
        Body=content,
        ContentType=content_type,
        ACL="public-read",
    )
    return f"{settings.DO_SPACES_ENDPOINT}/{settings.DO_SPACES_BUCKET}/{key}"


async def delete_file(path: str):
    if settings.USE_SPACES:
        pass  # TODO: implement S3 delete for prod
    else:
        rel = path.replace("/media/", "", 1)
        full = os.path.join(settings.MEDIA_ROOT, rel)
        if os.path.exists(full):
            os.remove(full)

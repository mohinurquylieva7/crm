from fastapi import APIRouter, Depends, UploadFile, File
from app.models.user import User
from app.services.upload_service import save_file
from app.dependencies import get_current_active_user

router = APIRouter(tags=["uploads"])


@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = "misc",
    _: User = Depends(get_current_active_user),
):
    url = await save_file(file, folder)
    return {"url": url, "filename": file.filename}

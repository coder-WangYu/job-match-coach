from io import BytesIO
from uuid import uuid4
from fastapi import APIRouter, File, UploadFile
from pypdf import PdfReader
from job_match_coach.core.store import RESUME_STORE

router = APIRouter()

# 上传简历
@router.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    content = await file.read()
    reader = PdfReader(BytesIO(content))
    parts = []

    for page in reader.pages:
        parts.append(page.extract_text() or "")

    text = "\n".join(parts).strip()

    # 创建resume_id
    resume_id = str(uuid4())
    RESUME_STORE[resume_id] = text

    return {
        "resume_id": resume_id,
        "filename": file.filename, 
        "size": len(content)
    }

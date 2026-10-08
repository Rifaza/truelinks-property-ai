from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.agents.photo_issue_agent import PhotoIssueAgent
from app.schemas.photo_issue import PhotoIssueResult


router = APIRouter(
    prefix="/api/photos",
    tags=["Photos"],
)


@router.post(
    "/analyze",
    response_model=PhotoIssueResult,
)
async def analyze_photo(
    file: UploadFile = File(...),
    affected_unit: str = Form(...),
) -> PhotoIssueResult:
    """
    Analyze a property photo and generate a draft work order.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Photo file must have a filename.",
        )

    allowed_content_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPEG, PNG, and WebP images are supported."
            ),
        )

    if not affected_unit.strip():
        raise HTTPException(
            status_code=400,
            detail="Affected unit must be provided.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Photo file is empty.",
        )

    suffix = Path(file.filename).suffix or ".jpg"

    temporary_path = None

    try:
        with NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temporary_file:
            temporary_file.write(content)
            temporary_path = temporary_file.name

        result = PhotoIssueAgent().analyze(
            image_path=temporary_path,
            affected_unit=affected_unit.strip(),
        )

        return result

    finally:
        if temporary_path:
            temporary_file_path = Path(temporary_path)

            if temporary_file_path.exists():
                temporary_file_path.unlink()
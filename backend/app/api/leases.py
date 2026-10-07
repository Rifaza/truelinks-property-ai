from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.db.database import SessionLocal
from app.models import Lease
from app.schemas.rule_evaluation import (
    LeaseEvaluationResponse,
    RuleEvidenceResponse,
    RuleResultResponse,
)
from app.services.rule_evaluation_service import RuleEvaluationService

router = APIRouter(
    prefix="/api/leases",
    tags=["Leases"],
)

UPLOAD_DIR = Path("uploads/leases")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_lease(file: UploadFile = File(...)):
    """
    Uploads and stores the original lease document.

    The original document is preserved because later extraction results
    and evidence records must be traceable back to the source document.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Lease file must have a filename.",
        )

    # The assessment currently expects lease documents such as PDFs.
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF lease documents are supported.",
        )

    # Prevent directory traversal by keeping only the filename.
    safe_filename = Path(file.filename).name

    destination = UPLOAD_DIR / safe_filename

    content = await file.read()
    destination.write_bytes(content)

    return {
        "message": "Lease uploaded successfully.",
        "filename": safe_filename,
        "path": str(destination),
    }


@router.post(
    "/{lease_id}/evaluate",
    response_model=LeaseEvaluationResponse,
)
def evaluate_lease(
    lease_id: int,
) -> LeaseEvaluationResponse:
    db = SessionLocal()

    try:
        lease = db.get(Lease, lease_id)

        if lease is None:
            raise HTTPException(
                status_code=404,
                detail=f"Lease with id {lease_id} not found.",
            )

    finally:
        db.close()

    results = RuleEvaluationService().evaluate_and_persist(
        lease
    )

    return LeaseEvaluationResponse(
        lease_id=lease_id,
        rules=[
            RuleResultResponse(
                rule_id=result.rule_id,
                status=result.status,
                explanation=result.explanation or "",
                evidence=[
                    RuleEvidenceResponse(
                        field_name=evidence.field_name,
                        source_reference=evidence.source_reference,
                        source_text=evidence.source_text,
                        confidence=evidence.confidence,
                    )
                    for evidence in result.evidence
                ],
            )
            for result in results
        ],
    )
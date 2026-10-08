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

from app.agents.lease_extraction_agent import LeaseExtractionAgent
from app.services.lease_service import LeaseService
from app.services.unit_matcher import UnitMatcher
from app.models import Unit

router = APIRouter(
    prefix="/api/leases",
    tags=["Leases"],
)

UPLOAD_DIR = Path("uploads/leases")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)



@router.post("/upload")
async def upload_lease(file: UploadFile = File(...)):
    """Demo workflow: upload, extract, match, persist, and evaluate."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Lease file must have a filename.",
        )

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF lease documents are supported.",
        )

    safe_filename = Path(file.filename).name
    if not safe_filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded filename must end in .pdf.",
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF is empty.",
        )

    destination = UPLOAD_DIR / safe_filename
    destination.write_bytes(content)

    # DEMO ONLY: this agent returns fixed fixture data.
    # It does not extract facts from the PDF contents.
    extraction = LeaseExtractionAgent().extract(
        safe_filename
    )

    if not extraction.unit_number:
        raise HTTPException(
            status_code=422,
            detail="No unit number was extracted.",
        )

    # Match against the owner's database records.
    db = SessionLocal()
    try:
        unit = UnitMatcher().find_unit(
            db,
            extraction.unit_number,
        )

        if unit is None:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Unknown unit: {extraction.unit_number}"
                ),
            )

        if unit.status.lower() != "available":
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Unit {unit.unit_number} is not available."
                ),
            )

        unit_id = unit.id
    finally:
        db.close()

    # Persist the lease and source evidence through the service.
    lease = LeaseService().create_lease_from_extraction(
        extraction=extraction,
        source_filename=safe_filename,
        unit_id=unit_id,
    )

    # Evaluate while the unit is still marked available,
    # so R7 checks the pre-linking state.
    results = RuleEvaluationService().evaluate_and_persist(
        lease
    )

    r7 = next(
        (result for result in results if result.rule_id == "R7"),
        None,
    )

    # Only update occupancy if R7 passes.
    if r7 and r7.status == "PASS":
        db = SessionLocal()
        try:
            unit = db.get(Unit, unit_id)
            if unit is not None:
                unit.status = "occupied"
                db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    return {
        "message": "Lease uploaded, extracted, matched, and evaluated successfully.",
        "lease_id": lease.id,
        "filename": safe_filename,
        "unit_number": extraction.unit_number,
        "extraction_mode": "DEMO_STUB_FIXED_SAMPLE_DATA",
        "human_review_required": True,
        "occupancy_updated": bool(
            r7 and r7.status == "PASS"
        ),
        "rules": [
            {
                "rule_id": result.rule_id,
                "status": result.status,
                "explanation": result.explanation,
            }
            for result in results
        ],
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
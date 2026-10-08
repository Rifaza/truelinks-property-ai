from fastapi import APIRouter, Depends, HTTPException

from app.db.database import SessionLocal
from app.models.property_issue import PropertyIssue
from app.models.unit import Unit
from app.schemas.photo_issue import PhotoIssueResult
from app.services.photo_issue_service import PhotoIssueService


router = APIRouter(
    prefix="/api/property-issues",
    tags=["Property Issues"],
)


@router.post(
    "/{unit_id}",
    response_model=PhotoIssueResult,
)
def create_property_issue(
    unit_id: int,
    result: PhotoIssueResult,
):
    db = SessionLocal()

    try:
        unit = db.get(Unit, unit_id)

        if unit is None:
            raise HTTPException(
                status_code=404,
                detail=f"Unit with id {unit_id} not found.",
            )

        issue = PhotoIssueService().create_issue_and_work_order(
            db=db,
            unit_id=unit_id,
            result=result,
        )

        return PhotoIssueResult(
            issue=issue.issue,
            description=issue.description,
            severity=issue.severity,
            condition=issue.condition,
            visible_items=(
                issue.visible_items.split(", ")
                if issue.visible_items
                else []
            ),
            work_order=result.work_order,
        )

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
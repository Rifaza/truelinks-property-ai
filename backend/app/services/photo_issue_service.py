from sqlalchemy.orm import Session

from app.models.property_issue import PropertyIssue
from app.models.work_order import WorkOrder
from app.schemas.photo_issue import PhotoIssueResult


class PhotoIssueService:

    def create_issue_and_work_order(
        self,
        db: Session,
        unit_id: int,
        result: PhotoIssueResult,
    ) -> PropertyIssue:

        issue = PropertyIssue(
            unit_id=unit_id,
            issue=result.issue,
            description=result.description,
            severity=result.severity,
            condition=result.condition,
            visible_items=", ".join(result.visible_items),
            status="OPEN",
        )

        db.add(issue)
        db.flush()

        work_order = WorkOrder(
            issue_id=issue.id,
            title=result.work_order.title,
            description=result.work_order.description,
            affected_unit=result.work_order.affected_unit,
            recommended_action=result.work_order.recommended_action,
            status="DRAFT",
        )

        db.add(work_order)
        db.commit()

        db.refresh(issue)

        return issue
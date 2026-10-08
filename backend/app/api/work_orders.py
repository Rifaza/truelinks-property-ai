
from fastapi import APIRouter, HTTPException

from app.db.database import SessionLocal
from app.models.work_order import WorkOrder


router = APIRouter(
    prefix="/api/work-orders",
    tags=["Work Orders"],
)


@router.patch("/{work_order_id}/accept")
def accept_work_order(work_order_id: int):
    db = SessionLocal()

    try:
        work_order = db.get(WorkOrder, work_order_id)

        if work_order is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Work order with id {work_order_id} not found."
                ),
            )

        work_order.status = "ACCEPTED"

        db.commit()
        db.refresh(work_order)

        return {
            "id": work_order.id,
            "status": work_order.status,
        }

    finally:
        db.close()


@router.patch("/{work_order_id}/reject")
def reject_work_order(work_order_id: int):
    db = SessionLocal()

    try:
        work_order = db.get(WorkOrder, work_order_id)

        if work_order is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Work order with id {work_order_id} not found."
                ),
            )

        work_order.status = "REJECTED"

        db.commit()
        db.refresh(work_order)

        return {
            "id": work_order.id,
            "status": work_order.status,
        }

    finally:
        db.close()
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app

from app.api.leases import evaluate_lease
from app.db.database import SessionLocal
from app.models import Lease


def test_evaluate_lease_returns_seven_rules():
    db = SessionLocal()

    try:
        lease = db.query(Lease).first()
        assert lease is not None

        lease_id = lease.id

    finally:
        db.close()

    response = evaluate_lease(lease_id)

    assert response.lease_id == lease_id
    assert len(response.rules) == 7

    assert [rule.rule_id for rule in response.rules] == [
        "R1",
        "R2",
        "R3",
        "R4",
        "R5",
        "R6",
        "R7",
    ]

    r1 = next(
        rule
        for rule in response.rules
        if rule.rule_id == "R1"
    )

    assert r1.status.value == "PASS"
    assert len(r1.evidence) > 0


def test_evaluate_unknown_lease_returns_404():
    with pytest.raises(HTTPException) as exc_info:
        evaluate_lease(999999)

    assert exc_info.value.status_code == 404


def test_evaluate_lease_http_endpoint():
    db = SessionLocal()

    try:
        lease = db.query(Lease).first()
        assert lease is not None
        lease_id = lease.id
    finally:
        db.close()

    client = TestClient(app)

    response = client.post(
        f"/api/leases/{lease_id}/evaluate"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["lease_id"] == lease_id
    assert len(data["rules"]) == 7

    rule_ids = [
        rule["rule_id"]
        for rule in data["rules"]
    ]

    assert rule_ids == [
        "R1",
        "R2",
        "R3",
        "R4",
        "R5",
        "R6",
        "R7",
    ]

    r1 = next(
        rule
        for rule in data["rules"]
        if rule["rule_id"] == "R1"
    )

    assert r1["status"] == "PASS"
    assert len(r1["evidence"]) > 0
# TrueLinks Property AI

A full-stack AI-assisted property management service built as part of the TrueLinks.AI SDE-Platform & Products technical exercise.

The application demonstrates two linked AI-assisted workflows for a property owner:

1. Lease document extraction and owner-rule validation.
2. Property photo analysis and draft work-order generation.

The two workflows are connected through the property unit, allowing an owner to view lease information and maintenance issues together.

---

## Architecture

```text
                         TrueLinks Property AI
                                  |
                    +-------------+-------------+
                    |                           |
                React UI                   FastAPI API
                    |                           |
                    |             +-------------+-------------+
                    |             |                           |
                    |       Lease Workflow              Photo Workflow
                    |             |                           |
                    |       Lease Extraction             Photo Issue Agent
                    |             |                           |
                    |       Evidence Store               VisionModel
                    |             |                           |
                    |       R1-R7 Rules              StubVisionModel
                    |             |                           |
                    +-------------+-------------+
                                  |
                             Unit / Property
                                  |
                    +-------------+-------------+
                    |                           |
                  Lease                   Property Issues
                                                |
                                           Work Orders



Key Features
Lease workflow
- Extract structured lease information.
- Extract supporting source evidence for lease fields.
- Store evidence references and source text.
- Validate leases against the owner's R1-R7 rules.
- Return PASS, FAIL, or NOT_DETERMINABLE.
- Match leases to known property units.
- Validate unit availability before accepting a new lease.
Property photo workflow
- Upload property photos.
- Analyze the photo through a vision-model abstraction.
- Identify:
  - Property condition
  - Visible equipment/items
  - Reported issue
  - Severity
- Generate a draft work order.
- Associate the issue with a property unit.
Human-in-the-loop
AI output is treated as a proposal rather than an automatic final decision.
The owner can review a generated work order before it is persisted and can subsequently accept or reject the work order.
Tech Stack
Frontend
- React
- TypeScript
- Vite
Backend
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Pytest
Database
- PostgreSQL
AI Architecture
The photo-analysis workflow uses a model abstraction:
VisionModel
     |
     +-- StubVisionModel
     |
     +-- Production vision provider (future)

This keeps the application independent of a specific AI provider.
Backend Structure
backend/
├── app/
│   ├── agents/
│   │   ├── lease_extraction_agent.py
│   │   ├── photo_issue_agent.py
│   │   ├── vision_model.py
│   │   └── stub_vision_model.py
│   │
│   ├── api/
│   │   ├── leases.py
│   │   ├── photos.py
│   │   ├── property_issues.py
│   │   ├── units.py
│   │   └── work_orders.py
│   │
│   ├── models/
│   │   ├── unit.py
│   │   ├── lease.py
│   │   ├── evidence.py
│   │   ├── rule_result.py
│   │   ├── property_issue.py
│   │   └── work_order.py
│   │
│   ├── schemas/
│   │   └── ...
│   │
│   ├── services/
│   │   ├── lease_service.py
│   │   ├── rule_evaluation_service.py
│   │   └── photo_issue_service.py
│   │
│   └── db/
│       └── ...
│
└── tests/
    └── ...

Core Data Relationship
The property unit is the shared business entity connecting both workflows.
Unit
 |
 +-- Lease
 |     |
 |     +-- Evidence
 |     |
 |     +-- Rule Results
 |
 +-- Property Issue
       |
       +-- Work Order

This allows the owner to open a unit and see its lease and maintenance issues together.
Owner Rules
The implementation supports the provided R1-R7 owner rules:
Rule	Description
R1	Security deposit must be at least one month's rent
R2	Lease must contain a defined rent escalation clause
R3	Fixed term must not exceed 36 months without approval
R4	Commencement, expiry and stated term must agree
R5	Both landlord and tenant must be identified and signed
R6	Annual rent must equal monthly rent × 12
R7	Unit must exist and be available before linking a new lease


Each rule produces:
- PASS
- FAIL
- NOT_DETERMINABLE
with an explanation and supporting evidence where applicable.
Photo Analysis Design
The assessment allows a vision model to be stubbed because an external AI API key is not required.
The implementation therefore uses:
PhotoIssueAgent
       |
       v
VisionModel
       |
       v
StubVisionModel

The StubVisionModel produces deterministic structured output for development and testing.
A production vision provider can later implement the same VisionModel interface without requiring changes to the higher-level photo issue workflow.
Sample Photos
The assessment brief referenced sample property photos, but sample photos were not provided with the materials available during implementation.
A local test fixture and deterministic vision stub were therefore used to validate the API and application architecture.
The application does not claim that the stub performs real computer-vision analysis.
Human Review
The intended workflow is:
AI analysis
    |
    v
Draft result
    |
    v
Human review
    |
    +---- Reject
    |
    +---- Accept
             |
             v
       Persist issue
             |
             v
       Draft work order
             |
             v
       Accept / Reject

This prevents AI-generated maintenance actions from becoming final actions without human review.
API Endpoints
Health
GET /health

Lease
POST /api/leases/upload
POST /api/leases/{lease_id}/evaluate

Photos
POST /api/photos/analyze

Property Issues
POST /api/property-issues/{unit_id}

Units
GET /api/units/{unit_id}

Work Orders
PATCH /api/work-orders/{work_order_id}/accept
PATCH /api/work-orders/{work_order_id}/reject

Interactive API documentation is available through FastAPI Swagger.
Running the Backend
From the project root:
cd backend

Create and activate the virtual environment:
Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1

Install dependencies:
pip install -r requirements.txt

Initialize missing database tables:
python -m app.db.init_db

Start the API:
uvicorn app.main:app --reload

Swagger:
http://127.0.0.1:8000/docs

Running Tests
From the backend directory:
python -m pytest -q

The backend currently includes tests covering:
- Lease extraction
- Evidence persistence
- Rule evaluation
- Lease evaluation API
- Photo issue agent
- Photo analysis API
- Photo persistence
- Unit overview API
- Work-order workflow
Running the Frontend
From the project root:
cd frontend
npm install
npm run dev

The frontend communicates with the local FastAPI backend at:
http://127.0.0.1:8000

Product Decisions
Why the unit is the central entity
The unit is the natural connection point between leasing and property maintenance.
Instead of treating lease analysis and photo analysis as unrelated AI features, both outputs are associated with a unit.
This gives the owner a single place to understand:
- Who occupies the unit
- What the lease says
- Whether the lease passes owner rules
- What maintenance issues have been reported
- What work orders are currently pending
Why AI output is not automatically trusted
AI-generated information can be incomplete or incorrect.
The application therefore treats AI output as a proposal and keeps human review in the workflow.
Why the vision model is abstracted
AI providers and models can change independently of the application.
Using a VisionModel interface allows the application to switch providers without changing the business workflow.
Current Scope / Omissions
To keep the assessment focused, the following were intentionally omitted:
- Authentication and authorization
- Multi-tenant access control
- Production AI provider integration
- Background job processing
- Email/SMS notifications
- Advanced property dashboards
- Maintenance contractor management
- Production object storage
- Full audit history for every human decision
- Automated lease-field correction workflow
These would be appropriate follow-up work for a production system.
Scaling Considerations
The current implementation uses synchronous API calls and is appropriate for a small assessment.
At larger scale, the main pressure points would be AI inference, document/image processing, file storage, and database growth.
A production implementation could:
1. Store uploaded documents/images in object storage.
2. Process AI workloads asynchronously through a queue.
3. Add retry and idempotency handling.
4. Add database indexes and pagination.
5. Add caching for frequently accessed unit data.
6. Add observability around AI latency, failures and confidence.
7. Track human corrections to measure AI accuracy.
Potential Product Enhancements
Future improvements could include:
- Lease expiry notifications
- Maintenance SLA tracking
- Automatic contractor assignment
- High-severity issue alerts
- Photo history per unit
- Lease/document versioning
- Confidence-based human review
- Search across all properties
- Maintenance cost tracking
- AI-generated maintenance summaries
- Dashboard showing property health
- Audit trail for owner decisions

First 30 Days at TrueLinks
My first 30 days would focus on understanding the existing product and improving reliability before adding significant new functionality.
Week 1
- Understand the existing architecture and domain model.
- Run the current workflows end-to-end.
- Identify reliability and observability gaps.
Week 2
- Improve AI-assisted workflow reliability.
- Review extraction accuracy and failure cases.
- Add useful automated tests around critical workflows.
Week 3
- Integrate production document/vision models behind stable interfaces.
- Measure confidence and human correction rates.
- Improve the owner review experience.
Week 4
- Prioritize product improvements based on actual user feedback.
- Improve performance, observability and operational readiness.

Assessment Status
The implementation demonstrates:
- Structured lease extraction
- Evidence-backed outputs
- Deterministic owner-rule evaluation
- Property/unit matching
- Vision-model abstraction
- Photo issue detection workflow
- Draft work-order generation
- Database persistence
- Unit-centric aggregation
- Human-in-the-loop review
- Automated backend testing
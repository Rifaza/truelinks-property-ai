from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.leases import router as leases_router
from app.api.photos import router as photos_router
from app.api.property_issues import router as property_issues_router
from app.api.units import router as units_router
from app.api.work_orders import router as work_orders_router

app = FastAPI(
    title="TrueLinks Property AI",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leases_router)
app.include_router(photos_router)
app.include_router(property_issues_router)
app.include_router(units_router)
app.include_router(work_orders_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
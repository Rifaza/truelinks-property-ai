from fastapi import FastAPI

from app.api.leases import router as leases_router


app = FastAPI(
    title="TrueLinks Property AI",
    version="0.1.0",
)


app.include_router(leases_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
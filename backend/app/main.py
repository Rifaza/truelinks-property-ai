from fastapi import FastAPI

app = FastAPI(
    title="TrueLinks Property AI",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
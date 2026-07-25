from fastapi import FastAPI

from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)


@app.get("/")
def root():
    return {
        "message": "TraffiSense AI Backend Running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
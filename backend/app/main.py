from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

# CORS Configuration
origins = [
    "http://localhost:5173",  # React (Vite)
    "http://localhost:3000",  # React (CRA)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
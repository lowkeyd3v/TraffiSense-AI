from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
import app.models

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
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
    return {"message": "TraffiSense AI Backend Running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
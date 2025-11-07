from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import engine, Base
from .api import router as api_router

# migrate tables at startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Amazon Scraper API", version="1.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False, 
)

# simple health in main
@app.get("/health")
def health():
    return {"status": "ok"}

# mount API router
app.include_router(api_router)

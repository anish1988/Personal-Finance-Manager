import sys
from pathlib import Path

# ensure project root (parent of src) is on sys.path so "backend" imports work
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import auth
from src.api.routes import transactions


app = FastAPI(
    title="Personal Finance Manager",
    description="API for personal income & expenses",
    version="1.0.0"
)

# Optional: Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes
app.include_router(auth.router)
app.include_router(transactions.router)

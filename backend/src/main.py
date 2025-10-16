from fastapi import FastAPI
from src.api.routes import auth  # your auth routes
from fastapi.middleware.cors import CORSMiddleware

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

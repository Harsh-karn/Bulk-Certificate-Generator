from fastapi import FastAPI
from app.core.database import engine, Base
from app.api.routers import jobs

# Create the database tables if they do not exist
Base.metadata.create_all(bind=engine)

# Initialize the FastAPI application
app = FastAPI(
    title="Bulk Certificate Generator API",
    description="Backend API for generating bulk PDF certificates.",
    version="1.0.0"
)

# Include API routers from the api/routers package
app.include_router(jobs.router)

@app.get("/")
def read_root():
    """Health check and welcome endpoint."""
    return {"message": "Welcome to Bulk Certificate Generator API"}

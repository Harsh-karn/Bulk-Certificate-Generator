from fastapi import FastAPI
from app.database import engine, Base
from app.routers import jobs

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bulk Certificate Generator API")

app.include_router(jobs.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Bulk Certificate Generator API"}

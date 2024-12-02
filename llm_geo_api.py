from fastapi import FastAPI, HTTPException, File, UploadFile, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, Integer, String, create_engine, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import json

# Import LLM-Geo module (adjust path as needed)
from LLM_Geo_kernel import process_task

# --- CONFIGURATION ---
API_KEY = os.getenv("API_KEY", "your-secure-api-key")  # Replace with env variable
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

DATABASE_URL = "sqlite:///llm_geo.db"

# --- DATABASE SETUP ---
Base = declarative_base()

class GeoQueryHistory(Base):
    __tablename__ = "geo_query_history"
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, nullable=False)
    result = Column(JSON, nullable=False)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# --- FASTAPI SETUP ---
app = FastAPI(
    title="LLM-Geo API",
    description="An API for geospatial analysis using LLM-Geo.",
    version="1.0.0"
)

# --- MODELS ---
class GeoQuery(BaseModel):
    query: str
    task_name: Optional[str] = "default_task"

# --- UTILITY FUNCTIONS ---
def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

def save_query_to_db(query: str, result: dict):
    db = SessionLocal()
    db_entry = GeoQueryHistory(query=query, result=result)
    db.add(db_entry)
    db.commit()
    db.close()

# --- API ENDPOINTS ---
@app.get("/health", tags=["System"])
async def health_check():
    """
    Simple endpoint to check if the API is running.
    """
    return {"status": "Healthy"}

@app.post("/geospatial", tags=["Geospatial Analysis"])
async def analyze_geospatial_query(query: GeoQuery, api_key: str = Depends(verify_api_key)):
    """
    Accepts a geospatial query and processes it using LLM-Geo.
    """
    if not query.query:
        raise HTTPException(status_code=400, detail="Query text cannot be empty.")
    
    try:
        # Directly call LLM-Geo's processing function
        result = process_task(query.query, task_name=query.task_name)

        # Save to history
        save_query_to_db(query.query, result)

        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload", tags=["File Upload"])
async def upload_file(file: UploadFile = File(...)):
    """
    Accepts a geospatial file (e.g., GeoJSON, shapefile) for processing.
    """
    try:
        file_content = await file.read()
        # Process file content (e.g., parse GeoJSON)
        return {"filename": file.filename, "message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")

@app.get("/history", tags=["Query History"])
def get_query_history(api_key: str = Depends(verify_api_key)):
    """
    Retrieves historical geospatial queries and results.
    """
    db = SessionLocal()
    queries = db.query(GeoQueryHistory).all()
    db.close()
    return [{"id": q.id, "query": q.query, "result": q.result} for q in queries]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

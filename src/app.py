"""
FastAPI Object Detection Service
Endpoint: POST /predict (multipart image upload)
Health:   GET /health
Metrics:  GET /metrics (monitoring report path)
"""
import os
import time
import uuid
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any

from src.model import detector
from src.monitor import monitor
from src.logger import setup_logging

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)

# Configuration
MODEL_VERSION = detector.MODEL_VERSION
SERVICE_VERSION = "1.0.0"
MAX_IMAGE_SIZE_MB = 10

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: load model. Shutdown: cleanup."""
    logger.info("Starting service v%s with model %s", SERVICE_VERSION, MODEL_VERSION)
    success = detector.load()
    if not success:
        logger.error("Model failed to load. Service will report unhealthy.")
    else:
        logger.info("Service ready.")
    yield
    logger.info("Shutting down service.")

app = FastAPI(
    title="Object Detection API",
    description="Object detection API for operational capstone assessment.",
    version=SERVICE_VERSION,
    lifespan=lifespan
)

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str
    service_version: str

class PredictionResponse(BaseModel):
    request_id: str
    model_version: str
    image_size: List[int]
    detections: List[Dict[str, Any]]
    detection_count: int
    inference_time_ms: float

@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Readiness probe. Returns 503 if model not loaded."""
    is_ready = detector.is_ready()
    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    response = HealthResponse(
        status="healthy" if is_ready else "unhealthy",
        model_loaded=is_ready,
        model_version=MODEL_VERSION,
        service_version=SERVICE_VERSION
    )
    return JSONResponse(content=response.model_dump(), status_code=status_code)

@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)) -> PredictionResponse:
    """Run object detection on uploaded image."""
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    # Validate input
    if not file.content_type or not file.content_type.startswith("image/"):
        monitor.record_request(
            request_id=request_id,
            latency_ms=(time.time() - start_time) * 1000,
            detection_count=0,
            confidences=[],
            image_size=(0, 0),
            status="failure",
            error="Invalid content type"
        )
        logger.error("Invalid content type: %s", file.content_type, extra={
            "request_id": request_id,
            "status": "failure",
            "error_type": "validation_error"
        })
        raise HTTPException(status_code=400, detail="File must be an image (image/*)")
    
    try:
        contents = await file.read()
        
        # Size check
        size_mb = len(contents) / (1024 * 1024)
        if size_mb > MAX_IMAGE_SIZE_MB:
            monitor.record_request(
                request_id=request_id,
                latency_ms=(time.time() - start_time) * 1000,
                detection_count=0,
                confidences=[],
                image_size=(0, 0),
                status="failure",
                error="Image too large"
            )
            raise HTTPException(status_code=413, detail="Image exceeds %dMB limit" % MAX_IMAGE_SIZE_MB)
        
        # Run inference
        result = detector.predict(contents)
        latency_ms = (time.time() - start_time) * 1000
        
        # Record metrics
        confidences = [d["confidence"] for d in result["detections"]]
        monitor.record_request(
            request_id=request_id,
            latency_ms=latency_ms,
            detection_count=result["detection_count"],
            confidences=confidences,
            image_size=result["image_size"],
            status="success"
        )
        
        # Structured log
        logger.info("Prediction completed: %d detections in %.2fms", result["detection_count"], latency_ms, extra={
            "request_id": request_id,
            "model_version": MODEL_VERSION,
            "latency_ms": round(latency_ms, 2),
            "input_count": 1,
            "status": "success"
        })
        
        return PredictionResponse(
            request_id=request_id,
            model_version=result["model_version"],
            image_size=list(result["image_size"]),
            detections=result["detections"],
            detection_count=result["detection_count"],
            inference_time_ms=round(latency_ms, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        monitor.record_request(
            request_id=request_id,
            latency_ms=latency_ms,
            detection_count=0,
            confidences=[],
            image_size=(0, 0),
            status="failure",
            error=str(e)
        )
        logger.error("Inference error: %s", str(e), extra={
            "request_id": request_id,
            "model_version": MODEL_VERSION,
            "latency_ms": round(latency_ms, 2),
            "status": "failure",
            "error_type": type(e).__name__
        })
        raise HTTPException(status_code=500, detail="Inference failed: %s" % str(e))

@app.get("/metrics")
async def metrics() -> Dict[str, Any]:
    """Return monitoring report file path and basic stats."""
    report_path = monitor.generate_report()
    return {
        "report_path": report_path,
        "total_requests": len(monitor.requests),
        "report_generated": True
    }

@app.get("/monitoring-report", response_class=HTMLResponse)
async def monitoring_report() -> str:
    """Serve the HTML monitoring report directly."""
    report_path = monitor.generate_report()
    with open(report_path, "r") as f:
        return f.read()

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
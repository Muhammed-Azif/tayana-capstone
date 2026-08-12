# Operator Runbook: Object Detection API

**Owner:** Capstone Candidate  
**Reviewer:** Any engineer with Docker experience  
**Last Updated:** 2026-08-12

---

## 1. Setup Steps

### 1.1 Clone Repository
```bash
git clone <repository-url>
cd tayana-capstone-object-detection
```

### 1.2 Verify Prerequisites
- Docker Engine 24.0+ OR Podman 4.0+
- 4GB free RAM (model loads into memory)
- 2GB free disk space (for image layers + model cache)
- Internet access (first run downloads ~150MB model weights)

### 1.3 Build Container
```bash
docker build -t object-detection-api:latest .
```
Expected output: `Successfully tagged object-detection-api:latest`

---

## 2. Test Steps

### 2.1 Run Automated Tests
```bash
docker run --rm object-detection-api:latest pytest tests/ -v
```
Expected: All tests pass or skip (model load may skip in CI without cache).

### 2.2 Start Service and Health Check
```bash
docker run -d -p 8000:8000 --name od-api object-detection-api:latest
sleep 45  # Wait for model download and load
curl http://localhost:8000/health
```
Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "fasterrcnn_resnet50_fpn_v2_torchvision_0.17",
  "service_version": "1.0.0"
}
```

### 2.3 Sample Prediction
```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@sample_inputs/sample_street.jpg"
```
Expected: JSON with `detections` array, `request_id`, `inference_time_ms`.

---

## 3. Deploy / Run Steps

### 3.1 Local Docker
```bash
docker run -d \
  -p 8000:8000 \
  --name od-api \
  --restart unless-stopped \
  object-detection-api:latest
```

### 3.2 GitHub Codespaces
```bash
pip install -r requirements.txt
uvicorn src.app:app --host 0.0.0.0 --port 8000
```
Forward port 8000 in Codespaces panel.

### 3.3 Verify Deployment
```bash
curl -f http://localhost:8000/health || echo "DEPLOYMENT FAILED"
```

---

## 4. Health Check Steps

```bash
# Basic health
curl http://localhost:8000/health

# Check container status
docker ps -a | grep od-api
docker logs od-api --tail 50

# If unhealthy:
# 1. Check logs for model load errors
# 2. Verify port 8000 is not in use: lsof -i :8000
# 3. Restart container: docker restart od-api
```

---

## 5. Monitoring Report Generation

```bash
# Trigger report generation via API
curl http://localhost:8000/metrics

# View report in browser
open http://localhost:8000/monitoring-report

# Or copy from container
docker cp od-api:/app/monitoring/monitoring_report.html ./
```

Report includes:
- Latency distribution & drift vs baseline
- Detections per image
- Confidence distribution & drift
- Success rate threshold check
- Recent request table

---

## 6. Common Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Connection refused` | Container not ready | Wait 45s for model load |
| `503 Service Unavailable` | Model failed to load | Check disk space, restart container |
| `400 Bad Request` | Invalid file type | Ensure file is JPEG/PNG |
| `413 Payload Too Large` | Image > 10MB | Resize image before upload |
| `500 Internal Server Error` | Inference failure | Check logs, verify image is valid |
| Slow inference (>10s) | CPU bottleneck / large image | Resize to <1000px, or use GPU |
| Empty detections | No objects above 0.5 threshold | Normal behavior; lower threshold if needed |

---

## 7. Rollback Steps

See `rollback_plan.md` for full details.

Quick command:
```bash
docker stop od-api
docker rm od-api
docker run -d -p 8000:8000 --name od-api object-detection-api:<PREVIOUS_TAG>
```

---

## 8. Cleanup Steps

```bash
# Stop and remove container
docker stop od-api
docker rm od-api

# Remove image
docker rmi object-detection-api:latest

# Remove model cache (frees ~150MB)
rm -rf ~/.cache/torch/hub/

# Clean local artifacts
rm -f monitoring/*.html monitoring/*.png logs/*.jsonl
```

---

## 9. Owner / Reviewer Assumptions

- Operator has basic Docker knowledge.
- Operator understands that this is a **pilot system**, not production-ready.
- Operator will not submit sensitive/personal images.
- Operator has access to the Git repository for source code inspection.
- If model weights need to be re-downloaded, internet access is required.

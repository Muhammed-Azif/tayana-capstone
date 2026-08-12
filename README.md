<<<<<<< HEAD
# Object Detection Service - Capstone Deployment

**Source Topic:** Topic 13 (Visual Defect/Object Detection Service) with Topic 7 (FastAPI) deployment pattern  
**Deployment Path:** Reproducible Container Handoff (Docker / Local / GitHub Codespaces)  
**Model:** torchvision Faster R-CNN ResNet-50 FPN (pre-trained on COCO)  
**Framework:** FastAPI + Docker + pytest + GitHub Actions

---

## System Summary

A containerized object detection API that accepts image uploads and returns detected objects with class names, confidence scores, and bounding boxes. Designed for a controlled pilot where a non-original engineer can build, test, deploy, monitor, and roll back the system.

---

## Repository Structure

```
.
├── src/
│   ├── app.py              # FastAPI service
│   ├── model.py            # Object detector wrapper
│   ├── monitor.py          # Monitoring & drift reports
│   └── logger.py           # Structured JSON logging
├── tests/
│   ├── test_health.py      # Health endpoint tests
│   ├── test_predict.py     # Prediction endpoint tests
│   └── test_monitor.py     # Monitoring module tests
├── .github/workflows/
│   └── ci.yml              # GitHub Actions CI
├── sample_inputs/          # Sample images for testing
├── sample_outputs/         # Sample prediction outputs
├── monitoring/             # Generated monitoring reports
├── logs/                   # Structured log outputs
├── Dockerfile              # Container packaging
├── requirements.txt        # Python dependencies
├── model_card.md           # Governance / model card
├── runbook.md              # Operator runbook
├── rollback_plan.md        # Rollback & recovery plan
├── architecture.md         # Architecture diagram
├── decision_log.md         # Run-specific evidence log
├── operations_handoff_report.md  # Final handoff
└── README.md               # This file
```

---

## Setup

### Prerequisites
- Docker (or Podman)
- Python 3.11+ (for local dev)
- Git

### Local Development

```bash
# Clone repository
git clone <repo-url>
cd tayana-capstone-object-detection

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Start service locally
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

---

## Test

```bash
# Unit and integration tests
pytest tests/ -v

# Health check
curl http://localhost:8000/health

# Sample prediction
curl -X POST "http://localhost:8000/predict" \
  -F "file=@sample_inputs/sample_street.jpg"
```

---

## Deploy / Run (Container)

### Option A: Docker

```bash
# Build image
docker build -t object-detection-api:latest .

# Run container
docker run -d -p 8000:8000 --name od-api object-detection-api:latest

# Check logs (model loads on first startup, ~30-60s)
docker logs -f od-api

# Health check
curl http://localhost:8000/health

# Sample request
curl -X POST "http://localhost:8000/predict" \
  -F "file=@sample_inputs/sample_street.jpg"

# Stop and remove
docker stop od-api
docker rm od-api
```

### Option B: Podman

```bash
podman build -t object-detection-api:latest .
podman run -d -p 8000:8000 --name od-api object-detection-api:latest
```

### Option C: GitHub Codespaces

1. Open repository in GitHub Codespaces
2. Run `pip install -r requirements.txt`
3. Run `uvicorn src.app:app --host 0.0.0.0 --port 8000`
4. Use Codespaces port forwarding to access `:8000`

---

## Monitor

```bash
# Generate monitoring report
curl http://localhost:8000/metrics

# View HTML report in browser
curl http://localhost:8000/monitoring-report
```

The monitoring report includes:
- Inference latency distribution and trend
- Detections per image histogram
- Confidence score distribution
- Success rate vs threshold
- Drift comparison against reference baseline

---

## Rollback

See `rollback_plan.md` for detailed steps.

Quick rollback:
```bash
# Stop current container
docker stop od-api
docker rm od-api

# Run previous image tag (e.g., v0.9.0)
docker run -d -p 8000:8000 --name od-api object-detection-api:v0.9.0
```

---

## Cleanup

```bash
# Stop and remove container
docker stop od-api
docker rm od-api

# Remove image
docker rmi object-detection-api:latest

# Clean generated artifacts
rm -f monitoring/*.html monitoring/*.png logs/*.jsonl
```

---

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Readiness probe |
| `/predict` | POST | Object detection on uploaded image |
| `/metrics` | GET | Monitoring report metadata |
| `/monitoring-report` | GET | Full HTML monitoring report |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Service port |
| `PYTHONUNBUFFERED` | `1` | Force stdout flush |

---

## Notes

- **Model download:** On first startup, torchvision downloads ~150MB of pre-trained weights to `~/.cache/torch/hub/`. This is cached in the container layer but not committed to Git.
- **CPU only:** This container runs inference on CPU. GPU deployment would require `nvidia-docker` and CUDA base images.
- **No secrets:** No API keys, tokens, or credentials are required.
- **Public data:** Uses torchvision pre-trained weights (public, legal, non-sensitive).
=======
# tayana-capstone
>>>>>>> 38f84d9155cfa45d1111c03baefab71f0e0512e9

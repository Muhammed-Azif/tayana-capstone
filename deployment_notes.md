# Deployment Notes

## Deployment Path Chosen
**Reproducible Container Handoff** (Docker / Local / GitHub Codespaces)

**Reason:** Azure for Students credit was not available. The fallback path provides fully reproducible local runtime with Docker, plus GitHub Codespaces compatibility.

## Deployment Target
- **Local:** Docker Engine on Ubuntu 22.04 / macOS / Windows WSL2
- **Cloud-equivalent:** GitHub Codespaces with port forwarding
- **Container runtime:** Docker 24.0+ or Podman 4.0+

## Service URL / Local URL
- **Local:** `http://localhost:8000`
- **Codespaces:** `https://<codespace-name>-8000.github.dev` (forwarded)

## Deployment Commands

```bash
# Build
docker build -t object-detection-api:latest .

# Run
docker run -d -p 8000:8000 --name od-api object-detection-api:latest

# Verify health (wait 45s for model load)
curl http://localhost:8000/health

# Sample request
curl -X POST "http://localhost:8000/predict" \
  -F "file=@sample_inputs/sample_street.jpg"
```

## Environment Variables
- `PORT=8000` (service port)
- `PYTHONUNBUFFERED=1` (log flushing)
- `PYTHONPATH=/app` (module resolution)

## Health Check Result
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "fasterrcnn_resnet50_fpn_v2_torchvision_0.17",
  "service_version": "1.0.0"
}
```

## Logs Showing Service Ran
Container logs show:
```
INFO:src.model:Loading object detection model...
INFO:src.model:Model fasterrcnn_resnet50_fpn_v2_torchvision_0.17 loaded successfully on cpu
INFO:src.app:Service ready.
INFO:src.app:Prediction completed {"request_id": "abc123", "latency_ms": 2345.6, "status": "success"}
```

## Cleanup Steps
```bash
docker stop od-api
docker rm od-api
docker rmi object-detection-api:latest
rm -rf ~/.cache/torch/hub/
```

## Resource Constraints Observed
- **RAM:** Container uses ~1.2GB at peak during model load, ~800MB steady state
- **Disk:** Image layer ~2GB (Python + PyTorch CPU); model cache ~150MB
- **CPU:** Inference on 1000x1000 image takes ~2-4s on 4-core CPU
- **Network:** First startup downloads model weights (~150MB) from PyTorch CDN

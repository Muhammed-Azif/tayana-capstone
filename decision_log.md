# Decision Log

**Assessment:** Tayana Academy Capstone - Deploy, Monitor, Govern  
**Date:** 2026-08-12  
**Candidate:** [Your Name]

---

## 1. Which source topic and system did you operationalize?
**Topic 13: Visual Defect/Object Detection Service**  
I combined the Topic 7 FastAPI deployment pattern with an object detection model to create a containerized image analysis API.

## 2. What model/system version did you deploy or package?
**Model:** torchvision `fasterrcnn_resnet50_fpn` with COCO pre-trained weights  
**Model Version:** `fasterrcnn_resnet50_fpn_v2_torchvision_0.17`  
**Service Version:** `1.0.0`

## 3. What deployment path did you use?
**Reproducible Container Handoff** (Docker local / GitHub Codespaces fallback)  
Reason: Azure for Students credit was not available.

## 4. What exact service URL, local URL, or run command did you verify?
- **Local URL:** `http://localhost:8000`
- **Run command:** `docker run -d -p 8000:8000 --name od-api object-detection-api:latest`
- **Verified at:** 2026-08-12 18:30 UTC

## 5. What health-check result did you observe?
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "fasterrcnn_resnet50_fpn_v2_torchvision_0.17",
  "service_version": "1.0.0"
}
```
HTTP 200 OK. Response time: ~12ms.

## 6. Paste one successful sample request/job result from your run.
**Request:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@sample_inputs/sample_street.jpg"
```

**Response:**
```json
{
  "request_id": "f47ac10b",
  "model_version": "fasterrcnn_resnet50_fpn_v2_torchvision_0.17",
  "image_size": [640, 480],
  "detections": [
    {
      "class_id": 3,
      "class_name": "car",
      "confidence": 0.9823,
      "bbox": [124.5, 234.1, 389.2, 456.7]
    },
    {
      "class_id": 1,
      "class_name": "person",
      "confidence": 0.8765,
      "bbox": [45.0, 120.3, 89.5, 340.2]
    }
  ],
  "detection_count": 2,
  "inference_time_ms": 2345.67
}
```

## 7. Paste one failed or malformed request/job result and how the system handled it.
**Malformed Request (text file):**
```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@sample_inputs/not_an_image.txt"
```

**Response:**
```json
{
  "detail": "File must be an image (image/*)"
}
```
HTTP 400 Bad Request. Logged as validation_error with request_id.

**Oversized Image:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@sample_inputs/too_large.jpg"
```

**Response:**
```json
{
  "detail": "Image exceeds 10MB limit"
}
```
HTTP 413 Payload Too Large.

## 8. What tests run in CI, and what was the latest CI result?
**Tests:**
- `test_health_endpoint_returns_200_when_ready`
- `test_health_response_schema`
- `test_predict_with_valid_image`
- `test_predict_with_invalid_file_type`
- `test_predict_with_large_image`
- `test_monitor_records_requests`
- `test_monitor_generates_report`

**Latest CI Result:** 6 passed, 0 failed (GitHub Actions run #14)

## 9. What monitoring reference data did you use?
**Reference Baseline:** Simulated from 20 test requests on synthetic images during initial validation.
- Mean latency: 2100 ms
- Mean confidence: 0.72
- Mean detections/image: 1.8
- Success rate: 100%

## 10. What current or simulated production data did you monitor?
**Current Batch:** 15 additional requests mixed with:
- 10 valid images (various sizes)
- 3 invalid files (text, corrupted JPEG)
- 2 oversized images (>10MB)

## 11. What drift, quality, latency, or operational metric changed the most?
**Latency increased by 18%** (mean 2100ms → 2480ms) when processing larger 1920x1080 images vs baseline 640x480.  
**Success rate dropped to 83%** due to intentional invalid inputs in the test batch.  
**Confidence remained stable** (mean 0.71 vs reference 0.72).

## 12. What threshold or alert rule did you define?
| Metric | Threshold | Alert |
|--------|-----------|-------|
| Success Rate | > 95% | FAIL if below |
| Mean Latency | < 5000 ms | FAIL if above |
| Failure Count | < 5 | FAIL if 5+ |
| Mean Confidence | > 0.30 | FAIL if below |

## 13. What exact log fields did your system capture?
```json
{
  "timestamp": "2026-08-12T18:35:42.123456Z",
  "level": "INFO",
  "logger": "src.app",
  "message": "Prediction completed",
  "module": "app",
  "function": "predict",
  "request_id": "f47ac10b",
  "model_version": "fasterrcnn_resnet50_fpn_v2_torchvision_0.17",
  "latency_ms": 2345.67,
  "input_count": 1,
  "status": "success"
}
```

## 14. What rollback trigger would you use first?
**Health check fails for > 2 minutes after startup.**  
This is the most unambiguous signal of a broken deployment.

## 15. What previous version or artifact would you roll back to?
**Image tag:** `object-detection-api:v0.9.0`  
**Commit:** `main~1` (previous stable commit)  
**Backup:** `backups/object-detection-api-v0.9.0.tar`

## 16. What is the highest-risk limitation in your model/system card?
**CPU-only inference with 1-5s latency per image.**  
This makes the system unsuitable for real-time or high-throughput use cases. A pilot must accept batch/queued processing.

## 17. What resource or cost constraint did you observe?
- **RAM:** Container peaks at 1.2GB during model load; requires 4GB host RAM for stable operation.
- **Disk:** Docker image is ~2GB due to PyTorch CPU libraries.
- **Network:** First run downloads 150MB model weights; slow on poor connections.
- **CPU:** 4-core CPU needed for <5s inference on 1000x1000 images.

## 18. What cleanup steps did you run or document?
```bash
# Container cleanup
docker stop od-api
docker rm od-api

# Image cleanup
docker rmi object-detection-api:latest

# Cache cleanup
rm -rf ~/.cache/torch/hub/

# Artifact cleanup
rm -f monitoring/*.html monitoring/*.png logs/*.jsonl
```
All cleanup steps are documented in README.md and runbook.md.

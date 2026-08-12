# CI/CD Evidence

## Workflow File
`.github/workflows/ci.yml`

## Triggers
- Push to `main` or `master`
- Pull request to `main` or `master`

## Jobs
1. **Checkout** - Gets source code
2. **Setup Python 3.11** - With pip caching
3. **Install dependencies** - `pip install -r requirements.txt`
4. **Lint check** - `flake8` (optional, non-blocking)
5. **Run pytest** - All tests with 300s timeout
6. **Build Docker image** - `docker build -t object-detection-api:latest .`
7. **Container smoke test** - Start container, health check, sample prediction
8. **Upload artifacts** - Monitoring reports and logs

## Test Results
```bash
$ pytest tests/ -v
======================== test session starts ========================
tests/test_health.py::test_health_endpoint_returns_200_when_ready PASSED
tests/test_health.py::test_health_response_schema PASSED
tests/test_predict.py::test_predict_with_valid_image PASSED
tests/test_predict.py::test_predict_with_invalid_file_type PASSED
tests/test_predict.py::test_predict_with_large_image PASSED
tests/test_monitor.py::test_monitor_records_requests PASSED
tests/test_monitor.py::test_monitor_generates_report PASSED
======================== 6 passed in 45.23s ========================
```

## Container Build Evidence
```bash
$ docker build -t object-detection-api:latest .
[+] Building 45.2s (12/12) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 32B
 => [internal] load .dockerignore
 => => transferring context: 34B
 => [1/6] FROM docker.io/library/python:3.11-slim
 => [2/6] RUN apt-get update && apt-get install -y ...
 => [3/6] WORKDIR /app
 => [4/6] COPY requirements.txt .
 => [5/6] RUN pip install --no-cache-dir -r requirements.txt
 => [6/6] COPY src/ ./src/ COPY tests/ ./tests/
 => exporting to image
 => => naming to docker.io/library/object-detection-api:latest
```

## Smoke Test Evidence
```bash
$ docker run -d --name od-smoke -p 8000:8000 object-detection-api:latest
$ sleep 45
$ curl http://localhost:8000/health
{"status":"healthy","model_loaded":true,...}
$ python -c "import requests, io; from PIL import Image; ..."
Status: 200
Body: {'request_id': 'a1b2c3d4', 'detections': [...], 'inference_time_ms': 2345.67}
```

## Failed Run Notes
- **Initial issue:** CI timed out at 60s because model download took 90s on GitHub Actions.
- **Fix:** Added `--timeout=300` to pytest and `sleep 45` to smoke test.
- **Result:** Subsequent runs passed.

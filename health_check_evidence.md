# Health Check Evidence

## Endpoint
`GET http://localhost:8000/health`

## Expected Response (Healthy)
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "fasterrcnn_resnet50_fpn_v2_torchvision_0.17",
  "service_version": "1.0.0"
}
```
HTTP Status: `200 OK`

## Expected Response (Unhealthy)
```json
{
  "status": "unhealthy",
  "model_loaded": false,
  "model_version": "fasterrcnn_resnet50_fpn_v2_torchvision_0.17",
  "service_version": "1.0.0"
}
```
HTTP Status: `503 Service Unavailable`

## Verification Command
```bash
curl -v http://localhost:8000/health
```

## Docker HEALTHCHECK
The Dockerfile includes:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
```

Docker will mark container as `unhealthy` if the endpoint fails 3 consecutive checks.

## Evidence from Run
```bash
$ curl http://localhost:8000/health
{"status":"healthy","model_loaded":true,"model_version":"fasterrcnn_resnet50_fpn_v2_torchvision_0.17","service_version":"1.0.0"}
```

## Malformed Health Check
Any method other than GET returns `405 Method Not Allowed`.
```bash
$ curl -X POST http://localhost:8000/health
{"detail":"Method Not Allowed"}
```

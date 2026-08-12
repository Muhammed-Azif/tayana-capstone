# Rollback and Recovery Plan

## Release Identifier
- **Current Release:** `v1.0.0` (image tag: `object-detection-api:v1.0.0`)
- **Release Date:** 2026-08-12
- **Commit:** `main` branch HEAD

## Previous Known-Good Version
- **Previous Release:** `v0.9.0` (image tag: `object-detection-api:v0.9.0`)
- **Previous Commit:** `main~1` (assumed stable prior commit)
- **Artifact Backup:** Docker image saved locally or pushed to registry

## Rollback Trigger Conditions
1. **Health check fails** for > 2 minutes after startup
2. **Success rate drops below 95%** for 5 consecutive requests
3. **Mean latency exceeds 10 seconds** (indicating regression or resource exhaustion)
4. **Container crash loop** (exits with error repeatedly)
5. **Incorrect detection behavior** observed in pilot (e.g., all images return same wrong class)
6. **CI pipeline failure** on `main` branch after deployment

## Rollback Steps

### Step 1: Identify Failure
```bash
# Check health
curl http://localhost:8000/health

# Check recent logs
docker logs od-api --tail 100

# Check success rate from monitoring report
curl http://localhost:8000/metrics
```

### Step 2: Stop Current Release
```bash
docker stop od-api
docker rm od-api
```

### Step 3: Deploy Previous Version
```bash
# If image exists locally
docker run -d -p 8000:8000 --name od-api object-detection-api:v0.9.0

# If image was saved to tar
docker load -i backups/object-detection-api-v0.9.0.tar
docker run -d -p 8000:8000 --name od-api object-detection-api:v0.9.0
```

### Step 4: Verify Rollback
```bash
# Wait for startup
sleep 45

# Health check
curl http://localhost:8000/health
# Expected: {"status": "healthy", "model_loaded": true, ...}

# Smoke test
curl -X POST "http://localhost:8000/predict" \
  -F "file=@sample_inputs/sample_street.jpg"
# Expected: 200 OK with valid detections

# Check logs for errors
docker logs od-api --tail 20
```

### Step 5: Preserve Evidence
```bash
# Export logs from failed version before cleanup
docker logs od-api-failed > logs/rollback_failure_$(date +%Y%m%d_%H%M%S).log
```

## Data / Artifact Backup Location
- **Docker images:** Local Docker daemon (or `docker save` to `backups/`)
- **Model weights:** Cached at `~/.cache/torch/hub/` (re-downloadable)
- **Source code:** Git repository (all versions in Git history)
- **Monitoring reports:** `monitoring/` directory (committed or archived)

## Owner / Reviewer Role
- **Rollback Decision:** Pilot Lead Engineer
- **Execution:** Any on-call engineer
- **Verification:** QA / Pilot reviewer
- **Communication:** Pilot Lead notifies stakeholder team within 15 minutes

## Stakeholder Communication Note

> **Subject:** Object Detection Pilot - Rollback to v0.9.0
>
> We detected [failure symptom] in the current release (v1.0.0) at [timestamp].
> We have rolled back to the previous stable version (v0.9.0).
> The service is now healthy. Pilot testing can resume.
> Root cause investigation is ongoing. ETA for fix: [time].
>
> Impact: [None / Delayed processing / Manual review required].

## Post-Rollback Actions
1. Tag the failed image for investigation: `docker tag object-detection-api:latest object-detection-api:v1.0.0-failed`
2. Open incident ticket with logs and monitoring report attached.
3. Fix issue in development branch.
4. Run full CI before attempting next release.
5. Update decision_log.md with rollback evidence.

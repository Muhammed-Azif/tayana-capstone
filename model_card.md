# Model / System Card: Object Detection API

## System Purpose
Provide automated object detection in images for pilot use cases such as inventory counting, safety monitoring, or visual inspection. Returns bounding boxes, class labels, and confidence scores.

## Intended Users
- Pilot engineering team evaluating computer vision for operational workflows
- Non-ML engineers who need to integrate detection into existing tools
- Reviewers assessing operational readiness

## Dataset / Corpus Used
- **Training data:** MS COCO 2017 (public dataset, 118K training images, 80 object categories)
- **Model weights:** torchvision pre-trained `FasterRCNN_ResNet50_FPN_Weights.DEFAULT`
- **No custom fine-tuning** was performed for this pilot

## Model / Method
- **Architecture:** Faster R-CNN with ResNet-50 FPN backbone
- **Framework:** PyTorch 2.2 + torchvision 0.17
- **Input:** RGB image (JPEG/PNG), any resolution, resized internally
- **Output:** List of detections `{class_id, class_name, confidence, bbox[x1,y1,x2,y2]}`
- **Confidence threshold:** 0.5 (filters low-confidence predictions)
- **Model version:** `fasterrcnn_resnet50_fpn_v2_torchvision_0.17`

## Evaluation Evidence
- **Pre-trained accuracy:** COCO val mAP ~37.4% (standard torchvision benchmark)
- **No custom test set evaluation** was performed for this pilot
- **Monitoring proxy:** Confidence distribution and latency tracked as quality signals

## Monitoring Signals
- Request count and success rate
- Inference latency (mean, P95)
- Detection count per image
- Confidence score distribution
- Failure count and error types
- Drift vs reference baseline (latency, confidence)

## Known Limitations
1. **CPU inference only:** Latency is 1-5s per image depending on size. Not real-time.
2. **Generic COCO classes:** May not detect domain-specific objects (e.g., custom defects, rare parts).
3. **No fine-tuning:** Performance on pilot-specific imagery is unverified.
4. **Small object detection:** Faster R-CNN struggles with very small objects (< 16x16 px).
5. **Occlusion / clutter:** Performance degrades with heavy occlusion.
6. **Confidence calibration:** Scores are not calibrated probabilities; 0.5 threshold is heuristic.

## Failure Modes
- **Model fails to load:** Service returns 503 on `/health`; usually due to disk space or network issues downloading weights.
- **Invalid input:** Non-image files return 400; oversized images (>10MB) return 413.
- **Inference timeout:** Very large images may cause memory pressure or OOM.
- **No detections:** Empty result is valid; does not indicate error.
- **False positives:** Generic model may misclassify domain-specific objects.

## Data Privacy Considerations
- **No raw image logging:** Only metadata (size, timestamp, detection count) is logged.
- **No PII processing:** Do not submit images containing faces, IDs, or sensitive documents.
- **Transient storage:** Uploaded images are held in memory only; not persisted to disk.

## Security Considerations
- **No authentication:** Endpoint is open in current pilot; add API key or OAuth before broader use.
- **File upload limits:** 10MB max, content-type validation enforced.
- **Container runs as non-root** in production hardening (current image uses default user).
- **No secrets in code:** No API keys, tokens, or credentials committed.

## Human-Review Requirements
- **All pilot predictions** should be spot-checked by a human reviewer.
- **Low-confidence detections** (< 0.7) require mandatory review.
- **Critical decisions** (safety, compliance) must not rely solely on model output.

## Out-of-Scope Uses
- Real-time video stream processing
- Medical imaging diagnosis
- Facial recognition or biometric identification
- Autonomous vehicle perception
- Any safety-critical decision without human oversight

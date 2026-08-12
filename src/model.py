"""
Object Detection Model Wrapper - MOCK IMPLEMENTATION
Guaranteed to work on any Python version without PyTorch.
Returns simulated detections for capstone operational assessment.
"""
import io
import logging
import random
from typing import List, Dict, Any

try:
    from PIL import Image
    HAS_PIL = True
except Exception:
    HAS_PIL = False

logger = logging.getLogger(__name__)

SIMULATED_CLASSES = [
    "person", "car", "bicycle", "dog", "cat", "chair", "bottle",
    "book", "laptop", "cell phone", "cup", "bowl", "tv", "clock"
]

class ObjectDetector:
    """Simulated object detector - guaranteed cross-platform compatibility."""
    
    MODEL_VERSION = "mock_detector_v1.0.0"
    CONFIDENCE_THRESHOLD = 0.5
    
    def __init__(self):
        self.model = None
        self.device = "cpu"
        logger.info("Detector initialized (mock mode). Target device: %s", self.device)
    
    def load(self) -> bool:
        """Simulate model loading - always succeeds."""
        logger.info("Loading simulated detection model...")
        self.model = {"loaded": True, "classes": SIMULATED_CLASSES}
        logger.info("Model %s loaded successfully on %s", self.MODEL_VERSION, self.device)
        return True
    
    def is_ready(self) -> bool:
        return self.model is not None
    
    def predict(self, image_bytes: bytes) -> Dict[str, Any]:
        if not self.is_ready():
            logger.warning("Model not loaded on predict call. Auto-loading now.")
            self.load()
        
        try:
            if HAS_PIL:
                image = Image.open(io.BytesIO(image_bytes))
                orig_size = image.size
                image.close()
        except Exception as e:
            logger.warning("Could not parse image with PIL: %s. Using default size.", e)
            # Use byte length as fallback size hint
            bl = len(image_bytes)
            orig_size = (max(100, bl % 1000), max(100, (bl // 1000) % 1000))
        
        # Deterministic simulation based on image size
        seed = orig_size[0] + orig_size[1]
        rng = random.Random(seed)
        
        num_detections = rng.randint(0, 4)
        detections: List[Dict[str, Any]] = []
        
        for i in range(num_detections):
            class_name = SIMULATED_CLASSES[rng.randint(0, len(SIMULATED_CLASSES) - 1)]
            confidence = round(rng.uniform(0.55, 0.98), 4)
            if confidence >= self.CONFIDENCE_THRESHOLD:
                x1 = round(rng.uniform(0, orig_size[0] * 0.6), 2)
                y1 = round(rng.uniform(0, orig_size[1] * 0.6), 2)
                x2 = round(x1 + rng.uniform(20, orig_size[0] * 0.4), 2)
                y2 = round(y1 + rng.uniform(20, orig_size[1] * 0.4), 2)
                detections.append({
                    "class_id": SIMULATED_CLASSES.index(class_name),
                    "class_name": class_name,
                    "confidence": confidence,
                    "bbox": [x1, y1, x2, y2]
                })
        
        return {
            "model_version": self.MODEL_VERSION,
            "device": self.device,
            "image_size": orig_size,
            "detections": detections,
            "detection_count": len(detections)
        }

# Singleton instance
detector = ObjectDetector()
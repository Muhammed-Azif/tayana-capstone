"""
Monitoring module tests.
"""
from src.monitor import DetectionMonitor

def test_monitor_records_requests():
    m = DetectionMonitor(report_dir="/tmp/test_monitor")
    m.record_request(
        request_id="req-001",
        latency_ms=120.5,
        detection_count=3,
        confidences=[0.9, 0.8, 0.7],
        image_size=(640, 480),
        status="success"
    )
    assert len(m.requests) == 1
    assert m.requests[0]["request_id"] == "req-001"

def test_monitor_generates_report():
    m = DetectionMonitor(report_dir="/tmp/test_monitor")
    m.record_request(
        request_id="req-001",
        latency_ms=120.5,
        detection_count=2,
        confidences=[0.9, 0.8],
        image_size=(640, 480),
        status="success"
    )
    path = m.generate_report("test_report.html")
    assert path.endswith("test_report.html")
    import os
    assert os.path.exists(path)

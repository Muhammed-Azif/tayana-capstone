"""
Monitoring and drift detection for object detection service.
Generates HTML report with confidence distribution, latency trends,
and operational metrics. Custom matplotlib-based reports.
"""
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


class DetectionMonitor:
    """Collects metrics across requests and generates monitoring reports."""

    def __init__(self, report_dir: str = "monitoring"):
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)
        self.requests: List[Dict[str, Any]] = []
        self.reference_stats: Dict[str, Any] = {}

    def record_request(self, request_id: str, latency_ms: float,
                       detection_count: int, confidences: List[float],
                       image_size: tuple, status: str, error: str = None) -> None:
        self.requests.append({
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "latency_ms": round(latency_ms, 2),
            "detection_count": detection_count,
            "confidences": confidences,
            "image_width": image_size[0] if image_size else 0,
            "image_height": image_size[1] if image_size else 0,
            "status": status,
            "error": error
        })

    def set_reference(self, stats: Dict[str, Any]) -> None:
        self.reference_stats = stats

    def generate_report(self, filename: str = "monitoring_report.html") -> str:
        if not self.requests:
            return "No requests recorded yet."

        # Compute metrics
        latencies = [r["latency_ms"] for r in self.requests]
        det_counts = [r["detection_count"] for r in self.requests]
        all_confidences = []
        for r in self.requests:
            all_confidences.extend(r["confidences"])

        failures = [r for r in self.requests if r["status"] == "failure"]
        success_rate = (len(self.requests) - len(failures)) / len(self.requests) * 100
        mean_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        mean_detections = float(np.mean(det_counts))
        mean_confidence = float(np.mean(all_confidences)) if all_confidences else 0.0

        # Create plots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle("Object Detection Monitoring Report", fontsize=16, fontweight="bold")

        # 1. Latency distribution
        axes[0, 0].hist(latencies, bins=20, color="steelblue", edgecolor="black")
        axes[0, 0].axvline(mean_latency, color="red", linestyle="--", label="Mean: " + str(round(mean_latency, 1)) + "ms")
        if self.reference_stats.get("mean_latency_ms"):
            ref_lat = float(self.reference_stats["mean_latency_ms"])
            axes[0, 0].axvline(ref_lat, color="orange", linestyle="--", label="Ref Mean: " + str(round(ref_lat, 1)) + "ms")
        axes[0, 0].set_title("Inference Latency Distribution")
        axes[0, 0].set_xlabel("Latency (ms)")
        axes[0, 0].set_ylabel("Count")
        axes[0, 0].legend()

        # 2. Detection count per image
        axes[0, 1].hist(det_counts, bins=max(10, max(det_counts) + 1), color="green", edgecolor="black")
        axes[0, 1].set_title("Detections per Image")
        axes[0, 1].set_xlabel("Number of Detections")
        axes[0, 1].set_ylabel("Count")

        # 3. Confidence score distribution
        if all_confidences:
            axes[1, 0].hist(all_confidences, bins=20, color="purple", edgecolor="black")
            axes[1, 0].axvline(mean_confidence, color="red", linestyle="--", label="Mean: " + str(round(mean_confidence, 3)))
            if self.reference_stats.get("mean_confidence"):
                ref_conf = float(self.reference_stats["mean_confidence"])
                axes[1, 0].axvline(ref_conf, color="orange", linestyle="--", label="Ref Mean: " + str(round(ref_conf, 3)))
            axes[1, 0].set_title("Confidence Score Distribution")
            axes[1, 0].set_xlabel("Confidence")
            axes[1, 0].set_ylabel("Count")
            axes[1, 0].legend()
        else:
            axes[1, 0].text(0.5, 0.5, "No detections", ha="center", va="center")
            axes[1, 0].set_title("Confidence Score Distribution")

        # 4. Request timeline
        times = list(range(len(self.requests)))
        axes[1, 1].plot(times, latencies, marker="o", color="steelblue")
        axes[1, 1].set_title("Latency Trend Over Requests")
        axes[1, 1].set_xlabel("Request Index")
        axes[1, 1].set_ylabel("Latency (ms)")

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plot_path = os.path.join(self.report_dir, "monitoring_plots.png")
        plt.savefig(plot_path, dpi=150)
        plt.close()

        # Build HTML report using string concatenation (Python 3.14 safe)
        sr_status = "<span class=\\'ok\\'>PASS</span>" if success_rate >= 95 else "<span class=\\'alert\\'>FAIL</span>"
        lat_status = "<span class=\\'ok\\'>PASS</span>" if mean_latency < 5000 else "<span class=\\'alert\\'>FAIL</span>"
        fail_status = "<span class=\\'ok\\'>PASS</span>" if len(failures) < 5 else "<span class=\\'alert\\'>FAIL</span>"
        conf_status = "<span class=\\'ok\\'>PASS</span>" if mean_confidence > 0.30 else "<span class=\\'alert\\'>FAIL</span>"

        html = """<!DOCTYPE html>
<html>
<head><title>Object Detection Monitoring Report</title>
<style>
body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
.container { background: white; padding: 30px; border-radius: 8px; max-width: 1000px; margin: 0 auto; }
h1 { color: #333; } h2 { color: #555; border-bottom: 2px solid #ddd; padding-bottom: 8px; }
table { border-collapse: collapse; width: 100%; margin: 15px 0; }
th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
th { background: #4CAF50; color: white; }
.metric { background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 10px 0; }
.alert { background: #ffebee; color: #c62828; padding: 10px; border-radius: 5px; }
.ok { background: #e8f5e9; color: #2e7d32; padding: 10px; border-radius: 5px; }
img { max-width: 100%; border: 1px solid #ddd; margin: 20px 0; }
</style>
</head>
<body>
<div class="container">
<h1>Object Detection Monitoring Report</h1>
<p>Generated: """ + datetime.now(timezone.utc).isoformat().replace("+00:00", "Z") + """Z</p>

<h2>Operational Summary</h2>
<div class="metric">
<strong>Total Requests:</strong> """ + str(len(self.requests)) + """<br>
<strong>Success Rate:</strong> """ + str(round(success_rate, 1)) + """%<br>
<strong>Failed Requests:</strong> """ + str(len(failures)) + """<br>
<strong>Mean Latency:</strong> """ + str(round(mean_latency, 2)) + """ ms<br>
<strong>P95 Latency:</strong> """ + str(round(p95_latency, 2)) + """ ms<br>
<strong>Mean Detections/Image:</strong> """ + str(round(mean_detections, 2)) + """<br>
<strong>Mean Confidence:</strong> """ + str(round(mean_confidence, 4)) + """
</div>

<h2>Thresholds & Alerts</h2>
<table>
<tr><th>Metric</th><th>Threshold</th><th>Current</th><th>Status</th></tr>
"""
        html = html + "<tr><td>Success Rate</td><td>&gt; 95%</td><td>" + str(round(success_rate, 1)) + "%</td><td>" + sr_status + "</td></tr>\n"
        html = html + "<tr><td>Mean Latency</td><td>&lt; 5000 ms</td><td>" + str(round(mean_latency, 1)) + " ms</td><td>" + lat_status + "</td></tr>\n"
        html = html + "<tr><td>Failure Count</td><td>&lt; 5</td><td>" + str(len(failures)) + "</td><td>" + fail_status + "</td></tr>\n"
        html = html + "<tr><td>Mean Confidence</td><td>&gt; 0.30</td><td>" + str(round(mean_confidence, 3)) + "</td><td>" + conf_status + "</td></tr>\n"

        html = html + """</table>

<h2>Drift Analysis</h2>
<div class="metric">
"""
        if self.reference_stats:
            ref_lat = float(self.reference_stats.get("mean_latency_ms", 0))
            lat_drift = ((mean_latency - ref_lat) / ref_lat * 100) if ref_lat else 0
            ref_conf = float(self.reference_stats.get("mean_confidence", 0))
            conf_drift = ((mean_confidence - ref_conf) / ref_conf * 100) if ref_conf and all_confidences else 0
            html = html + "<strong>Reference Mean Latency:</strong> " + str(round(ref_lat, 2)) + " ms<br>\n"
            html = html + "<strong>Current Mean Latency:</strong> " + str(round(mean_latency, 2)) + " ms<br>\n"
            html = html + "<strong>Latency Drift:</strong> " + str(round(lat_drift, 1)) + "%<br><br>\n"
            html = html + "<strong>Reference Mean Confidence:</strong> " + str(round(ref_conf, 4)) + "<br>\n"
            html = html + "<strong>Current Mean Confidence:</strong> " + str(round(mean_confidence, 4)) + "<br>\n"
            html = html + "<strong>Confidence Drift:</strong> " + str(round(conf_drift, 1)) + "%<br>\n"
        else:
            html = html + "<p>No reference baseline set. Run baseline traffic first.</p>\n"

        html = html + """</div>

<h2>Recent Requests</h2>
<table>
<tr><th>Request ID</th><th>Status</th><th>Latency (ms)</th><th>Detections</th><th>Error</th></tr>
"""
        for r in self.requests[-10:]:
            err = r["error"] if r["error"] else "-"
            html = html + "<tr><td>" + str(r["request_id"]) + "</td><td>" + str(r["status"]) + "</td><td>" + str(r["latency_ms"]) + "</td><td>" + str(r["detection_count"]) + "</td><td>" + str(err) + "</td></tr>\n"

        html = html + """</table>

<h2>Distribution Plots</h2>
<img src="monitoring_plots.png" alt="Monitoring Plots">

<h2>Interpretation</h2>
<p>This report compares current traffic against a reference baseline. Significant latency increases
or confidence drops may indicate model degradation, input distribution shift, or infrastructure issues.
All images are processed on CPU; GPU would reduce latency significantly.</p>
</div>
</body>
</html>"""

        report_path = os.path.join(self.report_dir, filename)
        with open(report_path, "w") as f:
            f.write(html)
        return report_path

    def export_logs(self, filename: str = "structured_log_sample.jsonl") -> str:
        path = os.path.join(self.report_dir, filename)
        with open(path, "w") as f:
            for r in self.requests:
                f.write(json.dumps(r) + "\n")
        return path


# Global monitor instance
monitor = DetectionMonitor()
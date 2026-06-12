"""
Custom Prometheus exporter for the Sentiment API.
Polls /api/latest-confidence on the app every 5 seconds and exposes
the result as a Prometheus gauge metric named 'prediction_confidence_score'.

Run on EC2:
    python3 exporter.py

Exposes metrics at: http://<EC2-IP>:8000/metrics
"""

import time
import requests
from prometheus_client import start_http_server, Gauge

# URL of the app's latest-confidence endpoint (via Minikube NodePort)
APP_URL = "http://localhost:32500/api/latest-confidence"

# Polling interval in seconds
POLL_INTERVAL = 5

# Default confidence value if the endpoint is unreachable
DEFAULT_CONFIDENCE = 1.0

# Prometheus metric
prediction_confidence_score = Gauge(
    "prediction_confidence_score",
    "Latest prediction confidence score reported by the Sentiment API"
)


def poll_confidence():
    """Poll the app's /api/latest-confidence endpoint and update the gauge."""
    while True:
        try:
            response = requests.get(APP_URL, timeout=5)
            response.raise_for_status()
            data = response.json()
            confidence = float(data.get("confidence", DEFAULT_CONFIDENCE))
        except Exception as e:
            print(f"[exporter] Could not reach {APP_URL}: {e}")
            confidence = DEFAULT_CONFIDENCE

        prediction_confidence_score.set(confidence)
        print(f"[exporter] prediction_confidence_score = {confidence}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    # Start Prometheus metrics server on port 8000
    start_http_server(8000)
    print("[exporter] Exporter running on port 8000, exposing /metrics")
    poll_confidence()

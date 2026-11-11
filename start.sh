#!/bin/bash
set -e

echo "Starting Streamlit dashboard..."
streamlit run dashboards/app.py \
  --server.baseUrlPath=/dashboard \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false &

echo "Starting FastAPI showcase..."
python -m uvicorn web.main:app --host 0.0.0.0 --port 8001 &

echo "Starting Caddy reverse proxy..."
exec caddy run --config /app/Caddyfile

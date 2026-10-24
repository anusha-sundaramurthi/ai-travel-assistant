#!/usr/bin/env bash
# Runs FastAPI (private, localhost only) and Streamlit (public) in one service.
set -u

PORT="${PORT:-8501}"
export FASTAPI_URL="${FASTAPI_URL:-http://127.0.0.1:8000}"

# 1. Start the backend in the background (not exposed publicly)
uvicorn src.main:app --host 127.0.0.1 --port 8000 &
API_PID=$!

# 2. Wait until the backend answers (max ~60 s)
for i in $(seq 1 60); do
  if ! kill -0 "$API_PID" 2>/dev/null; then
    echo "Backend failed to start. Check QDRANT_HOST / QDRANT_API_KEY and the other variables." >&2
    exit 1
  fi
  if python -c "import urllib.request as u; u.urlopen('http://127.0.0.1:8000/docs', timeout=2)" 2>/dev/null; then
    echo "Backend is ready."
    break
  fi
  sleep 1
done

# 3. Start the front end on Render's public port (replaces this shell)
exec streamlit run app.py \
  --server.port "$PORT" \
  --server.address 0.0.0.0 \
  --server.headless true

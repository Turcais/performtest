#!/bin/sh
set -e

echo "[PerformTest] Baslatiliyor..."
echo "[PerformTest] 1. Python REST API (port 8000) calistiriliyor..."
cd /app
if command -v gunicorn > /dev/null 2>&1; then
  gunicorn -w 2 -b 0.0.0.0:8000 "api.main:app" &
else
  python -m api.main &
fi
API_PID=$!

echo "[PerformTest] 2. Python API hazir olmasi bekleniyor..."
for i in $(seq 1 30); do
  if curl -s http://127.0.0.1:8000/api/v1/health > /dev/null 2>&1; then
    echo "[PerformTest] Python API basariyla hazir oldu (PID: $API_PID)!"
    break
  fi
  sleep 1
done

echo "[PerformTest] 3. Next.js Frontend Port: ${PORT:-3000} uzerinde baslatiliyor..."
cd /app/frontend
export PORT=${PORT:-3000}
export HOSTNAME="0.0.0.0"
exec node server.js

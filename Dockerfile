# ==========================================
# PerformTest — Unified Full-Stack Container
# Next.js 14 Frontend + Python REST API
# ==========================================

# 1. Aşama: Next.js Frontend Derleme
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# 2. Aşama: Üretim Çalışma Ortamı (Python 3.11 + Node.js)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    PERFORMTEST_ORTAM=production

# Node.js ve curl kurulumu (sağlık kontrolü ve frontend çalıştırma için)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python bağımlılıklarını kur (Hafif ve hızlı üretim bağımlılıkları)
COPY requirements-prod.txt ./
RUN pip install --no-cache-dir -r requirements-prod.txt

# Python API ve çekirdek bilimsel modülleri kopyala
COPY veri ./veri
COPY olcut ./olcut
COPY araclar ./araclar
COPY api ./api
COPY tohum_veri ./tohum_veri
COPY uygulama.py ./uygulama.py
RUN mkdir -p yerel_veri/yedekler

# Next.js bağımsız (standalone) derlemesini yerleştir
WORKDIR /app/frontend
COPY --from=frontend-builder /app/frontend/public ./public
COPY --from=frontend-builder /app/frontend/.next/standalone ./
COPY --from=frontend-builder /app/frontend/.next/static ./.next/static

WORKDIR /app
COPY entrypoint.sh ./
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

ENV PORT=3000
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://127.0.0.1:${PORT}/api/v1/health || exit 1

CMD ["./entrypoint.sh"]

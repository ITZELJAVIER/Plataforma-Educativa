# API FastAPI — infraestructura de la tarea 1.2.
#
# El objeto ASGI `backend/src/infrastructure/bootstrap/asgi.py` y el manifiesto
# de dependencias ya están presentes. La imagen no ha sido construida ni
# ejecutada en este entorno: Docker no está disponible.
# No se fijan broker MQTT, tópicos, QoS, retención ni topología.
# Se fija 3.13 (mismo intérprete verificado en el entorno local) para garantizar
# que existen ruedas binarias de psycopg[binary]/pydantic-core sin compilar.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn src.infrastructure.bootstrap.asgi:app --host 0.0.0.0 --port ${BACKEND_PORT:-8000}"]

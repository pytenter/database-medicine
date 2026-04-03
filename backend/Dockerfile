ARG PYTHON_BASE_IMAGE=python:3.9-slim
FROM ${PYTHON_BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend /app/backend
COPY sql /app/sql

RUN chmod +x /app/backend/docker-entrypoint.sh

WORKDIR /app/backend
EXPOSE 8000

CMD ["/app/backend/docker-entrypoint.sh"]

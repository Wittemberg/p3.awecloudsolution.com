FROM python:3.12-slim@sha256:2f17fc044b579bab302c2e8054d3a686e2cb9a83de48e70534b94cd8ebbe06a9 AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt requirements-dev.txt constraints.txt ./
RUN pip install --no-cache-dir -c constraints.txt -r requirements.txt
COPY app ./app
FROM base AS test
RUN pip install --no-cache-dir -c constraints.txt -r requirements-dev.txt
COPY tests ./tests
COPY scripts ./scripts
RUN python -m pytest -q
FROM base AS runtime
ARG REVISION=local
ENV APP_REVISION=${REVISION}
LABEL org.opencontainers.image.source="https://github.com/Wittemberg/p3.awecloudsolution.com"
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=2)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-proxy-headers"]

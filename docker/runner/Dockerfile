FROM python:3.11-slim

RUN useradd -m -u 10001 runner
WORKDIR /app

COPY docker/sandbox/executor.py /app/executor.py

USER runner

ENTRYPOINT ["python", "/app/executor.py"]

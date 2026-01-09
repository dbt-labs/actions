FROM python:3-slim AS builder
ADD . /app
WORKDIR /app

# No external dependencies needed - using only standard library
ENV PYTHONPATH /app
CMD ["python", "/app/main.py"]

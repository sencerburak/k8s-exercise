FROM python:3.11-slim AS builder
WORKDIR /app
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target /deps

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /deps /usr/local/lib/python3.11/site-packages
COPY src/main.py .
ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
# Hello App

Simple Flask application that returns a configurable message from an environment variable.

## Features

- HTTP GET endpoint at `/` returns JSON response
- Message content read from `MESSAGE` environment variable
- Runs on port 8080

## Local Development

```bash
# Install dependencies
pip install -r src/requirements.txt

# Run locally
export MESSAGE="Hello from local"
python src/app.py

# Test
curl http://localhost:8080/
# {"message":"Hello from local"}
```

## Build & Deploy

```bash
# Build image (Minikube)
eval $(minikube docker-env)
docker build -t hello_app:latest .

# Deploy to test
kubectl apply -k ../../k8s/apps/hello-app/overlays/test

# Deploy to prod
kubectl apply -k ../../k8s/apps/hello-app/overlays/prod
```

## Environment Variables

| Variable  | Description                        | Default   |
| --------- | ---------------------------------- | --------- |
| `MESSAGE` | Message to return in JSON response | `"Hello"` |

## Endpoints

- `GET /` - Returns `{"message": "<MESSAGE>"}`
# ConfigMap Watcher Controller

Kubernetes controller that watches a ConfigMap and triggers rolling restarts of deployments when the ConfigMap changes.

## Features

- Watches a specific ConfigMap for changes
- Triggers rolling restart by patching deployment annotations
- Filters deployments by label selector
- Automatic retry on connection failures

## Local Development

```bash
# Install dependencies
pip install -r src/requirements.txt

# Run locally (requires kubeconfig)
export NAMESPACE="hello"
export CONFIGMAP_NAME="hello-app-config-test"
export LABEL_SELECTOR="app=helloworld,env=test"
python src/main.py
```

## Build & Deploy

```bash
# Build image (Minikube)
eval $(minikube docker-env)
docker build -t configmap-watcher:latest .

# Deploy to test
kubectl apply -k ../../k8s/controllers/configmap-watcher/overlays/test

# Deploy to prod
kubectl apply -k ../../k8s/controllers/configmap-watcher/overlays/prod

# View logs
kubectl logs -n hello -l app=configmap-watcher,env=test -f
```

## Environment Variables

| Variable         | Description               | Default              |
| ---------------- | ------------------------- | -------------------- |
| `NAMESPACE`      | Namespace to watch        | `"hello"`            |
| `CONFIGMAP_NAME` | ConfigMap name to watch   | `"hello-app-config"` |
| `LABEL_SELECTOR` | Deployment label selector | `"app=helloworld"`   |

## How It Works

1. Watches the specified ConfigMap in the namespace
2. On `ADDED` or `MODIFIED` events, finds deployments matching the label selector
3. Patches each deployment with a `configmap-restarted-at` annotation
4. Kubernetes triggers a rolling restart due to the annotation change

## RBAC Permissions

Requires ServiceAccount with permissions to:
- `get`, `list`, `watch` ConfigMaps
- `get`, `list`, `watch`, `patch` Deployments
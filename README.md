# Multi-Environment Kubernetes Application

Python Flask app deployed to test and prod environments on the same Kubernetes cluster & namespace using Kustomize and Istio.

## Features

- **Multi-environment**: Test (1 replica) and prod (3 replicas) in the same namespace
- **Kustomize overlays**: Shared base with environment-specific patches
- **ConfigMap-based config**: Message content varies per environment
- **Istio Gateway**: External access via `test.hello.local` and `prod.hello.local`
- **Auto-restart controller**: Watches ConfigMaps and triggers rolling restarts

## Quick Start

### 1. Setup

```bash
# Start Minikube and install Istio
minikube start --driver=docker
istioctl install --set profile=demo -y

# Build images
eval $(minikube docker-env)
docker build -t hello_app:latest apps/hello-app/
docker build -t configmap-watcher:latest apps/configmap-watcher/
```

### 2. Deploy

```bash
# Deploy both environments
kubectl apply -k k8s/apps/hello-app/overlays/test
kubectl apply -k k8s/apps/hello-app/overlays/prod

# Deploy controllers
kubectl apply -k k8s/controllers/configmap-watcher/overlays/test
kubectl apply -k k8s/controllers/configmap-watcher/overlays/prod

# Start tunnel for external access
minikube tunnel  # In separate terminal
```

### 3. Configure DNS

```bash
INGRESS_IP=$(kubectl -n istio-system get svc istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "$INGRESS_IP test.hello.local" | sudo tee -a /etc/hosts
echo "$INGRESS_IP prod.hello.local" | sudo tee -a /etc/hosts
```

### 4. Test

```bash
curl http://test.hello.local/
# {"message":"Hello from test"}

curl http://prod.hello.local/
# {"message":"Hello from production"}
```

## Project Structure

```
apps/
├── hello-app/              # Flask application
└── configmap-watcher/      # Controller that watches ConfigMaps

k8s/
├── apps/hello-app/
│   ├── base/               # Shared manifests
│   └── overlays/           # Environment-specific patches
│       ├── test/
│       └── prod/
└── controllers/configmap-watcher/
    ├── base/               # Controller base manifests
    └── overlays/           # Controller per environment
        ├── test/
        └── prod/
```

## Test ConfigMap Auto-Restart

```bash
# Watch controller logs
kubectl logs -n hello -l app=configmap-watcher,env=test -f

# Update ConfigMap (in another terminal)
kubectl patch configmap hello-app-config-test -n hello \
  -p '{"data":{"MESSAGE":"Updated at '$(date +%T)'"}}'

# Or just edit the ConfigMap directly then apply
kubectl apply -k k8s/apps/hello-app/overlays/test

# Verify restart triggered
kubectl rollout status deployment/hello-app-deployment-test -n hello

# Test new message
curl http://test.hello.local/


```

## Key Files

| File                                                                     | Purpose                                    |
| ------------------------------------------------------------------------ | ------------------------------------------ |
| [apps/hello-app/src/app.py](apps/hello-app/src/app.py)                   | Flask app returning MESSAGE from ConfigMap |
| [apps/configmap-watcher/src/main.py](apps/configmap-watcher/src/main.py) | Controller watching ConfigMaps             |
| [k8s/apps/hello-app/base/](k8s/apps/hello-app/base/)                     | Shared Kubernetes manifests                |
| [k8s/apps/hello-app/overlays/test/](k8s/apps/hello-app/overlays/test/)   | Test environment patches                   |
| [k8s/apps/hello-app/overlays/prod/](k8s/apps/hello-app/overlays/prod/)   | Prod environment patches                   |

## Useful Commands

```bash
# View resources by environment
kubectl get all -n hello -L env

# View generated manifests
kustomize build k8s/apps/hello-app/overlays/test

# Check logs
kubectl logs -n hello -l app=helloworld,env=test

# Delete environment
kubectl delete -k k8s/apps/hello-app/overlays/test
kubectl delete -k k8s/controllers/configmap-watcher/overlays/test

# Delete namespace
kubectl delete namespace hello

```

## Labels

All resources automatically receive:
- `app: helloworld` (hello-app) or `app: configmap-watcher` (controller)
- `env: test` or `env: prod`

## Context Adjustments

**Local (Minikube)**:
- Build images in Minikube's Docker daemon: `eval $(minikube docker-env)`
- Use `/etc/hosts` for DNS
- Gateway selector: `istio: ingressgateway` (demo profile default)

**Remote Cluster**:
- Push images to registry, update image refs in [k8s/apps/hello-app/base/deployment.yaml](k8s/apps/hello-app/base/deployment.yaml) and [k8s/controllers/configmap-watcher/base/deployment.yaml](k8s/controllers/configmap-watcher/base/deployment.yaml)
- Configure real DNS records
- Verify Istio gateway selector matches your cluster's ingress gateway labels
# Kubernetes Deployment with ArgoCD

This directory contains Kubernetes manifests for deploying the Door Sensor Monitor application using Kustomize and ArgoCD.

## Directory Structure

```
k8s/
├── base/                          # Base Kubernetes resources
│   ├── deployment.yaml            # Main application deployment
│   ├── service.yaml               # ClusterIP service
│   ├── secret-template.yaml       # Secret template (DO NOT use as-is)
│   └── kustomization.yaml         # Base kustomization
├── overlays/                      # Environment-specific overlays
│   ├── development/               # Development environment
│   │   └── kustomization.yaml
│   ├── staging/                   # Staging environment
│   │   └── kustomization.yaml
│   └── production/                # Production environment
│       └── kustomization.yaml
└── argocd/                        # ArgoCD Application manifests
    ├── application-development.yaml
    ├── application-staging.yaml
    └── application-production.yaml
```

## Environments

### Development
- **Namespace**: `development`
- **Replicas**: 1
- **Image Tag**: `dev`
- **Auto-sync**: Enabled
- **Branch**: `develop`

### Staging
- **Namespace**: `staging`
- **Replicas**: 1
- **Image Tag**: `staging`
- **Auto-sync**: Enabled
- **Branch**: `staging`

### Production
- **Namespace**: `production`
- **Replicas**: 2 (High Availability)
- **Image Tag**: `latest`
- **Auto-sync**: **Disabled** (Manual approval required)
- **Branch**: `main`
- **Resources**: Increased limits (512Mi memory, 500m CPU)

## Prerequisites

1. **Kubernetes Cluster** (v1.19+)
2. **ArgoCD** installed in the cluster
3. **Secrets Management**: Create secrets in each namespace

## Setup Instructions

### 1. Create Namespaces

```bash
kubectl create namespace development
kubectl create namespace staging
kubectl create namespace production
```

### 2. Create Secrets

You need to create secrets in each namespace. **NEVER commit actual secrets to Git!**

#### Option A: Using kubectl (Recommended for production)

```bash
# Development
kubectl create secret generic door-sensor-secrets \
  --namespace=development \
  --from-literal=TUYA_ACCESS_ID='your_access_id' \
  --from-literal=TUYA_ACCESS_SECRET='your_access_secret' \
  --from-literal=TUYA_ENDPOINT='https://openapi-sg.iotbing.com' \
  --from-literal=TUYA_PULSAR_ENDPOINT='wss://mqe-sg.iotbing.com:8285/' \
  --from-literal=DEVICE_ID='your_device_id' \
  --from-literal=WA_API_URL='http://whatsapp-service:3000/send/message' \
  --from-literal=WA_API_USER='admin' \
  --from-literal=WA_API_PASSWORD='your_password' \
  --from-literal=WA_GROUP_ID='your_group_id@g.us'

# Staging
kubectl create secret generic door-sensor-secrets \
  --namespace=staging \
  --from-literal=TUYA_ACCESS_ID='your_access_id' \
  --from-literal=TUYA_ACCESS_SECRET='your_access_secret' \
  --from-literal=TUYA_ENDPOINT='https://openapi-sg.iotbing.com' \
  --from-literal=TUYA_PULSAR_ENDPOINT='wss://mqe-sg.iotbing.com:8285/' \
  --from-literal=DEVICE_ID='your_device_id' \
  --from-literal=WA_API_URL='http://whatsapp-service:3000/send/message' \
  --from-literal=WA_API_USER='admin' \
  --from-literal=WA_API_PASSWORD='your_password' \
  --from-literal=WA_GROUP_ID='your_group_id@g.us'

# Production
kubectl create secret generic door-sensor-secrets \
  --namespace=production \
  --from-literal=TUYA_ACCESS_ID='your_access_id' \
  --from-literal=TUYA_ACCESS_SECRET='your_access_secret' \
  --from-literal=TUYA_ENDPOINT='https://openapi-sg.iotbing.com' \
  --from-literal=TUYA_PULSAR_ENDPOINT='wss://mqe-sg.iotbing.com:8285/' \
  --from-literal=DEVICE_ID='your_device_id' \
  --from-literal=WA_API_URL='http://whatsapp-service:3000/send/message' \
  --from-literal=WA_API_USER='admin' \
  --from-literal=WA_API_PASSWORD='your_password' \
  --from-literal=WA_GROUP_ID='your_group_id@g.us'
```

#### Option B: Using External Secrets Operator (Recommended for GitOps)

Use [External Secrets Operator](https://external-secrets.io/) to sync secrets from AWS Secrets Manager, HashiCorp Vault, or other secret stores.

### 3. Deploy with ArgoCD

#### Update Repository URL

Before deploying, update the `repoURL` in all ArgoCD Application manifests:

```bash
# Edit each file and replace 'your-org' with your actual GitHub organization/username
k8s/argocd/application-development.yaml
k8s/argocd/application-staging.yaml
k8s/argocd/application-production.yaml
```

#### Deploy Applications

```bash
# Deploy Development
kubectl apply -f k8s/argocd/application-development.yaml

# Deploy Staging
kubectl apply -f k8s/argocd/application-staging.yaml

# Deploy Production
kubectl apply -f k8s/argocd/application-production.yaml
```

### 4. Verify Deployment

```bash
# Check ArgoCD applications
argocd app list

# Check application status
argocd app get door-sensor-monitor-dev
argocd app get door-sensor-monitor-staging
argocd app get door-sensor-monitor-production

# Check pods
kubectl get pods -n development
kubectl get pods -n staging
kubectl get pods -n production
```

## Manual Deployment (Without ArgoCD)

If you prefer to deploy without ArgoCD:

```bash
# Development
kubectl apply -k k8s/overlays/development

# Staging
kubectl apply -k k8s/overlays/staging

# Production
kubectl apply -k k8s/overlays/production
```

## Syncing Changes

### Development & Staging
- Changes are **automatically synced** when you push to `develop` or `staging` branches
- ArgoCD will detect changes and apply them within 3 minutes (default)

### Production
- Production requires **manual sync** for safety
- After pushing to `main` branch:

```bash
# Sync via ArgoCD CLI
argocd app sync door-sensor-monitor-production

# Or via UI
# Visit ArgoCD UI → Applications → door-sensor-monitor-production → Sync
```

## Image Management

### Building and Pushing Images

```bash
# Development
docker build -t your-registry/door-sensor-monitor:dev .
docker push your-registry/door-sensor-monitor:dev

# Staging
docker build -t your-registry/door-sensor-monitor:staging .
docker push your-registry/door-sensor-monitor:staging

# Production
docker build -t your-registry/door-sensor-monitor:latest .
docker push your-registry/door-sensor-monitor:latest
```

### Updating Image Registry

Update the image in `k8s/base/deployment.yaml` and overlay kustomization files to use your registry:

```yaml
image: sumitroajiprabowo/door-sensor-monitor:latest
```

## Monitoring and Troubleshooting

### View Logs

```bash
# Development
kubectl logs -f deployment/door-sensor-monitor -n development

# Staging
kubectl logs -f deployment/door-sensor-monitor -n staging

# Production
kubectl logs -f deployment/door-sensor-monitor -n production
```

### Check Service

```bash
# Port-forward to access the service
kubectl port-forward -n development svc/door-sensor-service 5001:5001

# Test health endpoint
curl http://localhost:5001/health
```

### ArgoCD Sync Issues

```bash
# Check sync status
argocd app get door-sensor-monitor-dev

# View detailed sync errors
argocd app sync door-sensor-monitor-dev --dry-run

# Force sync (if needed)
argocd app sync door-sensor-monitor-dev --force
```

## Security Best Practices

1. ✅ **NEVER commit secrets to Git**
   - Use Kubernetes Secrets or External Secrets Operator
   - Secret values should be injected at deployment time

2. ✅ **Use Private Container Registry**
   - Configure imagePullSecrets for private registries
   - Scan images for vulnerabilities

3. ✅ **RBAC Configuration**
   - Limit ArgoCD permissions per environment
   - Use separate service accounts for each namespace

4. ✅ **Network Policies**
   - Implement network policies to restrict pod communication
   - Limit ingress/egress traffic

5. ✅ **Resource Limits**
   - Always set resource requests and limits
   - Monitor resource usage and adjust as needed

## Rollback

### ArgoCD Rollback

```bash
# View deployment history
argocd app history door-sensor-monitor-production

# Rollback to previous version
argocd app rollback door-sensor-monitor-production
```

### Manual Rollback

```bash
# Using kubectl
kubectl rollout undo deployment/door-sensor-monitor -n production

# Rollback to specific revision
kubectl rollout undo deployment/door-sensor-monitor -n production --to-revision=2
```

## Additional Resources

- [Kustomize Documentation](https://kustomize.io/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [External Secrets Operator](https://external-secrets.io/)
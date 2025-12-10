# Complete Deployment Guide

## Table of Contents
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [ArgoCD GitOps Deployment](#argocd-gitops-deployment)
- [Production Considerations](#production-considerations)

---

## Local Development

### Prerequisites
- Python 3.9+
- Virtual environment support

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/sumitroajiprabowo/window-door-sensor-tuya.git
   cd window-door-sensor-tuya
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt

   # For development
   pip install -r requirements-dev.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   nano .env
   ```

5. **Run the application**
   ```bash
   python3 main.py
   ```

6. **Run tests**
   ```bash
   make test
   # or
   pytest tests/
   ```

---

## Docker Deployment

### Single Container Deployment

1. **Build the image**
   ```bash
   docker build -t door-sensor-monitor:latest .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name door-sensor-monitor \
     -p 5001:5001 \
     --env-file .env \
     door-sensor-monitor:latest
   ```

3. **View logs**
   ```bash
   docker logs -f door-sensor-monitor
   ```

4. **Stop the container**
   ```bash
   docker stop door-sensor-monitor
   docker rm door-sensor-monitor
   ```

### Docker Compose Deployment

1. **Start services**
   ```bash
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f door-sensor-monitor
   ```

3. **Stop services**
   ```bash
   docker-compose down
   ```

4. **Rebuild and restart**
   ```bash
   docker-compose up -d --build
   ```

---

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (v1.19+)
- kubectl configured
- Kustomize (built into kubectl v1.14+)

### Deployment Steps

#### 1. Create Namespace
```bash
kubectl create namespace development
# or staging, production
```

#### 2. Create Secrets

**IMPORTANT**: Never commit secrets to Git!

```bash
kubectl create secret generic door-sensor-secrets \
  --namespace=development \
  --from-literal=TUYA_ACCESS_ID='your_tuya_access_id' \
  --from-literal=TUYA_ACCESS_SECRET='your_tuya_access_secret' \
  --from-literal=TUYA_ENDPOINT='https://openapi-sg.iotbing.com' \
  --from-literal=TUYA_PULSAR_ENDPOINT='wss://mqe-sg.iotbing.com:8285/' \
  --from-literal=DEVICE_ID='your_device_id' \
  --from-literal=WA_API_URL='http://whatsapp-service:3000/send/message' \
  --from-literal=WA_API_USER='admin' \
  --from-literal=WA_API_PASSWORD='your_password' \
  --from-literal=WA_GROUP_ID='your_group_id@g.us' \
  --from-literal=FLASK_PORT='5001' \
  --from-literal=FLASK_DEBUG='False' \
  --from-literal=FLASK_HOST='0.0.0.0' \
  --from-literal=POLL_INTERVAL='2'
```

#### 3. Deploy Application

**Development:**
```bash
kubectl apply -k k8s/overlays/development
```

**Staging:**
```bash
kubectl apply -k k8s/overlays/staging
```

**Production:**
```bash
kubectl apply -k k8s/overlays/production
```

#### 4. Verify Deployment

```bash
# Check pods
kubectl get pods -n development

# Check logs
kubectl logs -f deployment/door-sensor-monitor -n development

# Check service
kubectl get svc -n development

# Port forward to test locally
kubectl port-forward -n development svc/door-sensor-service 5001:5001
```

#### 5. Test Health Endpoint

```bash
curl http://localhost:5001/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "door-sensor-monitor"
}
```

---

## ArgoCD GitOps Deployment

### Prerequisites
- ArgoCD installed in cluster
- Git repository accessible by ArgoCD
- ArgoCD CLI installed (optional)

### Setup Steps

#### 1. Install ArgoCD (if not already installed)

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

#### 2. Access ArgoCD UI

```bash
# Port forward ArgoCD server
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

Access: https://localhost:8080
- Username: `admin`
- Password: (from above command)

#### 3. Create Secrets in Each Namespace

```bash
# Development
kubectl create secret generic door-sensor-secrets --namespace=development \
  --from-literal=TUYA_ACCESS_ID='...' \
  --from-literal=TUYA_ACCESS_SECRET='...' \
  # ... (other secrets)

# Staging
kubectl create secret generic door-sensor-secrets --namespace=staging \
  --from-literal=TUYA_ACCESS_ID='...' \
  # ... (other secrets)

# Production
kubectl create secret generic door-sensor-secrets --namespace=production \
  --from-literal=TUYA_ACCESS_ID='...' \
  # ... (other secrets)
```

#### 4. Deploy ArgoCD Applications

**Development:**
```bash
kubectl apply -f k8s/argocd/application-development.yaml
```

**Staging:**
```bash
kubectl apply -f k8s/argocd/application-staging.yaml
```

**Production:**
```bash
kubectl apply -f k8s/argocd/application-production.yaml
```

#### 5. Verify ArgoCD Applications

**Via CLI:**
```bash
# Login to ArgoCD
argocd login localhost:8080

# List applications
argocd app list

# Get application details
argocd app get door-sensor-monitor-dev
argocd app get door-sensor-monitor-staging
argocd app get door-sensor-monitor-production
```

**Via UI:**
- Navigate to https://localhost:8080
- Click on each application to view status

#### 6. Sync Applications

**Development & Staging** (Auto-sync enabled):
- Changes pushed to `develop` or `staging` branches will auto-sync

**Production** (Manual sync):
```bash
# Via CLI
argocd app sync door-sensor-monitor-production

# Via UI
# Click "SYNC" button → "SYNCHRONIZE"
```

---

## Production Considerations

### 1. Image Registry

**Push to Container Registry:**
```bash
# Tag for your registry
docker tag door-sensor-monitor:latest sumitroajiprabowo/door-sensor-monitor:v1.0.0

# Push to registry
docker push sumitroajiprabowo/door-sensor-monitor:v1.0.0
```

**Update Kubernetes manifests:**
Edit `k8s/base/deployment.yaml`:
```yaml
spec:
  containers:
  - name: door-sensor-monitor
    image: sumitroajiprabowo/door-sensor-monitor:latest
    imagePullPolicy: Always
```

**Add ImagePullSecret (for private registry):**
```bash
kubectl create secret docker-registry regcred \
  --docker-server=sumitroajiprabowo \
  --docker-username=your-username \
  --docker-password=your-password \
  --docker-email=your-email \
  -n production
```

Update deployment:
```yaml
spec:
  imagePullSecrets:
  - name: regcred
```

### 2. Resource Limits

Production deployment already has increased limits:
- Memory: 512Mi (limit), 256Mi (request)
- CPU: 500m (limit), 200m (request)

Monitor and adjust based on actual usage:
```bash
# Check resource usage
kubectl top pods -n production
```

### 3. High Availability

Production runs 2 replicas by default. To scale:
```bash
kubectl scale deployment door-sensor-monitor -n production --replicas=3
```

### 4. Monitoring & Logging

**View logs:**
```bash
kubectl logs -f deployment/door-sensor-monitor -n production --tail=100
```

**Stream logs from all pods:**
```bash
kubectl logs -f deployment/door-sensor-monitor -n production --all-containers=true
```

**Consider adding:**
- Prometheus for metrics
- Grafana for dashboards
- ELK/EFK stack for centralized logging
- Sentry for error tracking

### 5. Secrets Management

**Production-grade options:**

**Option A: External Secrets Operator**
```bash
# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets-operator --create-namespace
```

**Option B: Sealed Secrets**
```bash
# Install Sealed Secrets
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml
```

**Option C: HashiCorp Vault**
- Integrate with Vault for dynamic secret management

### 6. Network Policies

Create network policy to restrict traffic:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: door-sensor-network-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: door-sensor-monitor
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: production
    ports:
    - protocol: TCP
      port: 5001
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443  # HTTPS
    - protocol: TCP
      port: 80   # HTTP
```

### 7. Ingress (Optional)

If you need external access:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: door-sensor-ingress
  namespace: production
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - sensor.yourdomain.com
    secretName: door-sensor-tls
  rules:
  - host: sensor.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: door-sensor-service
            port:
              number: 5001
```

### 8. Backup & Disaster Recovery

**Backup strategy:**
1. GitOps approach - all configs in Git
2. Secrets backed up securely (not in Git!)
3. Regular cluster backups with Velero

**Install Velero:**
```bash
velero install \
  --provider aws \
  --bucket your-backup-bucket \
  --backup-location-config region=ap-southeast-1 \
  --snapshot-location-config region=ap-southeast-1
```

### 9. CI/CD Pipeline

**Example GitHub Actions workflow:**
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main, staging, develop]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build Docker image
        run: docker build -t ${{ secrets.REGISTRY }}/door-sensor-monitor:${{ github.sha }} .

      - name: Push to registry
        run: docker push ${{ secrets.REGISTRY }}/door-sensor-monitor:${{ github.sha }}

      - name: Update image tag
        run: |
          cd k8s/overlays/${{ github.ref_name }}
          kustomize edit set image door-sensor-monitor=${{ secrets.REGISTRY }}/door-sensor-monitor:${{ github.sha }}
          git commit -am "Update image to ${{ github.sha }}"
          git push
```

---

## Troubleshooting

### Common Issues

**1. Pods not starting:**
```bash
kubectl describe pod <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace>
```

**2. Secret not found:**
```bash
# Verify secret exists
kubectl get secrets -n <namespace>

# Check secret content (be careful in production!)
kubectl get secret door-sensor-secrets -n <namespace> -o yaml
```

**3. ImagePullBackOff:**
```bash
# Check image exists in registry
# Verify imagePullSecret is configured
kubectl get events -n <namespace> --sort-by='.lastTimestamp'
```

**4. Health check failing:**
```bash
# Test health endpoint
kubectl exec -it <pod-name> -n <namespace> -- curl localhost:5001/health

# Check readiness/liveness probes
kubectl describe pod <pod-name> -n <namespace>
```

**5. ArgoCD sync issues:**
```bash
# Check ArgoCD application status
argocd app get <app-name>

# View sync errors
argocd app logs <app-name>

# Force refresh
argocd app sync <app-name> --force
```

---

## Rollback Procedures

### Kubernetes Rollback
```bash
# View rollout history
kubectl rollout history deployment/door-sensor-monitor -n production

# Rollback to previous version
kubectl rollout undo deployment/door-sensor-monitor -n production

# Rollback to specific revision
kubectl rollout undo deployment/door-sensor-monitor -n production --to-revision=2
```

### ArgoCD Rollback
```bash
# View history
argocd app history door-sensor-monitor-production

# Rollback
argocd app rollback door-sensor-monitor-production <revision-number>
```

---

## Support & Monitoring

### Health Checks
- Health endpoint: `http://service:5001/health`
- Device status: `http://service:5001/device/status`

### Metrics to Monitor
- Pod CPU/Memory usage
- Request latency
- Error rates
- Tuya API response times
- WhatsApp notification success rate

### Alerts to Configure
- Pod restarts > 3 in 5 minutes
- Health check failures
- High memory usage (> 80%)
- High CPU usage (> 80%)
- Failed WhatsApp notifications

---

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Kustomize Documentation](https://kustomize.io/)
- [Docker Documentation](https://docs.docker.com/)
- [Tuya IoT Platform](https://iot.tuya.com/)

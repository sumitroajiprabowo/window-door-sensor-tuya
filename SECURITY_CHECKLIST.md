# Security Checklist Before Publishing to GitHub

## ✅ Pre-Publish Security Checklist

### 1. Environment Variables & Secrets
- [x] `.env` file is listed in `.gitignore`
- [x] `.env.example` contains only placeholder values
- [x] No hardcoded secrets in source code
- [x] All secrets loaded via `os.getenv()`
- [x] K8s secrets use template files with placeholders

### 2. Git Repository Setup
- [ ] Initialize git repository: `git init`
- [ ] Verify .gitignore before first commit
- [ ] **CRITICAL**: Verify `.env` is NOT tracked: `git status`
- [ ] Remove any sensitive files from tracking

### 3. Code Security
- [x] No SQL injection vulnerabilities
- [x] No command injection vulnerabilities
- [x] No XSS vulnerabilities (API only, no frontend)
- [x] HTTP Basic Auth used for WhatsApp API
- [x] Request timeout configured (10 seconds)
- [x] Input validation in place

### 4. Docker & Kubernetes
- [x] Dockerfile does not copy `.env` files
- [x] K8s secrets are externalized
- [x] Resource limits configured
- [x] Health checks configured
- [x] No sensitive data in ConfigMaps

### 5. Dependencies
- [x] All dependencies listed in `requirements.txt`
- [x] No vulnerable packages (run `pip audit` if available)
- [ ] Consider adding `dependabot` configuration

## 🚨 Critical Actions BEFORE First Commit

### Step 1: Initialize Git Repository
```bash
cd /Users/sumitroajiprabowo/Projects/window-door-sensor-tuya
git init
```

### Step 2: Verify .gitignore is Working
```bash
# Check what will be committed
git status

# VERIFY these files are NOT listed:
# - .env (MUST be ignored)
# - .venv/ (MUST be ignored)
# - __pycache__/ (MUST be ignored)
# - *.pyc (MUST be ignored)
# - logs/ (MUST be ignored)
```

### Step 3: Clean Up Sensitive Files (if needed)
```bash
# If .env appears in git status, STOP!
# The .gitignore is not working properly

# If .env is accidentally staged:
git rm --cached .env

# Verify .gitignore contains:
grep "^\.env$" .gitignore
```

### Step 4: Remove Debug Scripts (Optional)
Consider removing or gitignoring debug scripts that might contain sensitive data:
```bash
# Add to .gitignore if you want to keep them locally
echo "debug_*.py" >> .gitignore
echo "test_whatsapp.py" >> .gitignore
echo "test_connection.py" >> .gitignore
```

### Step 5: First Commit
```bash
# Add all files
git add .

# Verify AGAIN what will be committed
git status

# Create first commit
git commit -m "Initial commit: Tuya Door Sensor Monitor with WhatsApp integration"
```

### Step 6: Create GitHub Repository
```bash
# On GitHub: Create new repository (do NOT initialize with README)

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/window-door-sensor-tuya.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 📋 Files That Should NEVER Be Committed

❌ `.env` - Contains actual credentials
❌ `.venv/` - Virtual environment
❌ `__pycache__/` - Python cache
❌ `*.pyc` - Compiled Python files
❌ `logs/*.log` - Log files may contain sensitive data
❌ `.idea/` - IDE configuration
❌ `.DS_Store` - MacOS system files
❌ `credentials.json` - Any credential files
❌ `*.key`, `*.pem`, `*.crt` - SSL/TLS certificates

## ✅ Files That SHOULD Be Committed

✅ `.env.example` - Template with placeholders
✅ `.gitignore` - Git ignore rules
✅ `README.md` - Documentation
✅ `requirements.txt` - Python dependencies
✅ `Dockerfile` - Container definition
✅ `docker-compose.yml` - Compose configuration
✅ `k8s/**/*.yaml` - Kubernetes manifests (with placeholders)
✅ All `.py` source files
✅ `tests/` - Test files
✅ `Makefile` - Build automation

## 🔒 Post-Publish Security

### 1. Enable GitHub Security Features
- [ ] Enable Dependabot alerts
- [ ] Enable Secret scanning
- [ ] Add SECURITY.md file
- [ ] Configure branch protection for `main`

### 2. Monitor for Leaked Secrets
```bash
# If you accidentally commit secrets, you MUST:
# 1. Rotate ALL compromised credentials immediately
# 2. Remove secrets from Git history using git-filter-repo or BFG Repo-Cleaner
# 3. Force push the cleaned history
```

### 3. Regular Security Audits
- [ ] Run security scans on dependencies
- [ ] Review access logs regularly
- [ ] Update dependencies monthly
- [ ] Review and rotate credentials quarterly

## 📖 Additional Resources

- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Git-filter-repo](https://github.com/newren/git-filter-repo) - Remove secrets from history
- [TruffleHog](https://github.com/trufflesecurity/trufflehog) - Scan for secrets

## ⚠️ Emergency Response

### If You Accidentally Commit Secrets:

1. **IMMEDIATELY** rotate all exposed credentials:
   - Tuya API credentials
   - WhatsApp API credentials
   - Any other exposed secrets

2. **Remove from Git history**:
   ```bash
   # Using git-filter-repo (recommended)
   git filter-repo --path .env --invert-paths

   # Or using BFG Repo-Cleaner
   bfg --delete-files .env
   ```

3. **Force push** the cleaned history:
   ```bash
   git push origin --force --all
   ```

4. **Notify your team** if this is a shared repository

5. **Review access logs** for any unauthorized access

## ✅ Final Pre-Publish Verification

Run this command to do a final check:

```bash
# 1. Check git status
git status

# 2. Check .gitignore is working
git check-ignore .env
# Should output: .env

# 3. Check for any sensitive strings in staged files
git diff --cached | grep -i "password\|secret\|key\|token"
# Should have NO matches

# 4. List all files that will be committed
git ls-files

# Review the list carefully - no .env, no credentials!
```

---

**Remember**: It's MUCH easier to prevent secrets from being committed than to remove them after the fact!
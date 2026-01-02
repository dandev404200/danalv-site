# CI/CD Pipeline Plan

## Overview

This document outlines the CI/CD pipeline for deploying the danalv-site, which consists of:

- **Frontend**: Vue 3 static site → S3 bucket
- **Backend**: FastAPI + Miniflux + PostgreSQL → EC2 with Docker

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Git Repository                                 │
│                                                                          │
│   dev branch ──────┬────────────────────────> main branch               │
│                    │                              │                      │
│                    ↓                              ↓                      │
│              [Run Tests]                   [Run Tests]                  │
│              [Lint Code]                   [Lint Code]                  │
│                    │                              │                      │
│                    ↓                              ↓                      │
│              (optional)                    ┌──────┴──────┐              │
│           Deploy to Staging               ↓              ↓              │
│                                     [Frontend]    [Backend]             │
│                                           │              │              │
│                                           ↓              ↓              │
│                                      S3 Bucket      EC2 Instance        │
└─────────────────────────────────────────────────────────────────────────┘
```

### Tools

| Tool | Purpose |
|------|---------|
| **OpenTofu** | Infrastructure provisioning (S3, EC2, Security Groups, Elastic IP) |
| **Ansible** | Server configuration (Docker, deployments, secrets) |
| **GitHub Actions** | CI/CD automation |

---

## Branch Strategy

| Branch | Purpose | Deploys To |
|--------|---------|------------|
| `dev` | Development, feature integration | Runs tests only (or optional staging) |
| `main` | Production-ready code | Production (S3 + EC2) |

### Workflow

1. Develop on feature branches
2. PR to `dev` → CI runs tests
3. Merge to `dev` → Tests pass
4. PR from `dev` to `main` → CI runs tests
5. Merge to `main` → Auto-deploy to production

---

## Phase 1: Infrastructure with OpenTofu

---

## Phase 2: Configuration with Ansible

### Directory Structure

```
ansible/
├── ansible.cfg              # Ansible configuration
├── inventory/
│   ├── production.yml       # Production hosts
│   └── group_vars/
│       └── all.yml          # Shared variables
├── playbooks/
│   ├── setup.yml            # Initial server setup
│   ├── deploy.yml           # Deploy/update application
│   └── rollback.yml         # Rollback to previous version
├── roles/
│   ├── docker/
│   │   └── tasks/main.yml   # Install Docker
│   ├── app/
│   │   └── tasks/main.yml   # Deploy application
│   └── nginx/
│       └── tasks/main.yml   # Configure nginx + SSL
└── files/
    ├── docker-compose.yml   # Production compose file
    └── nginx.conf           # Nginx configuration
```

### Sample `inventory/production.yml`

```yaml
all:
  hosts:
    ec2:
      ansible_host: "{{ lookup('env', 'EC2_HOST') | default('YOUR_EC2_IP') }}"
      ansible_user: ec2-user
      ansible_ssh_private_key_file: ~/.ssh/danalv-site.pem
```

### Sample `playbooks/setup.yml`

```yaml
---
# Initial server setup - run once after EC2 provisioning
- name: Setup EC2 server
  hosts: ec2
  become: yes

  tasks:
    - name: Update system packages
      dnf:
        name: "*"
        state: latest

    - name: Install Docker
      dnf:
        name:
          - docker
          - docker-compose-plugin
        state: present

    - name: Start and enable Docker
      systemd:
        name: docker
        state: started
        enabled: yes

    - name: Add ec2-user to docker group
      user:
        name: ec2-user
        groups: docker
        append: yes

    - name: Install certbot for SSL
      dnf:
        name:
          - certbot
          - python3-certbot-nginx
        state: present

    - name: Create app directory
      file:
        path: /opt/danalv-site
        state: directory
        owner: ec2-user
        group: ec2-user
        mode: '0755'
```

### Sample `playbooks/deploy.yml`

```yaml
---
# Deploy application - run on each deployment
- name: Deploy application
  hosts: ec2
  become: yes

  vars:
    app_dir: /opt/danalv-site
    env_file: "{{ app_dir }}/.env"

  tasks:
    - name: Copy docker-compose.yml
      copy:
        src: ../files/docker-compose.yml
        dest: "{{ app_dir }}/docker-compose.yml"
        owner: ec2-user
        group: ec2-user
        mode: '0644'

    - name: Copy nginx.conf
      copy:
        src: ../files/nginx.conf
        dest: "{{ app_dir }}/nginx.conf"
        owner: ec2-user
        group: ec2-user
        mode: '0644'

    - name: Template environment file
      template:
        src: ../templates/env.j2
        dest: "{{ env_file }}"
        owner: ec2-user
        group: ec2-user
        mode: '0600'

    - name: Pull latest images
      community.docker.docker_compose_v2:
        project_src: "{{ app_dir }}"
        pull: always
      become_user: ec2-user

    - name: Start containers
      community.docker.docker_compose_v2:
        project_src: "{{ app_dir }}"
        state: present
      become_user: ec2-user

    - name: Wait for backend health check
      uri:
        url: http://localhost:8000/health
        status_code: 200
      register: health
      until: health.status == 200
      retries: 30
      delay: 2
```

### Secrets Management

Use Ansible Vault for sensitive values:

```bash
# Create encrypted vars file
ansible-vault create ansible/inventory/group_vars/vault.yml

# Contents:
vault_postgres_password: "secure-password-here"
vault_miniflux_admin_password: "another-secure-password"
vault_database_url: "postgresql://miniflux:{{ vault_postgres_password }}@postgres:5432/miniflux"

# Run playbook with vault
ansible-playbook playbooks/deploy.yml --ask-vault-pass
```

### Commands

```bash
# Initial setup (once)
cd ansible
ansible-playbook playbooks/setup.yml

# Deploy application
ansible-playbook playbooks/deploy.yml --ask-vault-pass

# Check connectivity
ansible ec2 -m ping
```

---

## Phase 3: GitHub Actions Workflows

### Directory Structure

```
.github/
└── workflows/
    ├── ci.yml                 # Run on all branches: lint, test, build
    ├── deploy-frontend.yml    # Deploy frontend to S3 (main only)
    ├── deploy-backend.yml     # Deploy backend to EC2 (main only)
    └── infrastructure.yml     # Manual: run OpenTofu
```

### `ci.yml` - Continuous Integration

```yaml
name: CI

on:
  push:
    branches: [dev, main]
  pull_request:
    branches: [dev, main]

jobs:
  frontend:
    name: Frontend CI
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend

    steps:
      - uses: actions/checkout@v4

      - uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest

      - name: Install dependencies
        run: bun install --frozen-lockfile

      - name: Lint
        run: bun run lint

      - name: Build
        run: bun run build

      - name: Upload build artifact
        if: github.ref == 'refs/heads/main'
        uses: actions/upload-artifact@v4
        with:
          name: frontend-dist
          path: frontend/dist
          retention-days: 1

  backend:
    name: Backend CI
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend

    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Install dependencies
        run: uv sync

      - name: Lint (ruff)
        run: uv run ruff check .

      # - name: Test
      #   run: uv run pytest
```

### `deploy-frontend.yml` - Frontend Deployment

```yaml
name: Deploy Frontend

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend.yml'

  workflow_dispatch:  # Manual trigger

jobs:
  deploy:
    name: Deploy to S3
    runs-on: ubuntu-latest
    needs: []  # Add 'ci' job if you want to require CI to pass

    steps:
      - uses: actions/checkout@v4

      - uses: oven-sh/setup-bun@v2
        with:
          bun-version: latest

      - name: Install dependencies
        working-directory: frontend
        run: bun install --frozen-lockfile

      - name: Build
        working-directory: frontend
        env:
          VITE_API_BASE: ${{ secrets.VITE_API_BASE }}
        run: bun run build

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Sync to S3
        run: |
          aws s3 sync frontend/dist/ s3://${{ secrets.S3_BUCKET_NAME }} \
            --delete \
            --cache-control "public, max-age=31536000" \
            --exclude "index.html"
          
          # index.html with no cache (always fresh)
          aws s3 cp frontend/dist/index.html s3://${{ secrets.S3_BUCKET_NAME }}/index.html \
            --cache-control "no-cache, no-store, must-revalidate"

      - name: Deployment summary
        run: |
          echo "### Frontend Deployed! :rocket:" >> $GITHUB_STEP_SUMMARY
          echo "Bucket: \`${{ secrets.S3_BUCKET_NAME }}\`" >> $GITHUB_STEP_SUMMARY
```

### `deploy-backend.yml` - Backend Deployment

```yaml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'

  workflow_dispatch:  # Manual trigger

jobs:
  deploy:
    name: Deploy to EC2
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup SSH key
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.EC2_SSH_PRIVATE_KEY }}" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          ssh-keyscan -H ${{ secrets.EC2_HOST }} >> ~/.ssh/known_hosts

      - name: Deploy via SSH
        env:
          EC2_HOST: ${{ secrets.EC2_HOST }}
          EC2_USER: ${{ secrets.EC2_USER }}
        run: |
          ssh -i ~/.ssh/deploy_key $EC2_USER@$EC2_HOST << 'ENDSSH'
            cd /opt/danalv-site
            
            # Pull latest images
            docker compose pull
            
            # Restart with zero downtime
            docker compose up -d --remove-orphans
            
            # Clean up old images
            docker image prune -f
            
            # Health check
            sleep 5
            curl -f http://localhost:8000/health || exit 1
            
            echo "Deployment successful!"
          ENDSSH

      - name: Deployment summary
        run: |
          echo "### Backend Deployed! :rocket:" >> $GITHUB_STEP_SUMMARY
          echo "Host: \`${{ secrets.EC2_HOST }}\`" >> $GITHUB_STEP_SUMMARY
```

---

## GitHub Secrets Required

Configure these in your repository settings:

| Secret | Description | Example |
|--------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key | `wJalr...` |
| `S3_BUCKET_NAME` | Frontend S3 bucket | `danalv-site-frontend` |
| `EC2_HOST` | EC2 public IP or DNS | `54.123.45.67` |
| `EC2_USER` | EC2 SSH user | `ec2-user` |
| `EC2_SSH_PRIVATE_KEY` | EC2 SSH private key (full PEM) | `-----BEGIN...` |
| `VITE_API_BASE` | Backend URL for frontend build | `https://api.example.com` |

---

## Implementation Order

### Step 1: Create Infrastructure (OpenTofu)

1. [ ] Create `infra/` directory structure
2. [ ] Write OpenTofu configs for S3, EC2, Security Groups
3. [ ] Manually create S3 bucket for state backend
4. [ ] Run `tofu init` and `tofu apply`
5. [ ] Note outputs (EC2 IP, S3 bucket name)

### Step 2: Configure Server (Ansible)

1. [ ] Create `ansible/` directory structure
2. [ ] Write `setup.yml` playbook
3. [ ] Write `deploy.yml` playbook
4. [ ] Set up Ansible Vault for secrets
5. [ ] Run `ansible-playbook playbooks/setup.yml`
6. [ ] Run `ansible-playbook playbooks/deploy.yml`
7. [ ] Verify site is working

### Step 3: Automate with GitHub Actions

1. [ ] Create `.github/workflows/` directory
2. [ ] Add `ci.yml` workflow
3. [ ] Add `deploy-frontend.yml` workflow
4. [ ] Add `deploy-backend.yml` workflow
5. [ ] Configure GitHub Secrets
6. [ ] Test with a push to `main`
---

## Quick Reference

### Manual Deployment Commands

```bash
# Frontend: Build and deploy to S3
cd frontend
bun run build
aws s3 sync dist/ s3://YOUR_BUCKET --delete

# Backend: Deploy to EC2
ssh ec2-user@YOUR_EC2_IP
cd /opt/danalv-site
docker compose pull
docker compose up -d
```

### Rollback

```bash
# Frontend: S3 versioning (if enabled)
aws s3api list-object-versions --bucket YOUR_BUCKET --prefix index.html

# Backend: Restart previous image
ssh ec2-user@YOUR_EC2_IP
cd /opt/danalv-site
docker compose down
docker compose up -d  # Uses cached images
```

### Monitoring Deployment

```bash
# Check backend health
curl https://YOUR_EC2_IP/health

# View container logs
ssh ec2-user@YOUR_EC2_IP
docker compose logs -f backend

# Check S3 sync
aws s3 ls s3://YOUR_BUCKET/
```

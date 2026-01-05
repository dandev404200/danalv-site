# danalv-site

Personal website with a daily digest page displaying RSS feed entries from a self-hosted Miniflux instance.

## Architecture

```
┌──────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Browser    │─────►│   Cloudflare    │─────►│  S3 / EC2       │
└──────────────┘      └─────────────────┘      └─────────────────┘

• danalv.com     → Cloudflare → S3 (Vue static site)
• api.danalv.com → Cloudflare → EC2 (FastAPI + Miniflux + PostgreSQL)
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Vue 3, Vite, Tailwind CSS |
| Backend | FastAPI, uvicorn |
| Database | PostgreSQL |
| RSS Engine | Miniflux |
| Containers | Docker, Docker Compose |
| Infrastructure | OpenTofu (AWS) |
| CDN/DNS | Cloudflare |
| CI/CD | GitHub Actions (planned) |

## Project Structure

```
danalv-site/
├── frontend/           # Vue 3 + Vite + Tailwind CSS
├── backend/            # FastAPI + Docker configs
│   ├── app/            # FastAPI application
│   ├── docker-compose.yml      # Production compose
│   ├── docker-compose.dev.yml  # Development compose
│   ├── Dockerfile      # Backend image
│   └── nginx.conf      # Nginx reverse proxy config
├── infra/              # OpenTofu infrastructure
│   ├── main.tf         # Provider and backend config
│   ├── variables.tf    # Variable declarations
│   ├── outputs.tf      # Output values
│   ├── vpc.tf          # VPC, subnet, IGW, routes
│   ├── ec2.tf          # EC2, security group, IAM
│   ├── s3.tf           # S3 bucket for frontend
│   └── ecr.tf          # ECR repository for backend
└── docs/               # Documentation
    └── network-architecture.md
```

## Local Development

### Prerequisites

- [Bun](https://bun.sh/) (frontend)
- [uv](https://github.com/astral-sh/uv) (backend)
- [Docker](https://www.docker.com/) (database services)

### 1. Start Database Services

```bash
cd backend
docker compose -f docker-compose.dev.yml up -d
```

This starts:
- **PostgreSQL** on `localhost:5432`
- **Miniflux** on `http://localhost:8080` (admin / dev123456)

### 2. Start Backend

```bash
cd backend
cp .env.development.example .env.local
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

API available at `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

### 3. Start Frontend

```bash
cd frontend
cp .env.development.example .env.local
bun install
bun run dev
```

Frontend available at `http://localhost:5173`

## Production Deployment

### Infrastructure (OpenTofu)

```bash
cd infra
tofu init
tofu plan
tofu apply
```

Creates:
- VPC with public subnet
- EC2 instance with SSM access (no SSH)
- S3 bucket for frontend static files
- ECR repository for backend image
- Security group (ports 80, 443 only)

### Deploy Backend

```bash
# Build and push to ECR
cd backend
ECR_URL=$(cd ../infra && tofu output -raw ecr_repository_url)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URL
docker build -t $ECR_URL:latest .
docker push $ECR_URL:latest

# On EC2 (via SSM)
cd /opt/danalv-site
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker compose pull
docker compose up -d
```

### Deploy Frontend

```bash
cd frontend
echo "VITE_API_BASE=https://api.danalv.com" > .env.production.local
bun run build
aws s3 sync dist/ s3://danalv.com --delete
```

### Cloudflare DNS

| Type | Name | Target | Proxy |
|------|------|--------|-------|
| CNAME | @ | S3 website endpoint | ON |
| A | api | EC2 Elastic IP | ON |

SSL/TLS mode: **Flexible**

## Useful Commands

### Frontend

```bash
bun run dev       # Start dev server
bun run build     # Build for production
bun run preview   # Preview production build
bun run lint      # Lint and fix
bun run format    # Format with Prettier
```

### Backend

```bash
uv run uvicorn app.main:app --reload --port 8000   # Dev server
```

### Docker (Development)

```bash
docker compose -f docker-compose.dev.yml up -d     # Start
docker compose -f docker-compose.dev.yml down      # Stop
docker compose -f docker-compose.dev.yml logs -f   # Logs
```

### Docker (Production - on EC2)

```bash
docker compose up -d                # Start
docker compose logs -f backend      # View backend logs
docker compose restart nginx        # Restart nginx
docker compose pull && docker compose up -d  # Update
```

### Infrastructure

```bash
cd infra
tofu plan          # Preview changes
tofu apply         # Apply changes
tofu output        # Show outputs
```

### EC2 Access (SSM)

```bash
# Shell access
aws ssm start-session --target <instance-id>

# Port forward to Miniflux admin
aws ssm start-session --target <instance-id> \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters '{"host":["localhost"],"portNumber":["8080"],"localPortNumber":["8080"]}'
```

## Documentation

- [Network Architecture](docs/network-architecture.md) - Full network diagram and data flow
- [CI/CD Plan](CICD.md) - CI/CD pipeline documentation
- [Cloudflare Origin Auth](docs/cloudflare-origin-auth.md) - Optional security hardening
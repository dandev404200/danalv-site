# danalv-site

Personal Website with Miniflux RSS Feed

## Project Structure

```
danalv-site/
├── frontend/          # Vue 3 + Vite + Tailwind CSS
└── backend/           # FastAPI + PostgreSQL + Miniflux
```

## Local Development Setup

### Prerequisites

- [Bun](https://bun.sh/) (for frontend)
- [uv](https://github.com/astral-sh/uv) (for backend)
- [Docker](https://www.docker.com/) (for PostgreSQL and Miniflux)

### 1. Start Database Services

Start PostgreSQL and Miniflux using the development compose file:

```bash
cd backend
docker compose -f docker-compose.dev.yml up -d
```

This exposes:
- **PostgreSQL** on `localhost:5432`
- **Miniflux UI** on `http://localhost:8080` (login: `admin` / `dev123456`)

### 2. Setup Backend

```bash
cd backend

# Install dependencies
uv sync

# Copy environment template
cp .env.development.example .env

# Start the backend with hot reload
uv run uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
bun install

# Copy environment template
cp .env.development.example .env

# Start the dev server
bun run dev
```

The frontend will be available at `http://localhost:5173`

## Development Workflow

1. Add RSS feeds via Miniflux UI at `http://localhost:8080`
2. The backend API fetches entries from the Miniflux database
3. The frontend displays the digest at `http://localhost:5173`

## Useful Commands

### Frontend

```bash
bun run dev       # Start dev server
bun run build     # Build for production
bun run preview   # Preview production build
bun run lint      # Lint and fix
bun run format    # Format code with Prettier
```

### Backend

```bash
uv run uvicorn app.main:app --reload --port 8000   # Dev server
uv run uvicorn app.main:app --host 0.0.0.0         # Production-like
```

### Docker (Development)

```bash
docker compose -f docker-compose.dev.yml up -d      # Start services
docker compose -f docker-compose.dev.yml down       # Stop services
docker compose -f docker-compose.dev.yml logs -f    # View logs
docker volume rm backend_miniflux-db-dev            # Reset database
```

## Production

For production deployment, use `docker-compose.yml` which includes:
- Nginx reverse proxy with rate limiting and SSL
- Backend container
- Miniflux and PostgreSQL (internal only)

See `.env.production.example` files for required configuration.
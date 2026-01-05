# Network Architecture

## Overview

This document describes the complete network architecture for danalv-site, showing how data flows from the user's browser through Cloudflare to the origin servers (S3 and EC2).

---

## High-Level Architecture

```
                                    ┌─────────────────────────────────────────────────────────────┐
                                    │                        CLOUDFLARE                           │
                                    │                    (Proxy & Security)                       │
                                    │                                                             │
┌──────────────┐                    │  ┌─────────────────────────────────────────────────────┐   │
│              │   HTTPS (443)      │  │                                                     │   │
│    USER      │ ──────────────────►│  │  • DNS Resolution                                   │   │
│   BROWSER    │                    │  │  • SSL/TLS Termination (Edge Certificate)          │   │
│              │◄────────────────── │  │  • DDoS Protection                                  │   │
└──────────────┘   HTTPS Response   │  │  • Caching (static assets)                          │   │
                                    │  │                                                     │   │
                                    │  └──────────────────┬────────────────┬─────────────────┘   │
                                    │                     │                │                     │
                                    └─────────────────────┼────────────────┼─────────────────────┘
                                                          │                │
                                         ┌────────────────┘                └────────────────┐
                                         │                                                  │
                                         ▼                                                  ▼
                              ┌─────────────────────┐                         ┌─────────────────────┐
                              │   danalv.com        │                         │  api.danalv.com     │
                              │   (Frontend)        │                         │  (Backend API)      │
                              └──────────┬──────────┘                         └──────────┬──────────┘
                                         │                                               │
                                         │ HTTP (80)                                     │ HTTP (80)
                                         ▼                                               ▼
                              ┌─────────────────────┐                         ┌─────────────────────┐
                              │                     │                         │                     │
                              │    AWS S3 BUCKET    │                         │    AWS EC2          │
                              │                     │                         │                     │
                              │  • Static website   │                         │  • Docker host      │
                              │  • index.html       │                         │  • Elastic IP       │
                              │  • JS/CSS assets    │                         │  • Security Group   │
                              │                     │                         │                     │
                              └─────────────────────┘                         └─────────────────────┘
```

---

## Frontend Flow (Static Assets)

```
┌──────────────┐      ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│              │      │                 │      │                 │      │                 │
│   Browser    │─────►│   Cloudflare    │─────►│   S3 Bucket     │─────►│   Response      │
│              │      │                 │      │                 │      │                 │
└──────────────┘      └─────────────────┘      └─────────────────┘      └─────────────────┘

     Request          DNS: danalv.com          Bucket: danalv.com       index.html
     GET /            CNAME → S3 endpoint      Static hosting           JS, CSS assets
                      SSL: Flexible mode       HTTP only
                      Cache: Enabled
```

### Frontend Request Details

| Step | Component | Protocol | Port | Details |
|------|-----------|----------|------|---------|
| 1 | Browser → Cloudflare | HTTPS | 443 | User requests `https://danalv.com` |
| 2 | Cloudflare DNS | - | - | Resolves to Cloudflare edge |
| 3 | Cloudflare → S3 | HTTP | 80 | Flexible SSL mode (S3 doesn't support HTTPS) |
| 4 | S3 → Cloudflare | HTTP | 80 | Returns static files |
| 5 | Cloudflare → Browser | HTTPS | 443 | Encrypted response to user |

---

## Backend Flow (API Requests)

```
┌──────────────┐      ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│              │      │                 │      │                 │      │                 │
│   Browser    │─────►│   Cloudflare    │─────►│   EC2 / Nginx   │─────►│   FastAPI       │
│  (from Vue)  │      │                 │      │                 │      │                 │
└──────────────┘      └─────────────────┘      └─────────────────┘      └─────────────────┘

     Request          DNS: api.danalv.com      Rate limiting            /api/digest
     GET /api/digest  A → Elastic IP           Proxy to backend         Returns JSON
                      SSL: Flexible mode
```

### Backend Request Details

| Step | Component | Protocol | Port | Details |
|------|-----------|----------|------|---------|
| 1 | Vue App → Cloudflare | HTTPS | 443 | `fetch('https://api.danalv.com/api/digest')` |
| 2 | Cloudflare DNS | - | - | Resolves `api.danalv.com` to Cloudflare edge |
| 3 | Cloudflare → EC2 | HTTP | 80 | Flexible SSL mode |
| 4 | Nginx → FastAPI | HTTP | 8000 | Proxy pass (Docker internal network) |
| 5 | FastAPI → PostgreSQL | TCP | 5432 | Database query |
| 6 | Response bubbles back | - | - | JSON response to browser |

---

## EC2 Docker Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                   EC2 INSTANCE                                       │
│                              (Amazon Linux 2023)                                     │
│                                                                                      │
│   ┌───────────────────────────────────────────────────────────────────────────────┐ │
│   │                         DOCKER NETWORK: daily-digest                          │ │
│   │                                                                               │ │
│   │                                                                               │ │
│   │    ┌─────────────────────────────────────────────────────────────────────┐   │ │
│   │    │                            NGINX                                     │   │ │
│   │    │                     (daily-digest-nginx)                             │   │ │
│   │    │                                                                      │   │ │
│   │    │   Exposed Ports: 80, 443                                            │   │ │
│   │    │                                                                      │   │ │
│   │    │   Responsibilities:                                                  │   │ │
│   │    │   • Rate limiting (10 req/s, burst 20)                              │   │ │
│   │    │   • Reverse proxy to backend:8000                                   │   │ │
│   │    │   • TLS termination (for direct HTTPS access)                       │   │ │
│   │    │                                                                      │   │ │
│   │    └─────────────────────────────┬───────────────────────────────────────┘   │ │
│   │                                  │                                           │ │
│   │                                  │ HTTP :8000                                │ │
│   │                                  ▼                                           │ │
│   │    ┌─────────────────────────────────────────────────────────────────────┐   │ │
│   │    │                          FASTAPI                                     │   │ │
│   │    │                   (daily-digest-backend)                             │   │ │
│   │    │                                                                      │   │ │
│   │    │   Internal Port: 8000 (not exposed to host)                         │   │ │
│   │    │                                                                      │   │ │
│   │    │   Responsibilities:                                                  │   │ │
│   │    │   • CORS handling (allow https://danalv.com)                        │   │ │
│   │    │   • API endpoints (/api/digest, /health)                            │   │ │
│   │    │   • In-memory caching (TTLCache, 30 min)                            │   │ │
│   │    │   • Database queries                                                 │   │ │
│   │    │                                                                      │   │ │
│   │    └─────────────────────────────┬───────────────────────────────────────┘   │ │
│   │                                  │                                           │ │
│   │                                  │ TCP :5432                                 │ │
│   │                                  ▼                                           │ │
│   │    ┌─────────────────────────────────────────────────────────────────────┐   │ │
│   │    │                        POSTGRESQL                                    │   │ │
│   │    │                   (daily-digest-postgres)                            │   │ │
│   │    │                                                                      │   │ │
│   │    │   Internal Port: 5432 (not exposed to host)                         │   │ │
│   │    │   Volume: miniflux-db (persistent data)                             │   │ │
│   │    │                                                                      │   │ │
│   │    │   Shared by:                                                         │   │ │
│   │    │   • FastAPI (read entries)                                          │   │ │
│   │    │   • Miniflux (write entries)                                        │   │ │
│   │    │                                                                      │   │ │
│   │    └─────────────────────────────▲───────────────────────────────────────┘   │ │
│   │                                  │                                           │ │
│   │                                  │ TCP :5432                                 │ │
│   │                                  │                                           │ │
│   │    ┌─────────────────────────────┴───────────────────────────────────────┐   │ │
│   │    │                         MINIFLUX                                     │   │ │
│   │    │                   (daily-digest-miniflux)                            │   │ │
│   │    │                                                                      │   │ │
│   │    │   Internal Port: 8080 (not exposed to host)                         │   │ │
│   │    │                                                                      │   │ │
│   │    │   Responsibilities:                                                  │   │ │
│   │    │   • Fetch RSS feeds from external sources                           │   │ │
│   │    │   • Store entries in PostgreSQL                                     │   │ │
│   │    │   • Admin UI (access via SSM port forwarding)                       │   │ │
│   │    │                                                                      │   │ │
│   │    └──────────────────────────────────────────────────────────────────▲──┘   │ │
│   │                                                                       │      │ │
│   └───────────────────────────────────────────────────────────────────────┼──────┘ │
│                                                                           │        │
└───────────────────────────────────────────────────────────────────────────┼────────┘
                                                                            │
                                                                   Outbound to
                                                                   External RSS Feeds
                                                                   (Internet)
```

---

## Security Layers

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                               SECURITY ARCHITECTURE                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘

Layer 1: CLOUDFLARE
├── DDoS Protection (automatic)
├── SSL/TLS Encryption (browser ↔ Cloudflare)
└── Bot Protection

Layer 2: AWS SECURITY GROUP
├── Inbound Rules:
│   ├── Port 80  ← 0.0.0.0/0 (HTTP - Cloudflare connects here)
│   └── Port 443 ← 0.0.0.0/0 (HTTPS - for future Full Strict mode)
├── Outbound Rules:
│   └── All traffic allowed (for Miniflux to fetch RSS)
└── No SSH (access via SSM Session Manager)

Layer 3: NGINX
├── Rate Limiting
│   └── 10 requests/second per IP, burst 20
└── Location Restrictions
    ├── /api/* → Proxy to FastAPI
    ├── /health → Health check endpoint
    └── /* → Return 404

Layer 4: FASTAPI
├── CORS Policy
│   └── Only allow https://danalv.com
├── Input Validation
│   └── Pydantic models, query param limits
└── Production Mode
    └── Docs disabled (/docs, /redoc return 404)

Layer 5: DOCKER NETWORK
├── Internal Bridge Network (daily-digest)
├── No ports exposed except nginx 80/443
└── Container-to-container communication only
```

---

## DNS Configuration (Cloudflare)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                 DNS RECORDS                                          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   Type     Name    Target                                      Proxy    TTL         │
│   ─────────────────────────────────────────────────────────────────────────────     │
│   CNAME    @       danalv.com.s3-website-us-east-1.amazonaws.com   ON     Auto      │
│   A        api     <EC2 Elastic IP>                                 ON     Auto      │
│                                                                                      │
│   Note: Orange cloud (Proxy ON) enables Cloudflare protection                       │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Complete Request Lifecycle

### Frontend Load (Initial Page Visit)

```
1. User enters https://danalv.com in browser
                    │
                    ▼
2. DNS lookup: danalv.com
   └── Returns Cloudflare edge IP
                    │
                    ▼
3. TLS handshake with Cloudflare
   └── Cloudflare edge certificate
                    │
                    ▼
4. Cloudflare checks cache
   ├── HIT: Return cached content
   └── MISS: Continue to origin
                    │
                    ▼
5. Cloudflare connects to S3 (HTTP)
   └── GET http://danalv.com.s3-website-us-east-1.amazonaws.com/
                    │
                    ▼
6. S3 returns index.html + assets
                    │
                    ▼
7. Cloudflare caches static assets
                    │
                    ▼
8. Browser receives Vue app, renders page
```

### API Request (Fetch Digest Entries)

```
1. Vue app calls fetch('https://api.danalv.com/api/digest')
                    │
                    ▼
2. DNS lookup: api.danalv.com
   └── Returns Cloudflare edge IP
                    │
                    ▼
3. TLS handshake with Cloudflare
                    │
                    ▼
4. Cloudflare connects to EC2 (HTTP :80)
                    │
                    ▼
5. Nginx receives request
   ├── Applies rate limiting
   └── Proxies to backend:8000
                    │
                    ▼
6. FastAPI receives request
   ├── CORS check (Origin: https://danalv.com)
   │   ├── NOT ALLOWED: Return CORS error
   │   └── ALLOWED: Continue
   ├── Check cache
   │   ├── HIT: Return cached entries
   │   └── MISS: Query database
   └── Query PostgreSQL
                    │
                    ▼
7. PostgreSQL returns entries
   └── Entries from last 24 hours
                    │
                    ▼
8. FastAPI formats response
   ├── Converts to Pydantic models
   ├── Caches result (30 min TTL)
   └── Returns JSON
                    │
                    ▼
9. Response travels back through stack
   └── Nginx → Cloudflare → Browser
                    │
                    ▼
10. Vue app renders digest cards
```

---

## Port Summary

| Service | Container Port | Host Port | Accessible From |
|---------|---------------|-----------|-----------------|
| Nginx | 80 | 80 | Internet (via Cloudflare) |
| Nginx | 443 | 443 | Internet (via Cloudflare) |
| FastAPI | 8000 | - | Docker network only |
| PostgreSQL | 5432 | - | Docker network only |
| Miniflux | 8080 | - | Docker network only (SSM port forward for admin) |

---

## Environment Variables Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              /opt/danalv-site/.env                                   │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   # Shared                                                                           │
│   POSTGRES_USER=miniflux                                                             │
│   POSTGRES_PASSWORD=<secret>                                                         │
│   POSTGRES_DB=miniflux                                                               │
│                                                                                      │
│   # Miniflux                                                                         │
│   MINIFLUX_ADMIN_USERNAME=admin                                                      │
│   MINIFLUX_ADMIN_PASSWORD=<secret>                                                   │
│                                                                                      │
│   # FastAPI                                                                          │
│   DATABASE_URL=postgresql://miniflux:<secret>@postgres:5432/miniflux                │
│   ENVIRONMENT=production                                                             │
│   CORS_ORIGINS=https://danalv.com                                                   │
│   CACHE_TTL=1800                                                                     │
│   CACHE_MAX_SIZE=10                                                                  │
│                                                                                      │
│   # ECR                                                                              │
│   AWS_ACCOUNT_ID=<account-id>                                                        │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Access Methods

| Resource | Method | Command |
|----------|--------|---------|
| EC2 Shell | SSM Session Manager | `aws ssm start-session --target <instance-id>` |
| Miniflux Admin | SSM Port Forward | `aws ssm start-session --target <instance-id> --document-name AWS-StartPortForwardingSessionToRemoteHost --parameters '{"host":["localhost"],"portNumber":["8080"],"localPortNumber":["8080"]}'` |
| Container Logs | SSM + Docker | `docker compose logs -f backend` |
| PostgreSQL | SSM + Docker | `docker exec -it daily-digest-postgres psql -U miniflux` |
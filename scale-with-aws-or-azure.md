# Scaling the Blog Platform Backend (AWS / Azure)

This document describes how to scale the FastAPI-based blog backend from a single-instance dev setup to a **highly available, horizontally scalable** deployment on **AWS** or **Azure**.

The focus is on:

- Stateless FastAPI app
- PostgreSQL as primary DB
- Real-time features (SSE, WebSockets)
- Caching and pub/sub
- Observability & security

---

## 1. Baseline Architecture (Current State)

Core components already implemented:

- **FastAPI app** (`app.main:app`)
  - JWT authentication
  - RBAC (user/admin/approver)
  - REST APIs (blogs, feature-requests, drafts)
  - Real-time:
    - **SSE**: `/api/notifications/sse`
    - **WebSockets**: `/api/blogs/{id}/ws`
- **SQLite** (dev) via SQLAlchemy
- **In-memory managers**:
  - SSE `NotificationManager`
  - WebSocket `BlogChatManager`
- **Pytest-based tests**
- **Swagger/OpenAPI** docs

To scale, we will:

1. Move to **PostgreSQL**.
2. Make the app **containerized and stateless**.
3. Introduce **Redis** for real-time pub/sub.
4. Deploy behind a **load balancer** with **horizontal scaling**.
5. Add **logging, monitoring, and secrets management**.

---

## 2. Core Scaling Principles

Regardless of cloud (AWS / Azure):

1. **Stateless app instances**
   - Authentication via JWT → no sticky sessions required.
   - No local filesystem state (use object storage for media if added later).

2. **Shared external state**
   - PostgreSQL for relational data.
   - Redis for:
     - Pub/Sub for WebSockets and SSE fan-out.
     - Optional caching.

3. **Horizontal scaling**
   - Multiple app instances behind a load balancer.
   - Auto-scaling based on CPU/RAM/request rate.

4. **Real-time awareness**
   - SSE and WebSockets must work across instances → use Redis pub/sub.

5. **Security and observability**
   - Secrets in Key Vault / Parameter Store.
   - Metrics, logs, and traces connected to cloud-native tools.

---

## 3. Scaling on AWS

### 3.1. Core Infrastructure

**Recommended AWS stack:**

- **Compute:**  
  - Option A: AWS ECS (Fargate)  
  - Option B: AWS EKS (Kubernetes)  
  - Option C: AWS App Runner (simpler PaaS-style)

- **Database:**  
  - Amazon RDS / Aurora PostgreSQL

- **Cache & Pub/Sub:**  
  - Amazon ElastiCache for Redis

- **Load Balancing & Routing:**  
  - Application Load Balancer (ALB)  
    - Must be configured to support WebSockets and long-lived HTTP (for SSE)

- **Static Assets / Media (future):**  
  - Amazon S3 + CloudFront

- **Secrets & Config:**  
  - AWS Systems Manager (SSM) Parameter Store  
  - AWS Secrets Manager (for DB password, JWT secret)

- **Monitoring & Logging:**  
  - CloudWatch Logs / Metrics  
  - X-Ray (optional) for tracing

---

### 3.2. App Layer (FastAPI)

1. **Containerize the app**
   - Create a `Dockerfile` for the FastAPI app.
   - Image runs: `uvicorn app.main:app --host 0.0.0.0 --port 8000`.

2. **Deploy the container**
   - Use ECS (Fargate) or App Runner for simplicity.
   - Define a task/service with:
     - Desired count: N instances (start with 2–3).
     - Auto-scaling: CPU or request-based scaling.

3. **Network**
   - Deploy app in a **VPC** with:
     - Public ALB
     - Private subnets for app tasks and DB.

---

### 3.3. Database: RDS PostgreSQL

- Migrate from SQLite → PostgreSQL.
- Create an **RDS PostgreSQL** instance in private subnets.
- Set `DATABASE_URL` like:
  ```env
  DATABASE_URL=postgresql+psycopg2://user:password@hostname:5432/dbname

- Use **Security Groups** to allow only app tasks to talk to the DB.

## 3.4. Real-Time: SSE & WebSockets at Scale

**Problem:** SSE + WebSockets with multiple instances require shared pub/sub.

**Solution:** Redis + ALB.

- Deploy **ElastiCache Redis**.
- Refactor:
  - **SSE `NotificationManager`** → publish events to Redis channel(s).
  - **WebSocket `BlogChatManager`** → use Redis pub/sub:
    - When a user sends a chat message, publish to:  
      `chat:blog:{id}`
    - All instances subscribe to this channel and broadcast to their local WebSocket clients.

**ALB configuration:**

- Target group protocol: **HTTP/HTTPS**.
- Supports persistent connections for **WebSocket** and **SSE**.
- Idle timeouts tuned higher (e.g., **60–120 seconds** or more depending on needs).

## 3.5. Security & Observability (AWS)

**Secrets:**

Store `SECRET_KEY`, DB credentials, etc. in:

- **AWS SSM Parameter Store**
- **AWS Secrets Manager**

**Logs:**

- Uvicorn/FastAPI logs → **CloudWatch Logs** (via ECS/App Runner integration).

**Metrics:**

- CloudWatch:
  - Request count
  - Latency
  - Error rate

**Scaling:**

- Auto Scaling Policies on **ECS Service**:
  - Target CPU (e.g., **60–70%**)
  - or **ALB `RequestCountPerTarget`**

---

## 4. Scaling on Azure

### 4.1. Core Infrastructure

**Recommended Azure stack:**

**Compute:**

- Azure App Service (**Web App for Containers**)  
- or **Azure Kubernetes Service (AKS)** for advanced setups

**Database:**

- **Azure Database for PostgreSQL (Flexible Server)**

**Cache & Pub/Sub:**

- **Azure Cache for Redis**

**Load Balancing & Routing:**

- **Azure Front Door** or **Azure Application Gateway**
- App Service built-in load balancing for simple setups

**Static Assets / Media (future):**

- **Azure Blob Storage** + **Azure CDN**

**Secrets & Config:**

- **Azure Key Vault**
- App Service **Application Settings**

**Monitoring & Logging:**

- **Azure Monitor** / **Application Insights**
- **Log Analytics**

---

### 4.2. App Layer (FastAPI on Azure)

Containerize the app (same Dockerfile as AWS).

**Option A: Azure App Service (easiest)**

- Deploy the container as a **Web App for Containers**.
- Configure:
  - `WEBSITE_WEBDEPLOY_USE_SCM=false` (if needed)
  - `WEBSITES_PORT=8000`
- Set env vars:
  - `DATABASE_URL`
  - `SECRET_KEY`
  - etc.

**Option B: AKS**

- Deploy container as a **Deployment + Service**.
- Use **Ingress** (NGINX/Azure Application Gateway) for HTTP/WS/SSE.

---

### 4.3. Database: Azure PostgreSQL

- Create **Azure Database for PostgreSQL (Flexible Server)**.
- Private **VNet** integration with App Service / AKS.
- Use connection string in `DATABASE_URL`.

---

### 4.4. Real-Time: SSE & WebSockets on Azure

Same pattern as AWS:

- Use **Azure Cache for Redis**:
  - Pub/Sub for WebSocket rooms & SSE.

In code:

- Replace in-memory managers with Redis-based pub/sub.

**App Service / AKS:**

- Ensure **WebSocket** is enabled at the App Service level.
- Ensure idle timeouts are set appropriately.

**Example text for README/discussion:**

> At scale, SSE and WebSocket fan-out are backed by Azure Cache for Redis, so any app instance can receive events and broadcast to connected clients.

---

### 4.5. Security & Observability (Azure)

- Store secrets in **Azure Key Vault**.
- Give App Service / AKS **managed identity** access to read secrets.

**Logs:**

- Forward `stdout` to **Log Analytics**.

**Monitoring / Metrics:**

- **Application Insights**:
  - Requests/sec
  - Latency
  - Error rate
  - WebSocket connection count (custom metric)

---

## 5. Horizontal Scaling Strategy

### 5.1. App Tier

**AWS:**

- ECS Service with auto-scaling
- or **App Runner**

**Azure:**

- App Service autoscale rules
- or **AKS HPA (Horizontal Pod Autoscaler)**

**Scale based on:**

- CPU usage
- Memory usage
- Request count
- Queue length

---

### 5.2. Database

- Scale **vertically** initially (bigger instance).
- Add **read replicas** for read-heavy endpoints (public blogs).
- Always **paginate** and avoid unbounded queries.

---

### 5.3. Cache

Use **Redis** to cache:

- Frequently accessed blogs
- Aggregated data (count of likes, comments, etc.)

Eviction strategy:

- **LRU**
- or **TTL-based**

---

## 6. Future Improvements (If Needed)

- Move real-time into a dedicated **“realtime service”** (if usage explodes).
- Add background workers (**Celery / RQ**) for heavy tasks:
  - Email notifications
  - Analytics aggregation
- Introduce a **service layer** (e.g., `BlogService`, `NotificationService`) for complex workflows.
- Add full **CI/CD**:
  - GitHub Actions
  - Azure DevOps
  - CodePipeline
- Automatic deployments to:
  - test → staging → prod

---

## 7. Summary

To scale this FastAPI backend to **millions of users** on **AWS or Azure**:

- Containerize the application and run multiple instances behind a load balancer.
- Switch to managed PostgreSQL (**RDS / Azure DB for PostgreSQL**).
- Use **Redis** (**ElastiCache / Azure Cache for Redis**) to handle:
  - pub/sub for WebSockets and SSE across instances
  - optional caching for hot content
- Use **JWT** + stateless app design to simplify horizontal scaling.
- Offload media to **S3 / Blob Storage** and use **CDN**.
- Add **monitoring, logging, and autoscaling** rules to react to traffic automatically.

This design lets the same backend codebase scale from a single dev box to a **multi-region, production-grade deployment** in AWS or Azure.

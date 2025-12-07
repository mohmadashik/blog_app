## 🚧 Intentional Omissions & Trade-offs

Some features were intentionally simplified or not implemented fully to keep the assignment focused on backend fundamentals, clarity, and maintainability. Below are the key decisions and why they were made:

### 1. No Separate Service Layer (API → CRUD Direct Call)
For this project, the business logic is straightforward (CRUD + simple workflows), so introducing a full service layer would add unnecessary complexity.  
In a production system with richer workflows or multiple entrypoints (API, CLI, workers), a service/use-case layer would be added.

### 2. Minimal Try/Except Usage
FastAPI already provides robust exception handling, and Pydantic handles validation errors.  
Explicit try/except blocks were added only where business logic required it (like 404/403 conditions).  
For DB and external integrations, a real system would include:
- transaction-level error handling  
- retries / circuit breakers  
- custom exception mapping  
These were intentionally left out to keep the example clean.

### 3. Logs Are Minimal
Uvicorn already logs access and errors to stdout.  
Production systems would include:
- structured JSON logs  
- domain-level event logging (approvals, rejects, failures)  
- log aggregation (ELK, Loki, CloudWatch, etc.)  
Since the assignment focuses on backend architecture, logs were kept minimal.

### 4. No Frontend Included
The requirement explicitly focused on backend behavior.  
All endpoints (REST + SSE + WebSockets) are frontend-ready and documented through Swagger/OpenAPI.  
A React frontend can be attached without modifying backend code.

### 5. Simple In-Memory Real-Time Managers
SSE and WebSocket managers use in-memory broadcast for simplicity.  
This is correct for a single-instance backend (local/dev).  
In real production:
- A Redis Pub/Sub layer would be used  
- Multiple FastAPI workers would subscribe to shared channels  
This was intentionally left out to avoid over-engineering.

### 6. No Dockerfile / Deployment Scripts (Optional)
Deployment instructions are documented, but automated containerization (Dockerfile, docker-compose) was not included because:
- The focus is backend implementation, not DevOps setup  
- It can be easily added if required  
If needed, a Dockerfile can be added in 5–10 minutes.

### 7. No Refresh Token Rotation or Session Invalidation
JWT access tokens are intentionally short-lived in this demo.  
A complete production auth system would add:
- refresh token rotation  
- forced logout / token invalidation logic  
- blacklist/whitelist patterns  
These were out of scope for the assignment.

### 8. Database Draft Storage Instead of Redis
Draft storage (for blog writing) uses a simple database model for clarity.  
Real-world systems may use Redis for:
- lower latency  
- expiration  
- session sharing between instances  
This was intentionally simplified.

---

## 🎯 Summary
Every omission above is deliberate.  
The solution focuses on **clarity, correctness, real-time features, testing, and clean modular design**, exactly matching the assignment requirements without unnecessary complexity.

# Blog Platform Backend (FastAPI + SQLite)

A modern, real-time backend for a blog platform built with **FastAPI**, **JWT Authentication**, **Role-Based Access Control (RBAC)**, **SSE Notifications**, **WebSocket Chat**, and **SQLAlchemy ORM**.  
Designed as an interview-ready case study demonstrating backend architecture, real-time features, modular design, and production readiness.

---

## 🚀 Features Overview

### **1. Authentication & Authorization**
- User registration and login using JWT access tokens  
- Secure password hashing using bcrypt  
- Roles:  
  - `user` → normal user  
  - `admin` → can approve blogs, update feature requests  
  - `approver` → can approve blogs  
- RBAC enforced via reusable FastAPI dependencies  

---

### **2. Blog Management**
- Users can create blog posts (default status: `pending`)
- Admin/Approver can:
  - Approve posts  
  - Reject posts  
- Public can view **approved** blogs only  
- Endpoint summary:
```
GET /api/blogs/
POST /api/blogs/
GET /api/blogs/{id}
PUT /api/blogs/{id}
DELETE /api/blogs/{id}
POST /api/blogs/{id}/approve
POST /api/blogs/{id}/reject
GET /api/blogs/pending (admin/approver only)
```


---

### **3. Real-Time Features**
#### **Server-Sent Events (SSE)**
Admins receive live notifications when a new blog is submitted for approval.

Endpoint:
```GET /api/notifications/sse```


Internally uses:
- Async generator
- In-memory notification manager
- Keep-alive pings to maintain connection

#### **WebSocket Chat**
Real-time chat per blog.

Endpoint:
```WS /api/blogs/{id}/ws?token=<JWT>```


Features:
- JWT-based authentication (via query param)
- Broadcast messages to all users connected to the same blog
- Lightweight in-memory connection manager

---

### **4. Feature Requests**
Users can submit new feature requests.

Admins/Approvers can change their status:
- `pending`
- `accepted`
- `declined`

Endpoints:
```
GET /api/feature-requests/
POST /api/feature-requests/
PATCH /api/feature-requests/{id}
```

---

### **5. Draft Session Storage**
Users can save blog drafts and continue later.

Endpoints:
```
GET /api/session/draft
POST /api/session/draft
```

Implementation:
- Simple `Draft` model per user  
- Stored in DB (interview-friendly and simple)  
- Mentioned in README for future Redis support  

---

## 🧱 Project Structure
```
app/
│
├── api/ # Request handlers (routes)
│ ├── auth.py
│ ├── blogs.py
│ ├── feature_requests.py
│ ├── notifications.py
│ ├── session.py
│ └── init.py
│
├── core/
│ ├── config.py # Settings / environment
│ └── security.py # JWT, hashing
│
├── crud/ # DB operations
│ ├── blog.py
│ ├── draft.py
│ ├── feature_request.py
│ └── init.py
│
├── db/
│ ├── session.py # DB engine + session
│ └── init.py
│
├── deps.py # Reusable dependencies (RBAC, user lookup)
│
├── model/ # SQLAlchemy models
│ ├── user.py
│ ├── blog.py
│ ├── draft.py
│ ├── feature_request.py
│ └── init.py
│
├── schemas/ # Pydantic models
│ ├── user.py
│ ├── blog.py
│ ├── draft.py
│ ├── feature_request.py
│ └── init.py
│
├── services/ # Real-time services
│ ├── chat.py
│ ├── notifications.py
│ └── init.py
│
└── main.py # App initialization
```


---

## ⚙️ Setup & Running Locally

### **1. Install dependencies**
```
pip install -r requirements.txt
```

### **2. Run the application**
```
uvicorn app.main:app --reload
```

### **3. Access API docs**
- Swagger UI: http://localhost:8020/docs  
- ReDoc: http://localhost:8020/redoc  

### **4. Environment Configuration**
Configuration is handled in `core/config.py`.

Typical `.env`:
```
SECRET_KEY="supersecret"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL="sqlite:///./dev.db"
```

---

## 🔐 Authentication Workflow

1. Register → `/api/auth/register`
2. Login → `/api/auth/login`
3. Use returned `access_token`:
Authorization: Bearer <token>


Role promotion (admin-only ops):
POST /api/auth/make-admin/{username}


---

## ✍️ Blog Workflow

1. User submits blog → `pending`
2. Admin/Approver sees it in:
```GET /api/blogs/pending```

3. Approve:
```POST /api/blogs/{id}/approve```

4. Then it appears publicly in:
```GET /api/blogs/```


---

## 🔔 SSE Real-Time Notifications (Admin)

```GET /api/notifications/sse```


Client example (curl):

```bash
curl -N -H "Accept: text/event-stream" \
     -H "Authorization: Bearer <ADMIN_TOKEN>" \
     http://localhost:8020/api/notifications/sse
```
Event format:
```
data: {"type":"blog_pending","blog_id":5,"title":"New Blog","author_id":2}
```
💬 WebSocket Chat Per Blog
```
ws://localhost:8020/api/blogs/{id}/ws?token=<JWT>
```
Example (wscat):
```
wscat -c "ws://localhost:8020/api/blogs/1/ws?token=XYZ"
```
Messages are broadcast to everyone connected to that blog.

🧪 Testing
Run tests:

```
python -m pytest
```
Tests include:

- Auth tests (register + login)

- Blog creation & approval workflow

- Pending visibility checks

- The test suite uses:

- Separate SQLite test DB

- FastAPI TestClient

- Dependency overrides for DB

📦 Production Readiness Notes
For real deployments:

- Run under Gunicorn + Uvicorn workers

- Reverse proxy with Nginx or Caddy

- HTTPS via Let's Encrypt

- Set environment variables for secrets (never hardcode)

- Use PostgreSQL instead of SQLite

- For multi-instance deployments:

- Use Redis for WebSocket pub/sub

- Use Redis or DB-backed SSE broadcaster

- CORS restricted to your frontend domain



📝 License
MIT — For interview/demo purposes.

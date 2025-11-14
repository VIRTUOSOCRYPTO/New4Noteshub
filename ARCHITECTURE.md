# NotesHub Architecture Documentation

## System Overview

NotesHub is a full-stack note-sharing platform built with modern web technologies, designed for scalability, maintainability, and performance.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          React + TypeScript + Tailwind CSS          │  │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │  │
│  │  │   Pages    │  │ Components │  │    Hooks     │  │  │
│  │  └────────────┘  └────────────┘  └──────────────┘  │  │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │  │
│  │  │  Services  │  │   State    │  │   Routing    │  │  │
│  │  └────────────┘  └────────────┘  └──────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway/NGINX                       │
│              (Load Balancing, Rate Limiting)                 │
└─────────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────────┐
│                         Backend                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              FastAPI + Python 3.9+                  │  │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │  │
│  │  │  Routers   │→ │  Services  │→ │ Repositories │  │  │
│  │  └────────────┘  └────────────┘  └──────────────┘  │  │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │  │
│  │  │ Middleware │  │   Models   │  │  Validators  │  │  │
│  │  └────────────┘  └────────────┘  └──────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │  MongoDB    │  │  Redis      │  │  File Storage   │    │
│  │  (Primary)  │  │  (Cache)    │  │  (S3/Local)     │    │
│  └─────────────┘  └─────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────────┐
│                   External Services                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │   Resend    │  │   Sentry    │  │    ClamAV       │    │
│  │   (Email)   │  │ (Monitoring)│  │ (Virus Scan)    │    │
│  └─────────────┘  └─────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Query (TanStack Query)
- **Routing**: Wouter
- **Build Tool**: Vite
- **Testing**: Vitest, React Testing Library, Playwright

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **Database**: MongoDB
- **Caching**: Redis (optional)
- **Authentication**: JWT
- **File Upload**: Multipart form data
- **Testing**: Pytest

### Infrastructure
- **Web Server**: NGINX
- **Process Manager**: Supervisor
- **Container**: Docker
- **Monitoring**: Sentry
- **Email**: Resend
- **Security**: ClamAV (virus scanning)

## Backend Architecture

### Layered Architecture

```
┌──────────────────────────────────────────────────┐
│                 Presentation Layer                │
│              (Routers/Endpoints)                 │
│  - Handle HTTP requests/responses                │
│  - Input validation (Pydantic)                   │
│  - Authentication/Authorization                   │
└──────────────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────┐
│                 Business Layer                    │
│                  (Services)                       │
│  - Business logic implementation                 │
│  - Data transformation                            │
│  - Orchestration of operations                   │
└──────────────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────┐
│                 Data Access Layer                 │
│               (Repositories)                      │
│  - Database queries                               │
│  - Data persistence                               │
│  - Cache management                               │
└──────────────────────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────┐
│                  Data Layer                       │
│                 (MongoDB)                         │
│  - Persistent storage                             │
│  - Indexing                                       │
│  - Replication                                    │
└──────────────────────────────────────────────────┘
```

### Directory Structure

```
backend/
├── routers/              # API endpoints
│   ├── __init__.py
│   ├── auth.py          # Authentication routes
│   ├── notes.py         # Notes CRUD routes
│   ├── users.py         # User management routes
│   ├── analytics.py     # Analytics endpoints
│   ├── admin.py         # Admin endpoints
│   └── search.py        # Search endpoints
│
├── services/            # Business logic
│   ├── __init__.py
│   ├── note_service.py
│   ├── user_service.py
│   ├── analytics_service.py
│   ├── search_service.py
│   ├── email_verification.py
│   ├── backup_service.py
│   ├── feature_flags.py
│   ├── ab_testing.py
│   ├── virus_scanner.py
│   ├── log_aggregation.py
│   └── performance_monitoring.py
│
├── middleware/          # Custom middleware
│   ├── __init__.py
│   ├── admin_auth.py   # Admin authorization
│   ├── rate_limit.py   # Rate limiting
│   └── logging.py      # Request logging
│
├── models.py           # Pydantic models
├── database.py         # Database connection
├── auth.py             # Authentication utilities
├── server.py           # Main application
└── requirements.txt    # Python dependencies
```

### API Design

#### RESTful Principles
- Use HTTP methods correctly (GET, POST, PUT, DELETE)
- Resource-based URLs (`/api/notes`, `/api/users`)
- Stateless communication
- Standard HTTP status codes

#### API Versioning Strategy
```
/api/v1/notes      # Version 1
/api/v2/notes      # Version 2 (with breaking changes)
/api/notes         # Latest stable version (alias)
```

**Versioning Rules**:
1. **No version** = Latest stable
2. **v1, v2, etc.** = Specific versions
3. Support at least 2 versions concurrently
4. Deprecation notice: 6 months before removal

#### Response Format

**Success Response**:
```json
{
  "data": {...},
  "meta": {
    "timestamp": "2025-01-15T10:30:00Z",
    "version": "1.0.0"
  }
}
```

**Error Response**:
```json
{
  "error": {
    "code": "NOTE_NOT_FOUND",
    "message": "Note with ID 123 not found",
    "details": {...},
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

### Authentication Flow

```
┌──────┐                                        ┌──────────┐
│Client│                                        │  Server  │
└───┬──┘                                        └────┬─────┘
    │                                                │
    │  1. POST /api/auth/register                   │
    │  {email, password, ...}                       │
    ├──────────────────────────────────────────────>│
    │                                                │
    │  2. Create user + Send verification email     │
    │  Return access_token + refresh_token          │
    │<──────────────────────────────────────────────┤
    │                                                │
    │  3. Store tokens in memory/localStorage       │
    │                                                │
    │  4. GET /api/notes                            │
    │  Header: Authorization: Bearer <access_token> │
    ├──────────────────────────────────────────────>│
    │                                                │
    │  5. Validate token                            │
    │  Return notes                                  │
    │<──────────────────────────────────────────────┤
    │                                                │
    │  6. POST /api/auth/refresh                    │
    │  {refresh_token}                              │
    ├──────────────────────────────────────────────>│
    │                                                │
    │  7. Return new access_token                   │
    │<──────────────────────────────────────────────┤
```

## Frontend Architecture

### Component Hierarchy

```
App
├── AuthProvider
│   └── ThemeProvider
│       ├── Header
│       │   ├── Logo
│       │   ├── Navigation
│       │   └── UserMenu
│       │
│       ├── Router
│       │   ├── Home
│       │   ├── Upload
│       │   │   ├── FileUpload
│       │   │   └── UploadForm
│       │   ├── FindNotes
│       │   │   ├── SearchBar
│       │   │   ├── Filters
│       │   │   └── NotesList
│       │   │       └── NoteCard
│       │   ├── Profile
│       │   ├── Analytics
│       │   │   ├── DashboardStats
│       │   │   ├── Charts
│       │   │   └── Tables
│       │   └── Settings
│       │
│       └── Footer
│
└── Toaster (Global notifications)
```

### State Management

```
┌─────────────────────────────────────────────┐
│         React Query (Server State)          │
│  - API data caching                         │
│  - Automatic refetching                     │
│  - Optimistic updates                       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│      React Context (Global State)           │
│  - Authentication state                     │
│  - Theme preferences                        │
│  - User settings                            │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│     useState/useReducer (Local State)       │
│  - Form inputs                              │
│  - UI state (modals, dropdowns)            │
│  - Component-specific data                  │
└─────────────────────────────────────────────┘
```

### Data Flow

```
User Action → Event Handler → Service Function → API Call
                                                      ↓
                                                 Response
                                                      ↓
UI Update ← State Update ← React Query Cache Update ←┘
```

## Database Design

### Collections

#### Users Collection
```javascript
{
  _id: ObjectId,
  email: String (unique, indexed),
  password: String (hashed),
  name: String,
  department: String,
  year: Number,
  usn: String (unique),
  role: String ("user" | "admin"),
  isEmailVerified: Boolean,
  emailVerificationToken: String,
  twoFactorEnabled: Boolean,
  twoFactorSecret: String,
  profileImage: String,
  createdAt: Date,
  updatedAt: Date
}
```

#### Notes Collection
```javascript
{
  _id: ObjectId,
  title: String (indexed),
  subject: String (indexed),
  department: String (indexed),
  year: Number,
  userId: ObjectId (ref: Users),
  usn: String,
  filename: String,
  originalFilename: String,
  fileSize: Number,
  uploadedAt: Date (indexed),
  viewCount: Number,
  downloadCount: Number,
  isFlagged: Boolean,
  flagReason: String,
  flaggedBy: ObjectId,
  flaggedAt: Date,
  isApproved: Boolean,
  tags: [String]
}
```

#### Feature Flags Collection
```javascript
{
  _id: ObjectId,
  name: String (unique),
  description: String,
  status: String ("enabled" | "disabled" | "percentage"),
  rolloutPercentage: Number,
  targetUsers: [ObjectId],
  createdAt: Date,
  updatedAt: Date
}
```

### Indexing Strategy

```javascript
// Users
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ usn: 1 }, { unique: true })
db.users.createIndex({ department: 1, year: 1 })

// Notes
db.notes.createIndex({ title: "text", subject: "text" })
db.notes.createIndex({ department: 1, subject: 1 })
db.notes.createIndex({ uploadedAt: -1 })
db.notes.createIndex({ userId: 1 })
db.notes.createIndex({ viewCount: -1, downloadCount: -1 })
```

## Security Architecture

### Authentication & Authorization

```
┌─────────────────────────────────────────┐
│         Security Layers                  │
├─────────────────────────────────────────┤
│ 1. Rate Limiting (SlowAPI)              │
│    - 100 requests/minute per IP         │
│    - Stricter limits for auth endpoints │
├─────────────────────────────────────────┤
│ 2. CORS (FastAPI Middleware)            │
│    - Allowed origins whitelist          │
│    - Credentials support                │
├─────────────────────────────────────────┤
│ 3. JWT Authentication                    │
│    - Access tokens (15 min)             │
│    - Refresh tokens (7 days)            │
├─────────────────────────────────────────┤
│ 4. Role-Based Access Control            │
│    - User role                           │
│    - Admin role                          │
├─────────────────────────────────────────┤
│ 5. Input Validation (Pydantic)          │
│    - Type checking                       │
│    - Custom validators                   │
├─────────────────────────────────────────┤
│ 6. File Upload Security                  │
│    - File type validation                │
│    - Size limits                         │
│    - Virus scanning (ClamAV)            │
├─────────────────────────────────────────┤
│ 7. Password Security                     │
│    - Bcrypt hashing                      │
│    - Minimum 8 characters                │
│    - Optional 2FA                        │
└─────────────────────────────────────────┘
```

### File Upload Security

```
File Upload → Validation → Virus Scan → Storage → Database Record
                  │              │
                Reject        Quarantine
```

## Performance Optimization

### Backend
1. **Database Query Optimization**
   - Use indexes for frequent queries
   - Limit result sets
   - Use projections to fetch only needed fields

2. **Caching Strategy**
   - Redis for session data
   - Query result caching
   - CDN for static assets

3. **Connection Pooling**
   - MongoDB connection pool
   - Reuse database connections

### Frontend
1. **Code Splitting**
   - Lazy loading routes
   - Dynamic imports for heavy components

2. **Asset Optimization**
   - Image compression
   - Minification
   - Gzip compression

3. **React Query Caching**
   - Stale-while-revalidate strategy
   - Background refetching
   - Optimistic updates

## Monitoring & Observability

### Metrics Tracked

```
┌─────────────────────────────────────────┐
│         Application Metrics              │
├─────────────────────────────────────────┤
│ - Request rate (req/sec)                │
│ - Response time (p50, p95, p99)         │
│ - Error rate (%)                         │
│ - Active users                           │
│ - Database query time                    │
│ - Upload success rate                    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Infrastructure Metrics           │
├─────────────────────────────────────────┤
│ - CPU usage                              │
│ - Memory usage                           │
│ - Disk I/O                              │
│ - Network throughput                     │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         Business Metrics                 │
├─────────────────────────────────────────┤
│ - Daily active users                     │
│ - Notes uploaded per day                │
│ - Download rate                          │
│ - User retention                         │
└─────────────────────────────────────────┘
```

### Logging Strategy

```
logs/
├── app.log              # Application logs
├── error.log            # Error logs
├── security.log         # Security events
└── performance.log      # Performance metrics
```

## Deployment Architecture

### Production Deployment

```
┌─────────────────────────────────────────┐
│         Load Balancer (NGINX)           │
└────────────┬────────────────────────────┘
             │
     ┌───────┴───────┐
     │               │
┌────▼────┐    ┌────▼────┐
│ Backend │    │ Backend │
│ Server 1│    │ Server 2│
└────┬────┘    └────┬────┘
     │               │
     └───────┬───────┘
             │
    ┌────────▼─────────┐
    │   MongoDB        │
    │   Replica Set    │
    │  (3 nodes)       │
    └──────────────────┘
```

### Rollback Strategy

```
1. Tag releases: v1.0.0, v1.0.1, etc.
2. Keep previous 3 versions deployed
3. Blue-green deployment:
   - Deploy to "green" environment
   - Run health checks
   - Switch traffic from "blue" to "green"
   - Keep "blue" for quick rollback
4. Database migrations:
   - Always backward compatible
   - Use migration scripts
   - Keep rollback scripts ready
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "version": "1.0.0",
        "timestamp": datetime.utcnow()
    }
```

## Scalability Considerations

### Horizontal Scaling
- Multiple backend instances behind load balancer
- Stateless API design
- Session data in Redis

### Database Scaling
- MongoDB replica sets for read scaling
- Sharding for write scaling
- Separate analytics database

### CDN Integration
- Static assets served from CDN
- File downloads through CDN
- Edge caching for common queries

## Future Enhancements

1. **Microservices Architecture**
   - Split into separate services (auth, notes, analytics)
   - API gateway for routing
   - Service mesh for communication

2. **Event-Driven Architecture**
   - Message queue (RabbitMQ/Kafka)
   - Async processing
   - Event sourcing

3. **Advanced Analytics**
   - Machine learning recommendations
   - Predictive analytics
   - Real-time dashboards

4. **Mobile Apps**
   - React Native apps
   - Push notifications
   - Offline support

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [MongoDB Best Practices](https://www.mongodb.com/docs/manual/administration/production-notes/)
- [System Design Primer](https://github.com/donnemartin/system-design-primer)

---

**Last Updated**: January 2025
**Version**: 1.0.0

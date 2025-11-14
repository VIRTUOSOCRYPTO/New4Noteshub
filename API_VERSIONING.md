# API Versioning Strategy

## Overview

NotesHub API uses URL-based versioning to manage API changes and ensure backward compatibility for clients.

## Versioning Scheme

### URL Structure
```
https://api.noteshub.com/api/v{version}/{resource}
```

### Examples
```
/api/v1/notes          # Version 1 (Stable)
/api/v2/notes          # Version 2 (Latest)
/api/notes             # Alias to latest stable version
```

## Version Lifecycle

```
Development → Beta → Stable → Deprecated → Sunset
    ↓           ↓        ↓          ↓           ↓
  Internal   Selected  Public   Supported   Removed
              Users     Use    (6 months)  (No access)
```

### Stage Definitions

1. **Development** (Internal only)
   - Active development
   - Breaking changes allowed
   - Not accessible to public

2. **Beta** (`/api/beta/...`)
   - Feature complete
   - Open to selected users
   - May have minor changes
   - No SLA guarantee

3. **Stable** (`/api/v1/...`)
   - Production ready
   - Full SLA support
   - Only backward-compatible changes
   - Supported for minimum 12 months

4. **Deprecated** (marked in docs)
   - Functionality maintained
   - No new features
   - 6-month sunset warning
   - Migration guide provided

5. **Sunset** (removed)
   - API no longer accessible
   - Returns 410 Gone status
   - Redirect to latest version

## Versioning Rules

### When to Create a New Version

Create a new major version when:
- ✅ Removing an endpoint
- ✅ Removing a field from response
- ✅ Changing field data types
- ✅ Changing authentication method
- ✅ Modifying required parameters
- ✅ Changing error response format

### Backward Compatible Changes (No version bump)

- ✅ Adding new endpoints
- ✅ Adding optional parameters
- ✅ Adding new fields to responses
- ✅ Making required parameters optional
- ✅ Bug fixes
- ✅ Performance improvements

## Implementation

### Backend Structure

```python
# routers/v1/notes.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["notes-v1"])

@router.get("/notes")
async def get_notes_v1():
    return {"version": "1.0", "notes": [...]}
```

```python
# routers/v2/notes.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/v2", tags=["notes-v2"])

@router.get("/notes")
async def get_notes_v2():
    return {
        "version": "2.0",
        "data": [...],
        "meta": {...}
    }
```

```python
# server.py
from routers.v1 import notes as notes_v1
from routers.v2 import notes as notes_v2

app.include_router(notes_v1.router)
app.include_router(notes_v2.router)

# Alias for latest version
app.include_router(notes_v2.router, prefix="/api")
```

### Version Headers

All responses include version information:

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-API-Version: 2.0
X-API-Deprecation: false

{
  "data": {...},
  "meta": {
    "version": "2.0",
    "deprecated": false
  }
}
```

### Deprecation Warnings

When using deprecated version:

```http
HTTP/1.1 200 OK
X-API-Version: 1.0
X-API-Deprecation: true
X-API-Sunset-Date: 2025-12-31
Warning: 299 - "API version 1.0 is deprecated and will be sunset on 2025-12-31. Please migrate to v2."

{
  "data": {...},
  "meta": {
    "version": "1.0",
    "deprecated": true,
    "sunset_date": "2025-12-31",
    "migration_guide": "https://docs.noteshub.com/migration/v1-to-v2"
  }
}
```

## Migration Guide Template

### Migration from v1 to v2

#### Breaking Changes

1. **Response Format Changed**
   ```json
   // v1
   {
     "notes": [...]
   }
   
   // v2
   {
     "data": [...],
     "meta": {...}
   }
   ```

2. **Authentication Header**
   ```
   v1: X-Auth-Token: <token>
   v2: Authorization: Bearer <token>
   ```

3. **Error Response Format**
   ```json
   // v1
   {
     "error": "Note not found"
   }
   
   // v2
   {
     "error": {
       "code": "NOTE_NOT_FOUND",
       "message": "Note not found",
       "details": {...}
     }
   }
   ```

#### New Features in v2

- Pagination support
- Advanced filtering
- Batch operations
- Webhooks

#### Migration Steps

1. Update API base URL from `/api/v1` to `/api/v2`
2. Update authentication to use Bearer tokens
3. Update response parsing to use `data` instead of direct response
4. Update error handling for new error format
5. Test thoroughly in staging environment
6. Deploy to production

## Version Support Policy

### Current Versions

| Version | Status | Release Date | Deprecation Date | Sunset Date |
|---------|--------|--------------|------------------|-------------|
| v2      | Stable | 2025-01-01  | -                | -           |
| v1      | Stable | 2024-01-01  | -                | -           |

### Support Timeline

```
v1: ████████████████████████ (Stable until v3 release)
v2: ████████████████████████████████ (Current)
v3:                         ████████ (Beta)

    2024        2025        2026
```

## Client Implementation

### JavaScript/TypeScript

```typescript
import axios from 'axios';

const API_VERSION = 'v2';
const BASE_URL = `https://api.noteshub.com/api/${API_VERSION}`;

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Accept': 'application/json',
    'X-Client-Version': '1.0.0'
  }
});

// Intercept responses to check for deprecation warnings
apiClient.interceptors.response.use(
  (response) => {
    if (response.headers['x-api-deprecation'] === 'true') {
      console.warn(
        `API version ${API_VERSION} is deprecated. ` +
        `Sunset date: ${response.headers['x-api-sunset-date']}`
      );
    }
    return response;
  }
);
```

### Python

```python
import requests
import warnings

API_VERSION = 'v2'
BASE_URL = f'https://api.noteshub.com/api/{API_VERSION}'

class APIClient:
    def __init__(self, version='v2'):
        self.base_url = f'https://api.noteshub.com/api/{version}'
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'X-Client-Version': '1.0.0'
        })
    
    def request(self, method, endpoint, **kwargs):
        response = self.session.request(
            method,
            f'{self.base_url}{endpoint}',
            **kwargs
        )
        
        # Check for deprecation
        if response.headers.get('X-API-Deprecation') == 'true':
            sunset_date = response.headers.get('X-API-Sunset-Date')
            warnings.warn(
                f'API version is deprecated. Sunset: {sunset_date}',
                DeprecationWarning
            )
        
        return response.json()
```

## Testing Different Versions

```bash
# Test v1
curl -H "Accept: application/json" \
     https://api.noteshub.com/api/v1/notes

# Test v2
curl -H "Accept: application/json" \
     https://api.noteshub.com/api/v2/notes

# Test latest (alias to stable)
curl -H "Accept: application/json" \
     https://api.noteshub.com/api/notes
```

## Documentation Strategy

### Versioned Documentation

```
docs/
├── api/
│   ├── v1/
│   │   ├── overview.md
│   │   ├── authentication.md
│   │   ├── notes.md
│   │   └── users.md
│   ├── v2/
│   │   ├── overview.md
│   │   ├── authentication.md
│   │   ├── notes.md
│   │   └── users.md
│   └── migration/
│       └── v1-to-v2.md
```

### Documentation URLs

- Latest: `https://docs.noteshub.com/api/`
- v2: `https://docs.noteshub.com/api/v2/`
- v1: `https://docs.noteshub.com/api/v1/`

## Monitoring Version Usage

```python
# Middleware to track version usage
from fastapi import Request
import logging

@app.middleware("http")
async def log_version_usage(request: Request, call_next):
    # Extract version from path
    version = extract_version(request.url.path)
    
    # Log version usage
    logger.info(f"API {version} called: {request.url.path}")
    
    # Track in analytics
    analytics.track_version_usage(version, request.url.path)
    
    response = await call_next(request)
    response.headers["X-API-Version"] = version
    
    return response
```

## Best Practices

### For API Developers

1. ✅ Always increment version for breaking changes
2. ✅ Maintain at least 2 versions simultaneously
3. ✅ Provide migration guides
4. ✅ Give 6-month deprecation notice
5. ✅ Monitor version usage before sunset
6. ✅ Test backward compatibility
7. ✅ Document all changes in changelog

### For API Consumers

1. ✅ Always specify version in requests
2. ✅ Monitor deprecation headers
3. ✅ Subscribe to API changelog
4. ✅ Test new versions early
5. ✅ Have migration plan ready
6. ✅ Don't use unversioned endpoints in production
7. ✅ Implement version monitoring

## Change Log Format

### CHANGELOG.md

```markdown
# API Changelog

## [v2.0.0] - 2025-01-01

### Added
- Pagination support for all list endpoints
- Batch operations for notes
- Webhook support

### Changed
- Response format now includes `data` and `meta` objects
- Authentication uses Bearer tokens instead of custom header
- Error responses now include error codes

### Deprecated
- None

### Removed
- None

### Fixed
- Fixed timezone issues in date fields

### Security
- Improved rate limiting

## [v1.0.0] - 2024-01-01

Initial stable release
```

---

**Questions?** Contact api-support@noteshub.com
**Last Updated**: January 2025

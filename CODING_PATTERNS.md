# Coding Patterns & Standards

## Overview

This document defines standard patterns and conventions for NotesHub codebase to ensure consistency and maintainability.

## Table of Contents

- [Backend Patterns](#backend-patterns)
- [Frontend Patterns](#frontend-patterns)
- [Naming Conventions](#naming-conventions)
- [Error Handling](#error-handling)
- [API Patterns](#api-patterns)
- [State Management](#state-management)
- [Testing Patterns](#testing-patterns)

## Backend Patterns

### 1. Layered Architecture Pattern

**Always follow the three-layer architecture:**

```python
# ❌ BAD: Business logic in route
@router.post("/notes")
async def create_note(title: str, database=Depends(get_database)):
    note = {"title": title, "created_at": datetime.utcnow()}
    result = await database.notes.insert_one(note)
    return {"id": str(result.inserted_id)}

# ✅ GOOD: Route delegates to service
@router.post("/notes")
async def create_note(
    title: str,
    note_service: NoteService = Depends(get_note_service)
):
    note = await note_service.create_note({"title": title})
    return serialize_doc(note)
```

**Layer Responsibilities:**

```python
# Router Layer (routers/notes.py)
# - Handle HTTP requests/responses
# - Validate input (Pydantic)
# - Call service layer
# - NO business logic

@router.post("/notes")
async def create_note(
    data: NoteCreate,
    user_id: str = Depends(get_current_user_id),
    service: NoteService = Depends(get_note_service)
):
    note = await service.create_note(data.dict(), user_id)
    return serialize_doc(note)

# Service Layer (services/note_service.py)
# - Business logic
# - Data transformation
# - Coordinate between repositories
# - Transaction management

class NoteService:
    def __init__(self, database):
        self.repository = get_note_repository(database)
        self.file_service = get_file_service()
    
    async def create_note(self, note_data: dict, user_id: str) -> dict:
        # Business logic here
        validated_data = self._validate_note(note_data)
        note = await self.repository.create(validated_data)
        return note

# Repository Layer (repositories/note_repository.py)
# - Database operations only
# - CRUD operations
# - Query building
# - NO business logic

class NoteRepository:
    def __init__(self, database):
        self.collection = database.notes
    
    async def create(self, note_data: dict) -> dict:
        result = await self.collection.insert_one(note_data)
        note_data["_id"] = result.inserted_id
        return note_data
```

### 2. Dependency Injection Pattern

```python
# ❌ BAD: Hardcoded dependencies
class NoteService:
    def __init__(self):
        self.db = get_database()  # Hard dependency

# ✅ GOOD: Injected dependencies
class NoteService:
    def __init__(self, database):
        self.db = database
        self.repository = get_note_repository(database)

# Usage in FastAPI
def get_note_service(database=Depends(get_database)) -> NoteService:
    return NoteService(database)

@router.get("/notes")
async def get_notes(service: NoteService = Depends(get_note_service)):
    return await service.get_notes()
```

### 3. Exception Handling Pattern

```python
# ❌ BAD: Generic exceptions
if not note:
    raise Exception("Note not found")

# ✅ GOOD: Custom typed exceptions
from exceptions import NotFoundError

if not note:
    raise NotFoundError("Note", note_id)

# Service layer
class NoteService:
    async def get_note(self, note_id: str):
        note = await self.repository.find_by_id(note_id)
        if not note:
            raise NotFoundError("Note", note_id)
        return note

# Router handles conversion
@router.get("/notes/{note_id}")
async def get_note(note_id: str, service: NoteService = Depends()):
    try:
        note = await service.get_note(note_id)
        return serialize_doc(note)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

### 4. Repository Pattern

```python
# ✅ Repository for data access
class NoteRepository:
    def __init__(self, database):
        self.collection = database.notes
    
    async def find_by_id(self, note_id: str) -> Optional[dict]:
        return await self.collection.find_one({"_id": ObjectId(note_id)})
    
    async def find_many(self, query: dict, skip: int = 0, limit: int = 100):
        cursor = self.collection.find(query).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def create(self, data: dict) -> dict:
        result = await self.collection.insert_one(data)
        data["_id"] = result.inserted_id
        return data
```

## Frontend Patterns

### 1. Component Structure Pattern

```typescript
// ❌ BAD: Large component with mixed concerns
export function NotesPage() {
    const [notes, setNotes] = useState([]);
    const [loading, setLoading] = useState(false);
    // ... 500 lines of code
}

// ✅ GOOD: Split into smaller components
// pages/Notes.tsx
export function NotesPage() {
    return (
        <div>
            <NotesHeader />
            <NotesFilters />
            <NotesList />
        </div>
    );
}

// components/NotesList.tsx
export function NotesList() {
    const { data, isLoading } = useNotes();
    
    if (isLoading) return <LoadingSpinner />;
    
    return (
        <div>
            {data.map(note => <NoteCard key={note.id} note={note} />)}
        </div>
    );
}
```

### 2. Custom Hooks Pattern

```typescript
// ❌ BAD: Duplicate data fetching logic
function ComponentA() {
    const [notes, setNotes] = useState([]);
    
    useEffect(() => {
        fetch('/api/notes')
            .then(res => res.json())
            .then(setNotes);
    }, []);
}

// ✅ GOOD: Reusable hook
// hooks/use-notes.ts
export function useNotes(filters?: NoteFilters) {
    return useQuery({
        queryKey: ['notes', filters],
        queryFn: () => fetchNotes(filters)
    });
}

// Usage
function ComponentA() {
    const { data: notes, isLoading } = useNotes();
    // ...
}
```

### 3. Service Layer Pattern

```typescript
// ❌ BAD: API calls directly in components
function NotesPage() {
    const fetchNotes = async () => {
        const response = await fetch(`${BACKEND_URL}/api/notes`);
        const data = await response.json();
        setNotes(data);
    };
}

// ✅ GOOD: Service layer
// services/note-service.ts
export const noteService = {
    async getNotes(filters?: NoteFilters): Promise<Note[]> {
        const params = new URLSearchParams(filters);
        const response = await fetch(`${BACKEND_URL}/api/notes?${params}`);
        if (!response.ok) throw new Error('Failed to fetch notes');
        return response.json();
    },
    
    async createNote(note: NoteCreate): Promise<Note> {
        const response = await fetch(`${BACKEND_URL}/api/notes`, {
            method: 'POST',
            body: JSON.stringify(note)
        });
        if (!response.ok) throw new Error('Failed to create note');
        return response.json();
    }
};

// Usage in component
const { data } = useQuery({
    queryKey: ['notes'],
    queryFn: () => noteService.getNotes()
});
```

### 4. Props Interface Pattern

```typescript
// ❌ BAD: Inline types
function NoteCard({ note }: { note: any }) {
    // ...
}

// ✅ GOOD: Explicit interface
interface NoteCardProps {
    note: Note;
    onDelete?: (id: string) => void;
    onEdit?: (note: Note) => void;
    className?: string;
}

export function NoteCard({
    note,
    onDelete,
    onEdit,
    className
}: NoteCardProps) {
    // ...
}
```

## Naming Conventions

### Backend (Python)

```python
# Classes: PascalCase
class NoteService:
    pass

class NoteRepository:
    pass

# Functions/methods: snake_case
async def get_note_by_id(note_id: str):
    pass

async def create_note(note_data: dict):
    pass

# Constants: UPPER_SNAKE_CASE
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.pdf', '.doc'}

# Private methods: leading underscore
class NoteService:
    def _validate_note(self, note_data):
        pass

# Variables: snake_case
note_count = 10
user_id = "123"
```

### Frontend (TypeScript)

```typescript
// Components: PascalCase
export function NoteCard() {}
export function UserProfile() {}

// Hooks: camelCase with 'use' prefix
export function useNotes() {}
export function useAuth() {}

// Functions: camelCase
function formatDate(date: Date) {}
async function fetchNotes() {}

// Constants: UPPER_SNAKE_CASE
const MAX_UPLOAD_SIZE = 10 * 1024 * 1024;
const API_TIMEOUT = 30000;

// Interfaces/Types: PascalCase
interface NoteCardProps {}
type NoteFilters = {};

// Variables: camelCase
const noteCount = 10;
const userId = "123";
```

### Files

```
# Backend files: snake_case
note_service.py
user_repository.py
error_handlers.py

# Frontend files: PascalCase for components, camelCase for utilities
NoteCard.tsx
UserProfile.tsx
api-client.ts
formatters.ts
```

## Error Handling

### Backend Error Pattern

```python
# Custom exceptions
from exceptions import NotFoundError, ValidationError

# Service layer
class NoteService:
    async def get_note(self, note_id: str):
        note = await self.repository.find_by_id(note_id)
        if not note:
            raise NotFoundError("Note", note_id)
        return note
    
    async def create_note(self, note_data: dict):
        if not note_data.get("title"):
            raise ValidationError("title", "Title is required")
        # ...

# Router layer
@router.get("/notes/{note_id}")
async def get_note(
    note_id: str,
    service: NoteService = Depends(get_note_service)
):
    note = await service.get_note(note_id)  # May raise NotFoundError
    return serialize_doc(note)

# Global exception handler catches and converts
app.add_exception_handler(NotFoundError, noteshub_exception_handler)
```

### Frontend Error Pattern

```typescript
// Service layer throws typed errors
class NoteNotFoundError extends Error {
    constructor(noteId: string) {
        super(`Note ${noteId} not found`);
        this.name = 'NoteNotFoundError';
    }
}

// Service
export const noteService = {
    async getNote(noteId: string): Promise<Note> {
        const response = await fetch(`/api/notes/${noteId}`);
        
        if (response.status === 404) {
            throw new NoteNotFoundError(noteId);
        }
        
        if (!response.ok) {
            throw new Error('Failed to fetch note');
        }
        
        return response.json();
    }
};

// Component handles errors
function NoteDetails({ noteId }: Props) {
    const { data, error } = useQuery({
        queryKey: ['note', noteId],
        queryFn: () => noteService.getNote(noteId),
        retry: (failureCount, error) => {
            // Don't retry on 404
            if (error instanceof NoteNotFoundError) return false;
            return failureCount < 3;
        }
    });
    
    if (error instanceof NoteNotFoundError) {
        return <NotFoundMessage />;
    }
    
    if (error) {
        return <ErrorMessage error={error} />;
    }
    
    return <NoteContent note={data} />;
}
```

## API Patterns

### Request/Response Format

```typescript
// ✅ Consistent response format
interface ApiResponse<T> {
    data: T;
    meta?: {
        page?: number;
        total?: number;
        timestamp: string;
    };
}

interface ApiError {
    error: {
        code: string;
        message: string;
        details?: Record<string, any>;
    };
}
```

### Pagination Pattern

```python
# Backend
@router.get("/notes")
async def get_notes(
    skip: int = 0,
    limit: int = 100,
    service: NoteService = Depends()
):
    notes = await service.get_notes(skip=skip, limit=limit)
    total = await service.count_notes()
    
    return {
        "data": serialize_docs(notes),
        "meta": {
            "page": skip // limit + 1,
            "limit": limit,
            "total": total
        }
    }
```

## State Management

### React Query Pattern

```typescript
// ✅ Standard pattern for data fetching
export function useNotes(filters?: NoteFilters) {
    return useQuery({
        queryKey: ['notes', filters],
        queryFn: () => noteService.getNotes(filters),
        staleTime: 5 * 60 * 1000, // 5 minutes
    });
}

// ✅ Mutation pattern
export function useCreateNote() {
    const queryClient = useQueryClient();
    
    return useMutation({
        mutationFn: (note: NoteCreate) => noteService.createNote(note),
        onSuccess: () => {
            // Invalidate and refetch
            queryClient.invalidateQueries({ queryKey: ['notes'] });
            toast.success('Note created successfully');
        },
        onError: (error) => {
            toast.error(`Failed to create note: ${error.message}`);
        }
    });
}
```

### Context Pattern

```typescript
// ✅ Context for global state
interface AuthContextType {
    user: User | null;
    login: (credentials: Credentials) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    
    // Implementation...
    
    return (
        <AuthContext.Provider value={{ user, login, logout, isAuthenticated }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) throw new Error('useAuth must be used within AuthProvider');
    return context;
}
```

## Testing Patterns

### Backend Tests

```python
# ✅ Test structure
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_note_success(client: AsyncClient, auth_headers):
    # Arrange
    note_data = {
        "title": "Test Note",
        "subject": "Mathematics"
    }
    
    # Act
    response = await client.post(
        "/api/notes",
        json=note_data,
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 201
    assert response.json()["title"] == "Test Note"

@pytest.mark.asyncio
async def test_create_note_unauthorized(client: AsyncClient):
    # Should fail without auth
    response = await client.post("/api/notes", json={})
    assert response.status_code == 401
```

### Frontend Tests

```typescript
// ✅ Component test
import { render, screen, fireEvent } from '@testing-library/react';
import { NoteCard } from './NoteCard';

describe('NoteCard', () => {
    const mockNote = {
        id: '1',
        title: 'Test Note',
        subject: 'Math'
    };
    
    it('renders note information', () => {
        render(<NoteCard note={mockNote} />);
        
        expect(screen.getByTestId('note-title')).toHaveTextContent('Test Note');
        expect(screen.getByTestId('note-subject')).toHaveTextContent('Math');
    });
    
    it('calls onDelete when delete button clicked', () => {
        const onDelete = jest.fn();
        render(<NoteCard note={mockNote} onDelete={onDelete} />);
        
        fireEvent.click(screen.getByTestId('delete-button'));
        
        expect(onDelete).toHaveBeenCalledWith('1');
    });
});
```

## Summary Checklist

### Backend Code Review

- [ ] Business logic is in service layer, not routes
- [ ] Using custom exceptions, not generic Exception
- [ ] Repository pattern for database access
- [ ] Dependency injection used correctly
- [ ] snake_case naming for Python
- [ ] Type hints on all functions
- [ ] Docstrings on classes and public methods

### Frontend Code Review

- [ ] Components are < 300 lines
- [ ] Reusable logic extracted into hooks
- [ ] API calls in service layer
- [ ] TypeScript interfaces defined
- [ ] camelCase/PascalCase naming correct
- [ ] Error handling implemented
- [ ] data-testid attributes on interactive elements
- [ ] Loading and error states handled

### General

- [ ] No hardcoded URLs or magic numbers
- [ ] Environment variables used for configuration
- [ ] Consistent error response format
- [ ] Logging implemented appropriately
- [ ] Tests added for new functionality

---

**Last Updated**: January 2025  
**Version**: 1.0.0

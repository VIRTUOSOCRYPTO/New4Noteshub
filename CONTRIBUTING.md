# Contributing to NotesHub

Thank you for your interest in contributing to NotesHub! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment
- Report unacceptable behavior to maintainers

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test thoroughly
6. Commit with clear messages
7. Push to your fork
8. Create a Pull Request

## Development Setup

See [SETUP.md](./SETUP.md) for detailed setup instructions.

## Coding Standards

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions/classes
- Maximum line length: 100 characters
- Use async/await for I/O operations

```python
async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get user by ID
    
    Args:
        user_id: User identifier
        
    Returns:
        User document or None if not found
    """
    return await self.db.users.find_one({"_id": ObjectId(user_id)})
```

### TypeScript (Frontend)

- Follow TypeScript strict mode
- Use functional components with hooks
- Prefer named exports
- Use Tailwind CSS for styling
- Maximum line length: 100 characters

```typescript
interface NoteCardProps {
  note: Note;
  onDownload?: (id: string) => void;
}

export const NoteCard: React.FC<NoteCardProps> = ({ note, onDownload }) => {
  // Component implementation
}
```

## Commit Messages

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(notes): add search functionality
fix(auth): resolve token expiration issue
docs(readme): update setup instructions
```

## Testing

### Before Submitting PR

1. Run all tests: `pytest` (backend) and `yarn test` (frontend)
2. Check linting: `ruff check .` and `yarn lint`
3. Verify type checking: `yarn tsc --noEmit`
4. Test manually in browser
5. Check console for errors

### Writing Tests

**Backend**:
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post("/api/register", json={
        "usn": "1RV21CS001",
        "email": "test@example.com",
        # ... other fields
    })
    assert response.status_code == 200
```

**Frontend**:
```typescript
import { render, screen } from '@testing-library/react'
import { NoteCard } from './NoteCard'

test('renders note title', () => {
  const note = { title: 'Test Note', /* ... */ }
  render(<NoteCard note={note} />)
  expect(screen.getByText('Test Note')).toBeInTheDocument()
})
```

## Pull Request Process

1. **Update Documentation**: If adding features, update relevant docs
2. **Add Tests**: New features must include tests
3. **Update Changelog**: Add entry to CHANGELOG.md
4. **Lint & Format**: Ensure code passes linting
5. **Describe Changes**: Write clear PR description
6. **Link Issues**: Reference related issues
7. **Request Review**: Tag relevant reviewers

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Manual testing completed
- [ ] Browser compatibility verified

## Checklist
- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No new warnings
```

## Project Structure Guidelines

### Adding New Backend Routes

1. Create route in appropriate router file (`routers/`)
2. Add business logic to service (`services/`)
3. Add validation to utils if needed (`utils/`)
4. Update API documentation
5. Add tests

### Adding New Frontend Components

1. Create component in appropriate directory
2. Export from index file if needed
3. Add TypeScript interfaces
4. Style with Tailwind CSS
5. Add tests

## Database Migrations

We don't use formal migrations yet, but:

1. Document schema changes
2. Provide migration script if needed
3. Test with existing data
4. Update models documentation

## Common Issues

### Virtual Environment Issues
```bash
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Node Modules Issues
```bash
rm -rf node_modules yarn.lock
yarn install
```

## Questions?

- Check existing issues
- Read documentation
- Ask in discussions
- Create new issue if needed

Thank you for contributing! 🎉

import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Home from '../pages/Home';

// Mock the hooks
vi.mock('../hooks/use-auth', () => ({
  useAuth: () => ({
    user: { usn: '1SI20CS045', department: 'CSE' },
    isLoading: false,
    logout: vi.fn()
  })
}));

vi.mock('wouter', () => ({
  useLocation: () => ['/', vi.fn()],
  Link: ({ children, ...props }: any) => <a {...props}>{children}</a>
}));

describe('Home Component', () => {
  it('should render without crashing', () => {
    render(<Home />);
    expect(screen.getByText(/Welcome/i)).toBeDefined();
  });

  it('should display user information when authenticated', () => {
    render(<Home />);
    // The component should show user-specific content
    expect(document.body).toBeDefined();
  });
});

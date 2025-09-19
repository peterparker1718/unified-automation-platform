import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Mock the BrowserRouter since we're not testing routing
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  BrowserRouter: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/' })
}));

test('renders unified automation platform', () => {
  render(<App />);
  const linkElement = screen.getByText(/Unified Automation Platform/i);
  expect(linkElement).toBeInTheDocument();
});

test('renders navigation tabs', () => {
  render(<App />);
  expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
  expect(screen.getByText(/Codex Trigger/i)).toBeInTheDocument();
  expect(screen.getByText(/Task Management/i)).toBeInTheDocument();
  expect(screen.getByText(/Dependency Audit/i)).toBeInTheDocument();
});
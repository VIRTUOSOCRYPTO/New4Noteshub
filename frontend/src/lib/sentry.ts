import * as Sentry from "@sentry/react";
import { useEffect } from "react";
import {
  createRoutesFromChildren,
  matchRoutes,
  useLocation,
  useNavigationType,
} from "react-router-dom";

// Initialize Sentry
export function initSentry() {
  const sentryDsn = import.meta.env.VITE_SENTRY_DSN;
  
  if (sentryDsn) {
    Sentry.init({
      dsn: sentryDsn,
      integrations: [
        Sentry.browserTracingIntegration(),
        Sentry.replayIntegration({
          maskAllText: false,
          blockAllMedia: false,
        }),
      ],
      // Performance Monitoring
      tracesSampleRate: 0.1, // 10% of transactions
      // Session Replay
      replaysSessionSampleRate: 0.1, // 10% of sessions
      replaysOnErrorSampleRate: 1.0, // 100% of errors
      // Environment
      environment: import.meta.env.MODE,
      // Release tracking
      release: import.meta.env.VITE_APP_VERSION || "1.0.0",
    });
    
    console.log("\u2705 Sentry initialized");
  } else {
    console.log("\u26a0\ufe0f Sentry DSN not configured - error monitoring disabled");
  }
}

// Error boundary fallback
export function SentryErrorFallback({ error, resetError }: { error: Error; resetError: () => void }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-8">
        <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full">
          <svg
            className="w-6 h-6 text-red-600"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </div>
        <h3 className="mt-4 text-lg font-medium text-gray-900 text-center">
          Something went wrong
        </h3>
        <p className="mt-2 text-sm text-gray-500 text-center">
          We've been notified and are working to fix the issue.
        </p>
        {import.meta.env.DEV && (
          <pre className="mt-4 p-4 bg-gray-100 rounded text-xs overflow-auto">
            {error.message}
          </pre>
        )}
        <div className="mt-6 flex gap-3">
          <button
            onClick={resetError}
            className="flex-1 bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90"
          >
            Try Again
          </button>
          <button
            onClick={() => window.location.href = "/"}
            className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300"
          >
            Go Home
          </button>
        </div>
      </div>
    </div>
  );
}

// Capture exceptions
export function captureException(error: Error, context?: Record<string, any>) {
  if (import.meta.env.VITE_SENTRY_DSN) {
    Sentry.captureException(error, {
      extra: context,
    });
  } else {
    console.error("Error:", error, context);
  }
}

// Capture messages
export function captureMessage(message: string, level: "info" | "warning" | "error" = "info") {
  if (import.meta.env.VITE_SENTRY_DSN) {
    Sentry.captureMessage(message, level);
  } else {
    console.log(`[${level}]`, message);
  }
}

// Set user context
export function setUserContext(user: { id: string; email?: string; username?: string }) {
  if (import.meta.env.VITE_SENTRY_DSN) {
    Sentry.setUser(user);
  }
}

// Clear user context
export function clearUserContext() {
  if (import.meta.env.VITE_SENTRY_DSN) {
    Sentry.setUser(null);
  }
}

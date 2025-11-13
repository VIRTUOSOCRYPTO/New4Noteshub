/**
 * Frontend Error Monitoring
 * Integrates with Sentry for production error tracking
 */

// Define Sentry types for when SDK is not installed
interface SentryUser {
  id?: string;
  email?: string;
  username?: string;
}

interface SentryContext {
  [key: string]: any;
}

interface SentryBreadcrumb {
  message: string;
  category?: string;
  level?: 'debug' | 'info' | 'warning' | 'error' | 'fatal';
  data?: Record<string, any>;
}

class ErrorMonitoring {
  private enabled: boolean = false;
  private sentryInitialized: boolean = false;

  constructor() {
    this.initialize();
  }

  /**
   * Initialize error monitoring
   */
  private async initialize() {
    // Check if Sentry DSN is configured
    const sentryDsn = import.meta.env.VITE_SENTRY_DSN;
    
    if (!sentryDsn) {
      console.log('⚠️  Sentry DSN not configured. Error monitoring disabled.');
      this.initializeFallback();
      return;
    }

    try {
      // Dynamically import Sentry to avoid loading in development
      const Sentry = await import('@sentry/react');
      
      Sentry.init({
        dsn: sentryDsn,
        environment: import.meta.env.MODE || 'development',
        integrations: [
          Sentry.browserTracingIntegration(),
          Sentry.replayIntegration({
            maskAllText: true,
            blockAllMedia: true,
          }),
        ],
        // Performance Monitoring
        tracesSampleRate: import.meta.env.MODE === 'production' ? 0.1 : 1.0,
        // Session Replay
        replaysSessionSampleRate: 0.1,
        replaysOnErrorSampleRate: 1.0,
        // Release tracking
        release: import.meta.env.VITE_APP_VERSION || 'unknown',
        // Filter out non-error events
        beforeSend(event, hint) {
          // Don't send events in development
          if (import.meta.env.MODE === 'development') {
            console.log('Sentry event (dev mode):', event);
            return null;
          }
          return event;
        },
      });

      this.enabled = true;
      this.sentryInitialized = true;
      console.log('✅ Sentry error monitoring initialized');
    } catch (error) {
      console.warn('Failed to initialize Sentry:', error);
      this.initializeFallback();
    }
  }

  /**
   * Initialize fallback error logging
   */
  private initializeFallback() {
    this.enabled = false;
    this.sentryInitialized = false;
    
    // Set up global error handler
    window.addEventListener('error', (event) => {
      this.logError(event.error || new Error(event.message), {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
      });
    });

    // Set up unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
      this.logError(
        new Error(`Unhandled Promise Rejection: ${event.reason}`),
        { reason: event.reason }
      );
    });

    console.log('📝 Using fallback error logging (console-based)');
  }

  /**
   * Capture an exception
   */
  captureException(error: Error, context?: SentryContext) {
    if (this.sentryInitialized) {
      import('@sentry/react').then((Sentry) => {
        if (context) {
          Sentry.setContext('additional_info', context);
        }
        Sentry.captureException(error);
      });
    } else {
      this.logError(error, context);
    }
  }

  /**
   * Capture a message
   */
  captureMessage(message: string, level: 'debug' | 'info' | 'warning' | 'error' = 'info', context?: SentryContext) {
    if (this.sentryInitialized) {
      import('@sentry/react').then((Sentry) => {
        if (context) {
          Sentry.setContext('additional_info', context);
        }
        Sentry.captureMessage(message, level);
      });
    } else {
      this.logMessage(message, level, context);
    }
  }

  /**
   * Set user context
   */
  setUser(user: SentryUser | null) {
    if (this.sentryInitialized) {
      import('@sentry/react').then((Sentry) => {
        Sentry.setUser(user);
      });
    } else {
      console.log('User context:', user);
    }
  }

  /**
   * Set custom tag
   */
  setTag(key: string, value: string) {
    if (this.sentryInitialized) {
      import('@sentry/react').then((Sentry) => {
        Sentry.setTag(key, value);
      });
    }
  }

  /**
   * Add breadcrumb for debugging
   */
  addBreadcrumb(breadcrumb: SentryBreadcrumb) {
    if (this.sentryInitialized) {
      import('@sentry/react').then((Sentry) => {
        Sentry.addBreadcrumb(breadcrumb);
      });
    } else {
      console.log('Breadcrumb:', breadcrumb);
    }
  }

  /**
   * Log API errors
   */
  logApiError(error: any, endpoint: string, method: string) {
    const context = {
      endpoint,
      method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
    };

    this.captureException(
      error instanceof Error ? error : new Error('API Error'),
      context
    );
  }

  /**
   * Fallback error logging
   */
  private logError(error: Error, context?: any) {
    console.error('Error captured:', {
      message: error.message,
      stack: error.stack,
      context,
      timestamp: new Date().toISOString(),
    });

    // Could send to custom logging endpoint here
    this.sendToCustomEndpoint('error', {
      message: error.message,
      stack: error.stack,
      context,
    });
  }

  /**
   * Fallback message logging
   */
  private logMessage(message: string, level: string, context?: any) {
    const logFn = level === 'error' ? console.error : 
                  level === 'warning' ? console.warn : console.log;
    
    logFn('Message captured:', {
      message,
      level,
      context,
      timestamp: new Date().toISOString(),
    });

    // Could send to custom logging endpoint here
    this.sendToCustomEndpoint('message', { message, level, context });
  }

  /**
   * Send to custom logging endpoint (optional)
   */
  private sendToCustomEndpoint(type: string, data: any) {
    // Only send in production
    if (import.meta.env.MODE !== 'production') {
      return;
    }

    // Send to backend logging endpoint
    const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001';
    
    fetch(`${backendUrl}/api/logs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        type,
        data,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
      }),
    }).catch((err) => {
      // Fail silently to avoid infinite loops
      console.warn('Failed to send log to backend:', err);
    });
  }

  /**
   * Track navigation
   */
  trackNavigation(to: string, from?: string) {
    this.addBreadcrumb({
      message: `Navigation: ${from || 'unknown'} → ${to}`,
      category: 'navigation',
      level: 'info',
    });
  }

  /**
   * Track user action
   */
  trackAction(action: string, data?: Record<string, any>) {
    this.addBreadcrumb({
      message: `User action: ${action}`,
      category: 'user',
      level: 'info',
      data,
    });
  }
}

// Export singleton instance
export const errorMonitoring = new ErrorMonitoring();

// Export for React Error Boundary integration
export const logErrorToService = (error: Error, errorInfo: any) => {
  errorMonitoring.captureException(error, {
    componentStack: errorInfo.componentStack,
    errorBoundary: true,
  });
};

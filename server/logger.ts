/**
 * Structured Logging System
 * Provides consistent logging across the application
 */

export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR',
}

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  context?: Record<string, any>;
  requestId?: string;
  userId?: number;
  error?: {
    message: string;
    stack?: string;
    code?: string;
  };
}

class Logger {
  private minLevel: LogLevel;

  constructor() {
    // Set minimum log level based on environment
    const env = process.env.NODE_ENV || 'development';
    this.minLevel = env === 'production' ? LogLevel.INFO : LogLevel.DEBUG;
  }

  private shouldLog(level: LogLevel): boolean {
    const levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR];
    const currentLevelIndex = levels.indexOf(this.minLevel);
    const messageLevelIndex = levels.indexOf(level);
    return messageLevelIndex >= currentLevelIndex;
  }

  private formatLog(entry: LogEntry): string {
    const { timestamp, level, message, context, requestId, userId, error } = entry;
    
    let logParts = [
      `[${timestamp}]`,
      `[${level}]`,
    ];

    if (requestId) {
      logParts.push(`[ReqID: ${requestId}]`);
    }

    if (userId) {
      logParts.push(`[User: ${userId}]`);
    }

    logParts.push(message);

    if (context && Object.keys(context).length > 0) {
      logParts.push(`\n  Context: ${JSON.stringify(context, null, 2)}`);
    }

    if (error) {
      logParts.push(`\n  Error: ${error.message}`);
      if (error.code) {
        logParts.push(`\n  Code: ${error.code}`);
      }
      if (error.stack && process.env.NODE_ENV === 'development') {
        logParts.push(`\n  Stack: ${error.stack}`);
      }
    }

    return logParts.join(' ');
  }

  private log(level: LogLevel, message: string, context?: Record<string, any>, error?: Error): void {
    if (!this.shouldLog(level)) return;

    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
    };

    if (error) {
      entry.error = {
        message: error.message,
        stack: error.stack,
        code: (error as any).code,
      };
    }

    const formattedLog = this.formatLog(entry);

    // Output to appropriate stream
    if (level === LogLevel.ERROR) {
      console.error(formattedLog);
    } else if (level === LogLevel.WARN) {
      console.warn(formattedLog);
    } else {
      console.log(formattedLog);
    }
  }

  debug(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.DEBUG, message, context);
  }

  info(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.INFO, message, context);
  }

  warn(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.WARN, message, context);
  }

  error(message: string, error?: Error, context?: Record<string, any>): void {
    this.log(LogLevel.ERROR, message, context, error);
  }

  // Request logging helpers
  logRequest(method: string, path: string, statusCode: number, duration: number, context?: Record<string, any>): void {
    const message = `${method} ${path} - ${statusCode} (${duration}ms)`;
    const level = statusCode >= 500 ? LogLevel.ERROR : statusCode >= 400 ? LogLevel.WARN : LogLevel.INFO;
    this.log(level, message, context);
  }

  logAuth(action: string, userId?: number, success: boolean = true, context?: Record<string, any>): void {
    const level = success ? LogLevel.INFO : LogLevel.WARN;
    const message = `Auth ${action}: ${success ? 'Success' : 'Failed'}`;
    this.log(level, message, { ...context, userId });
  }

  logDatabase(operation: string, table: string, duration?: number, error?: Error): void {
    const message = `DB ${operation} on ${table}${duration ? ` (${duration}ms)` : ''}`;
    if (error) {
      this.error(message, error);
    } else {
      this.debug(message);
    }
  }

  logSecurity(event: string, severity: 'low' | 'medium' | 'high', context?: Record<string, any>): void {
    const level = severity === 'high' ? LogLevel.ERROR : severity === 'medium' ? LogLevel.WARN : LogLevel.INFO;
    this.log(level, `Security Event: ${event}`, context);
  }
}

// Export singleton instance
export const logger = new Logger();

// Export for testing or custom instances
export { Logger };

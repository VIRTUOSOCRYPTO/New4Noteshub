/**
 * Environment Variable Validator
 * Validates all required environment variables on startup
 * Fails fast with clear error messages if any are missing
 */

import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

export interface EnvConfig {
  // Database
  DATABASE_URL: string;
  PGHOST?: string;
  PGUSER?: string;
  PGPASSWORD?: string;
  PGDATABASE?: string;
  PGPORT?: string;
  
  // Supabase (optional)
  SUPABASE_URL?: string;
  SUPABASE_KEY?: string;
  
  // Server
  NODE_ENV: string;
  PORT?: string;
  SESSION_SECRET?: string;
  
  // Security
  FORCE_SECURE_COOKIES?: string;
  FORCE_HSTS?: string;
  CORS_ALLOW_ORIGIN?: string;
  CORS_CREDENTIALS?: string;
}

export class EnvValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'EnvValidationError';
  }
}

/**
 * Validates required environment variables
 * @throws {EnvValidationError} If validation fails
 */
export function validateEnv(): EnvConfig {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Required variables
  const required: (keyof EnvConfig)[] = [
    'DATABASE_URL',
    'NODE_ENV'
  ];

  // Check required variables
  for (const key of required) {
    if (!process.env[key]) {
      errors.push(`❌ Missing required environment variable: ${key}`);
    }
  }

  // Validate DATABASE_URL format if present
  if (process.env.DATABASE_URL) {
    const dbUrlPattern = /^postgres(ql)?:\/\/.+/;
    if (!dbUrlPattern.test(process.env.DATABASE_URL)) {
      errors.push(`❌ Invalid DATABASE_URL format. Expected: postgresql://user:password@host:port/database`);
    }
  }

  // Validate NODE_ENV
  if (process.env.NODE_ENV) {
    const validEnvs = ['development', 'production', 'test'];
    if (!validEnvs.includes(process.env.NODE_ENV)) {
      warnings.push(`⚠️  NODE_ENV should be one of: ${validEnvs.join(', ')}. Current: ${process.env.NODE_ENV}`);
    }
  }

  // Check optional but recommended variables
  if (!process.env.SESSION_SECRET) {
    warnings.push(`⚠️  SESSION_SECRET not set. Using default (not recommended for production)`);
  }

  if (process.env.NODE_ENV === 'production') {
    // Production-specific checks
    if (!process.env.CORS_ALLOW_ORIGIN) {
      warnings.push(`⚠️  CORS_ALLOW_ORIGIN not set in production. Using defaults.`);
    }
    
    if (process.env.FORCE_SECURE_COOKIES !== 'true') {
      warnings.push(`⚠️  FORCE_SECURE_COOKIES should be 'true' in production`);
    }
  }

  // Check Supabase configuration (optional but warn if incomplete)
  const hasSupabaseUrl = !!process.env.SUPABASE_URL;
  const hasSupabaseKey = !!process.env.SUPABASE_KEY;
  
  if (hasSupabaseUrl !== hasSupabaseKey) {
    warnings.push(`⚠️  Incomplete Supabase configuration. Both SUPABASE_URL and SUPABASE_KEY should be set.`);
  }

  // Print warnings
  if (warnings.length > 0) {
    console.log('\n📋 Environment Warnings:');
    warnings.forEach(warning => console.log(warning));
    console.log('');
  }

  // If there are errors, throw
  if (errors.length > 0) {
    const errorMessage = [
      '\n❌ Environment Validation Failed!\n',
      ...errors,
      '\n💡 Fix: Create a .env file with all required variables.',
      '   See .env.example for reference.\n'
    ].join('\n');
    
    throw new EnvValidationError(errorMessage);
  }

  // Return validated config
  return {
    DATABASE_URL: process.env.DATABASE_URL!,
    PGHOST: process.env.PGHOST,
    PGUSER: process.env.PGUSER,
    PGPASSWORD: process.env.PGPASSWORD,
    PGDATABASE: process.env.PGDATABASE,
    PGPORT: process.env.PGPORT,
    SUPABASE_URL: process.env.SUPABASE_URL,
    SUPABASE_KEY: process.env.SUPABASE_KEY,
    NODE_ENV: process.env.NODE_ENV!,
    PORT: process.env.PORT,
    SESSION_SECRET: process.env.SESSION_SECRET,
    FORCE_SECURE_COOKIES: process.env.FORCE_SECURE_COOKIES,
    FORCE_HSTS: process.env.FORCE_HSTS,
    CORS_ALLOW_ORIGIN: process.env.CORS_ALLOW_ORIGIN,
    CORS_CREDENTIALS: process.env.CORS_CREDENTIALS,
  };
}

/**
 * Prints environment configuration summary (sanitized)
 */
export function printEnvSummary(config: EnvConfig): void {
  console.log('\n✅ Environment Configuration:');
  console.log(`   NODE_ENV: ${config.NODE_ENV}`);
  console.log(`   DATABASE: ${config.DATABASE_URL ? '✓ Connected' : '✗ Not configured'}`);
  console.log(`   SUPABASE: ${config.SUPABASE_URL ? '✓ Configured' : '✗ Not configured (optional)'}`);
  console.log(`   SESSION_SECRET: ${config.SESSION_SECRET ? '✓ Set' : '✗ Using default'}`);
  console.log('');
}

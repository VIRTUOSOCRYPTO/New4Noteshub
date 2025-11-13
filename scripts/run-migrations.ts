/**
 * Database Migration Runner
 * Runs all pending migrations against the database
 */
import { drizzle } from 'drizzle-orm/postgres-js';
import { migrate } from 'drizzle-orm/postgres-js/migrator';
import postgres from 'postgres';
import dotenv from 'dotenv';
import { resolve } from 'path';

// Load environment variables
dotenv.config();

const DATABASE_URL = process.env.DATABASE_URL;

if (!DATABASE_URL) {
  console.error('❌ DATABASE_URL environment variable is not set');
  process.exit(1);
}

async function runMigrations() {
  console.log('🔄 Starting database migrations...');
  console.log('📁 Migrations folder: ./migrations');
  
  // Create connection for migrations
  const migrationClient = postgres(DATABASE_URL, { max: 1 });
  
  try {
    console.log('🔌 Connecting to database...');
    
    // Run migrations
    const db = drizzle(migrationClient);
    await migrate(db, { migrationsFolder: resolve(__dirname, '../migrations') });
    
    console.log('✅ Migrations completed successfully!');
  } catch (error) {
    console.error('❌ Migration failed:', error);
    throw error;
  } finally {
    // Close connection
    await migrationClient.end();
    console.log('🔌 Database connection closed');
  }
}

// Run migrations
runMigrations()
  .then(() => {
    console.log('\n✨ All done!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n💥 Migration process failed:', error);
    process.exit(1);
  });

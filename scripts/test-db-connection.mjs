/**
 * Database Connection Test Script
 * Tests database connectivity and verifies schema
 */

import dotenv from 'dotenv';
import postgres from 'postgres';

// Load environment variables
dotenv.config();

async function testDatabaseConnection() {
  console.log('🔍 Testing Database Connection...\n');
  
  // Check if DATABASE_URL exists
  if (!process.env.DATABASE_URL) {
    console.error('❌ DATABASE_URL environment variable is not set!');
    process.exit(1);
  }
  
  console.log('✓ DATABASE_URL is set');
  console.log(`  Host: ${process.env.PGHOST || 'N/A'}`);
  console.log(`  Database: ${process.env.PGDATABASE || 'N/A'}`);
  console.log(`  Port: ${process.env.PGPORT || 'N/A'}\n`);
  
  let sql;
  
  try {
    // Create connection
    console.log('📡 Attempting to connect...');
    sql = postgres(process.env.DATABASE_URL, {
      ssl: { rejectUnauthorized: false },
      max: 1,
      connect_timeout: 10,
    });
    
    // Test basic query
    console.log('🔄 Testing basic query (SELECT 1)...');
    const result = await sql`SELECT 1 as test`;
    console.log('✅ Basic query successful:', result);
    
    // Check PostgreSQL version
    console.log('\n🔄 Checking PostgreSQL version...');
    const versionResult = await sql`SELECT version()`;
    console.log('✅ PostgreSQL version:', versionResult[0].version.split(' ').slice(0, 2).join(' '));
    
    // Check if our tables exist
    console.log('\n🔄 Checking for application tables...');
    const tablesResult = await sql`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      AND table_type = 'BASE TABLE'
      ORDER BY table_name
    `;
    
    if (tablesResult.length === 0) {
      console.warn('⚠️  No tables found in database!');
      console.log('   You may need to run: npm run db:push');
    } else {
      console.log('✅ Found tables:', tablesResult.map(t => t.table_name).join(', '));
    }
    
    // Test a sample query on users table if it exists
    const hasUsersTable = tablesResult.some(t => t.table_name === 'users');
    if (hasUsersTable) {
      console.log('\n🔄 Testing query on users table...');
      const userCount = await sql`SELECT COUNT(*) as count FROM users`;
      console.log(`✅ Users table accessible. Total users: ${userCount[0].count}`);
    }
    
    console.log('\n✅ All database tests passed!');
    console.log('   Database connection is working correctly.\n');
    
  } catch (error) {
    console.error('\n❌ Database connection failed!');
    console.error('Error:', error.message);
    
    if (error.code) {
      console.error('Error code:', error.code);
    }
    
    console.error('\n💡 Troubleshooting tips:');
    console.error('   1. Verify DATABASE_URL is correct in .env');
    console.error('   2. Check if database server is accessible');
    console.error('   3. Verify credentials (username/password)');
    console.error('   4. Check firewall/network settings');
    console.error('   5. Run: npm run db:push to create tables\n');
    
    process.exit(1);
  } finally {
    // Close connection
    if (sql) {
      await sql.end();
      console.log('🔌 Connection closed');
    }
  }
}

// Run the test
testDatabaseConnection().catch(error => {
  console.error('Unexpected error:', error);
  process.exit(1);
});

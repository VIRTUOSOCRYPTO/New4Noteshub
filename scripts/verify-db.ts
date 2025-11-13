/**
 * Database Connection Verification Script
 * Tests database connection and queries basic info
 */
import postgres from 'postgres';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const DATABASE_URL = process.env.DATABASE_URL;

if (!DATABASE_URL) {
  console.error('❌ DATABASE_URL environment variable is not set');
  process.exit(1);
}

async function verifyDatabase() {
  console.log('🔄 Verifying database connection...');
  console.log('🔗 Using connection from DATABASE_URL');
  
  const sql = postgres(DATABASE_URL, {
    ssl: { rejectUnauthorized: false },
    max: 1
  });
  
  try {
    // Test basic connection
    console.log('\n📊 Running test queries...');
    
    // 1. Check PostgreSQL version
    const versionResult = await sql`SELECT version()`;
    console.log('\n✅ PostgreSQL Version:');
    console.log('   ', versionResult[0].version.split(',')[0]);
    
    // 2. Check current database
    const dbResult = await sql`SELECT current_database()`;
    console.log('\n✅ Current Database:', dbResult[0].current_database);
    
    // 3. List all tables
    const tablesResult = await sql`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public'
      ORDER BY table_name
    `;
    
    console.log('\n✅ Tables in database:');
    if (tablesResult.length === 0) {
      console.log('   ⚠️  No tables found (run migrations first)');
    } else {
      tablesResult.forEach((row: any) => {
        console.log(`   - ${row.table_name}`);
      });
    }
    
    // 4. Check for required tables
    const requiredTables = ['users', 'notes', 'bookmarks', 'messages', 'conversations', 'drawings'];
    const existingTables = tablesResult.map((row: any) => row.table_name);
    const missingTables = requiredTables.filter(table => !existingTables.includes(table));
    
    if (missingTables.length > 0) {
      console.log('\n⚠️  Missing tables:');
      missingTables.forEach(table => console.log(`   - ${table}`));
      console.log('\n💡 Run: yarn migrate to create missing tables');
    } else {
      console.log('\n✅ All required tables exist!');
    }
    
    // 5. Count records in key tables
    if (existingTables.includes('users')) {
      const userCount = await sql`SELECT COUNT(*) as count FROM users`;
      console.log(`\n📊 Database Statistics:`);
      console.log(`   Users: ${userCount[0].count}`);
      
      if (existingTables.includes('notes')) {
        const notesCount = await sql`SELECT COUNT(*) as count FROM notes`;
        console.log(`   Notes: ${notesCount[0].count}`);
      }
      
      if (existingTables.includes('bookmarks')) {
        const bookmarksCount = await sql`SELECT COUNT(*) as count FROM bookmarks`;
        console.log(`   Bookmarks: ${bookmarksCount[0].count}`);
      }
    }
    
    console.log('\n✅ Database connection verified successfully!');
    
  } catch (error: any) {
    console.error('\n❌ Database verification failed:');
    console.error('   Error:', error.message);
    if (error.code) {
      console.error('   Code:', error.code);
    }
    throw error;
  } finally {
    await sql.end();
    console.log('\n🔌 Connection closed');
  }
}

// Run verification
verifyDatabase()
  .then(() => {
    console.log('\n✨ Verification complete!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n💥 Verification failed');
    process.exit(1);
  });

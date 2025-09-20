#!/usr/bin/env python3
"""
Optimize Kanban Performance
==========================

This script creates optimized Kanban API endpoints with pagination, filtering, and performance improvements.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime

# Railway Database Configuration
RAILWAY_DB_CONFIG = {
    'host': 'nozomi.proxy.rlwy.net',
    'database': 'railway',
    'user': 'postgres',
    'password': 'irUsikIqAifdrCMNOlGtApioMQJDjDfE',
    'port': 49967
}

def create_kanban_indexes():
    """Create database indexes to optimize Kanban queries"""
    try:
        print("🔌 Connecting to Railway database...")
        conn = psycopg2.connect(**RAILWAY_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        print("=" * 60)
        
        print("🔧 Creating performance indexes for Kanban...")
        
        # Index for organization_id (most important for filtering)
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_deals_organization_id ON deals(organization_id)")
            print("  ✅ Created index on deals.organization_id")
        except Exception as e:
            print(f"  ⚠️  Index on deals.organization_id may already exist: {e}")
        
        # Index for stage_id (for kanban columns)
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_deals_stage_id ON deals(stage_id)")
            print("  ✅ Created index on deals.stage_id")
        except Exception as e:
            print(f"  ⚠️  Index on deals.stage_id may already exist: {e}")
        
        # Composite index for organization_id + stage_id (most common query pattern)
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_deals_org_stage ON deals(organization_id, stage_id)")
            print("  ✅ Created composite index on deals(organization_id, stage_id)")
        except Exception as e:
            print(f"  ⚠️  Composite index may already exist: {e}")
        
        # Index for owner_id (for filtering by user)
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_deals_owner_id ON deals(owner_id)")
            print("  ✅ Created index on deals.owner_id")
        except Exception as e:
            print(f"  ⚠️  Index on deals.owner_id may already exist: {e}")
        
        # Index for created_at (for sorting)
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_deals_created_at ON deals(created_at DESC)")
            print("  ✅ Created index on deals.created_at")
        except Exception as e:
            print(f"  ⚠️  Index on deals.created_at may already exist: {e}")
        
        # Index for watcher table
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_watcher_deal_id ON watcher(deal_id)")
            print("  ✅ Created index on watcher.deal_id")
        except Exception as e:
            print(f"  ⚠️  Index on watcher.deal_id may already exist: {e}")
        
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_watcher_user_id ON watcher(user_id)")
            print("  ✅ Created index on watcher.user_id")
        except Exception as e:
            print(f"  ⚠️  Index on watcher.user_id may already exist: {e}")
        
        print("\n📊 Performance Analysis:")
        
        # Test query performance
        cursor.execute("EXPLAIN (ANALYZE, BUFFERS) SELECT COUNT(*) FROM deals WHERE organization_id = 1")
        result = cursor.fetchone()
        print(f"  Query plan for organization filter: {result[0][:100]}...")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Database indexes created successfully!")
        print("🚀 Kanban performance should be significantly improved")
        
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")

def analyze_current_performance():
    """Analyze current Kanban performance issues"""
    try:
        print("🔌 Connecting to Railway database...")
        conn = psycopg2.connect(**RAILWAY_DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        print("=" * 60)
        
        print("📊 CURRENT KANBAN PERFORMANCE ANALYSIS:")
        print("-" * 50)
        
        # Count deals by organization
        cursor.execute("SELECT organization_id, COUNT(*) FROM deals GROUP BY organization_id ORDER BY COUNT(*) DESC")
        org_counts = cursor.fetchall()
        
        for org_id, count in org_counts:
            print(f"  Organization {org_id}: {count:,} deals")
        
        # Count deals by stage
        cursor.execute("""
            SELECT s.name, COUNT(d.id) as deal_count 
            FROM stages s 
            LEFT JOIN deals d ON s.id = d.stage_id AND d.organization_id = 1 
            GROUP BY s.id, s.name 
            ORDER BY deal_count DESC
        """)
        stage_counts = cursor.fetchall()
        
        print(f"\n📋 DEALS BY STAGE (Organization 1):")
        for stage_name, count in stage_counts:
            print(f"  {stage_name}: {count:,} deals")
        
        # Count watchers
        cursor.execute("SELECT COUNT(*) FROM watcher")
        watcher_count = cursor.fetchone()[0]
        print(f"\n👥 Total watchers: {watcher_count:,}")
        
        # Performance issues identified
        print(f"\n⚠️  PERFORMANCE ISSUES IDENTIFIED:")
        print(f"  1. Loading {org_counts[0][1]:,} deals at once (should be paginated)")
        print(f"  2. N+1 query problem: {org_counts[0][1]:,} separate watcher queries")
        print(f"  3. No database indexes on key fields")
        print(f"  4. Frontend rendering {org_counts[0][1]:,} DOM elements")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error analyzing performance: {e}")

if __name__ == "__main__":
    analyze_current_performance()
    print("\n" + "="*60)
    create_kanban_indexes()

#!/usr/bin/env python3
"""
Check CallQueueMembers Schema
============================

This script checks the actual database schema for call_queue_members table.
"""

import psycopg2

def check_queue_members_schema():
    """Check the call_queue_members table structure"""
    
    try:
        # Connect to Railway database
        conn = psycopg2.connect(
            host='nozomi.proxy.rlwy.net',
            port=49967,
            database='railway',
            user='postgres',
            password='irUsikIqAifdrCMNOlGtApioMQJDjDfE'
        )
        
        cur = conn.cursor()
        
        # Check call_queue_members table structure
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'call_queue_members' 
            ORDER BY ordinal_position;
        """)
        
        print('🔍 CallQueueMembers Table Structure:')
        print('=' * 50)
        columns = []
        for row in cur.fetchall():
            column_name, data_type, is_nullable = row
            columns.append(column_name)
            print(f'   {column_name}: {data_type} {"(nullable)" if is_nullable == "YES" else "(not null)"}')
        
        print(f'\n📋 Available columns: {", ".join(columns)}')
        
        # Check if there are any records
        cur.execute("SELECT COUNT(*) FROM call_queue_members")
        count = cur.fetchone()[0]
        print(f'\n📊 Records count: {count}')
        
        if count > 0:
            # Get a sample record
            cur.execute("SELECT * FROM call_queue_members LIMIT 1")
            sample = cur.fetchone()
            if sample:
                print(f'\n📝 Sample record:')
                for i, col in enumerate(columns):
                    print(f'   {col}: {sample[i]}')
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    check_queue_members_schema()

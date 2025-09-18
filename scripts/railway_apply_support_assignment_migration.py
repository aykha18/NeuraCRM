#!/usr/bin/env python3
"""
Apply Support Assignment DB changes on Railway (PostgreSQL).

This script is idempotent and safe to run multiple times. It will:
- Create tables: support_queues, user_skills, assignment_audits (IF NOT EXISTS)
- Add columns to support_tickets: assigned_at, assignment_reason, assignment_type, queue_id (IF NOT EXISTS)

Usage:
  # Ensure DATABASE_URL points to your Railway Postgres URL
  # Example (PowerShell):
  #   $env:DATABASE_URL = "postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DB"
  # Then run:
  #   python scripts/railway_apply_support_assignment_migration.py
"""

import os
import sys
from sqlalchemy import create_engine, text


def get_database_url() -> str:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    # Accept either SQLAlchemy or plain psycopg URLs
    if db_url.startswith("postgres://"):
        # SQLAlchemy recommends postgresql+psycopg2
        db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    return db_url


DDL_STATEMENTS = [
    # 1) Tables
    text(
        """
        CREATE TABLE IF NOT EXISTS support_queues (
            id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL,
            description TEXT,
            organization_id INTEGER NOT NULL,
            auto_assign BOOLEAN DEFAULT TRUE,
            round_robin BOOLEAN DEFAULT TRUE,
            max_workload INTEGER DEFAULT 10,
            business_hours_only BOOLEAN DEFAULT FALSE,
            business_hours_start VARCHAR DEFAULT '09:00',
            business_hours_end VARCHAR DEFAULT '17:00',
            timezone VARCHAR DEFAULT 'UTC',
            handles_priorities JSON,
            escalation_queue_id INTEGER,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
    ),
    text(
        """
        CREATE TABLE IF NOT EXISTS user_skills (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            skill_name VARCHAR NOT NULL,
            skill_level VARCHAR DEFAULT 'intermediate',
            category VARCHAR,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
    ),
    text(
        """
        CREATE TABLE IF NOT EXISTS assignment_audits (
            id SERIAL PRIMARY KEY,
            ticket_id INTEGER NOT NULL,
            assigned_to_id INTEGER,
            assigned_by_id INTEGER NOT NULL,
            assignment_type VARCHAR NOT NULL,
            assignment_reason TEXT,
            previous_assigned_to_id INTEGER,
            queue_id INTEGER,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
    ),
    # 2) Columns on support_tickets
    text(
        """
        ALTER TABLE support_tickets
        ADD COLUMN IF NOT EXISTS assigned_at TIMESTAMP NULL;
        """
    ),
    text(
        """
        ALTER TABLE support_tickets
        ADD COLUMN IF NOT EXISTS assignment_reason TEXT NULL;
        """
    ),
    text(
        """
        ALTER TABLE support_tickets
        ADD COLUMN IF NOT EXISTS assignment_type VARCHAR NULL DEFAULT 'manual';
        """
    ),
    text(
        """
        ALTER TABLE support_tickets
        ADD COLUMN IF NOT EXISTS queue_id INTEGER NULL;
        """
    ),
]


def main() -> None:
    db_url = get_database_url()
    print(f"Using DATABASE_URL: {db_url}")
    engine = create_engine(db_url, future=True)

    with engine.begin() as conn:
        for stmt in DDL_STATEMENTS:
            conn.execute(stmt)

        # Optional: add FK after column exists (ignore errors if table/column missing)
        try:
            conn.execute(
                text(
                    """
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.table_constraints tc
                            WHERE tc.constraint_type = 'FOREIGN KEY'
                              AND tc.table_name = 'support_tickets'
                              AND tc.constraint_name = 'support_tickets_queue_id_fkey'
                        ) THEN
                            ALTER TABLE support_tickets
                            ADD CONSTRAINT support_tickets_queue_id_fkey
                            FOREIGN KEY (queue_id) REFERENCES support_queues (id);
                        END IF;
                    END$$;
                    """
                )
            )
        except Exception as fk_err:
            print(f"Warning: could not create FK for support_tickets.queue_id: {fk_err}")

    print("✅ Support assignment migration applied successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)



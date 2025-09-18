"""
Utility script to create/verify all database tables on a target DATABASE_URL.

Usage:
  python scripts/railway_create_tables.py <DATABASE_URL>

If the DATABASE_URL argument is omitted, the environment variable DATABASE_URL
will be used. The script also ensures project root is on sys.path.
"""

import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Optionally override DATABASE_URL from argv
if len(sys.argv) > 1 and sys.argv[1]:
    os.environ['DATABASE_URL'] = sys.argv[1]

from backend.api.db import get_engine
from backend.api import models


def main() -> None:
    engine = get_engine()
    # Create/verify all tables defined in models
    models.Base.metadata.create_all(bind=engine)
    print("Created/verified all tables on target DATABASE_URL")


if __name__ == "__main__":
    main()



import os
import sys
from sqlalchemy import text

# Ensure project root is on PYTHONPATH
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.api.db import get_engine


def main() -> None:
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
        # No-op select to ensure connection stays open until commit
        conn.execute(text("SELECT 1"))


if __name__ == "__main__":
    main()



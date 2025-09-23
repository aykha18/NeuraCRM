import os
import sys
from sqlalchemy import text

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.api.db import get_engine


def main() -> None:
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(text("SELECT id FROM users ORDER BY id ASC LIMIT 1")).first()
        if not row:
            print("")
            return
        print(str(row[0]))


if __name__ == "__main__":
    main()



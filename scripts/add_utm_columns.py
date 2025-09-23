import os
import sys
from sqlalchemy import text

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.api.db import get_engine


def main() -> None:
    stmts = [
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS utm_source VARCHAR",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS utm_medium VARCHAR",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS utm_campaign VARCHAR",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS utm_term VARCHAR",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS utm_content VARCHAR",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS referrer_url VARCHAR",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS landing_page_url VARCHAR",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS gclid VARCHAR",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS fbclid VARCHAR",
    ]
    engine = get_engine()
    with engine.begin() as conn:
        for s in stmts:
            conn.execute(text(s))


if __name__ == "__main__":
    main()



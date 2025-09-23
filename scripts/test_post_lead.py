import os
import sys
import json
import requests

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.generate_jwt import make_jwt  # type: ignore
from backend.api.db import get_engine  # type: ignore
from sqlalchemy import text  # type: ignore


def get_first_user_id() -> int:
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(text("SELECT id FROM users ORDER BY id ASC LIMIT 1")).first()
        if not row:
            raise RuntimeError("No users found in DB")
        return int(row[0])


def main() -> None:
    base_url = os.environ.get("API_BASE", "http://localhost:8000")
    user_id = get_first_user_id()
    secret = os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")
    token = make_jwt(user_id, secret)

    payload = {
        "title": "UTM Test Lead",
        "status": "new",
        "source": "web",
        "utm_source": "google",
        "utm_medium": "cpc",
        "utm_campaign": "fall_promo",
        "utm_term": "crm software",
        "utm_content": "ad_a",
        "referrer_url": "https://example.com",
        "landing_page_url": "http://localhost:5173/?utm_source=google",
        "gclid": "test-gclid",
        "fbclid": "test-fbclid",
    }

    resp = requests.post(
        f"{base_url}/api/leads",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
        timeout=15,
    )
    print(resp.status_code)
    print(resp.text)


if __name__ == "__main__":
    main()



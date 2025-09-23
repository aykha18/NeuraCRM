import os
import json
import base64
import hmac
import hashlib
import time


def b64url(data: bytes) -> bytes:
    return base64.urlsafe_b64encode(data).rstrip(b"=")


def make_jwt(sub: int, secret: str, hours_valid: int = 2) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {"sub": sub, "iat": now, "exp": now + hours_valid * 3600}
    h = b64url(json.dumps(header, separators=(",", ":")).encode())
    p = b64url(json.dumps(payload, separators=(",", ":")).encode())
    msg = h + b"." + p
    sig = b64url(hmac.new(secret.encode(), msg, hashlib.sha256).digest())
    return (msg + b"." + sig).decode()


if __name__ == "__main__":
    secret = os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")
    sub = int(os.environ.get("JWT_SUB", "1"))
    print(make_jwt(sub, secret))



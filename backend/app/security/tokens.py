import base64
import hashlib
import hmac
import json
import time


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(subject: str, secret_key: str, expires_in_minutes: int) -> str:
    payload = {
        "sub": subject,
        "exp": int(time.time()) + (expires_in_minutes * 60),
    }
    payload_segment = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(secret_key.encode("utf-8"), payload_segment.encode("utf-8"), hashlib.sha256)
    signature_segment = _b64url_encode(signature.digest())
    return f"{payload_segment}.{signature_segment}"


def decode_access_token(token: str, secret_key: str) -> dict[str, int | str]:
    try:
        payload_segment, signature_segment = token.split(".", maxsplit=1)
    except ValueError as exc:
        raise ValueError("Invalid token format") from exc

    expected_signature = hmac.new(
        secret_key.encode("utf-8"), payload_segment.encode("utf-8"), hashlib.sha256
    )
    actual_signature = _b64url_decode(signature_segment)
    if not hmac.compare_digest(expected_signature.digest(), actual_signature):
        raise ValueError("Invalid token signature")

    payload = json.loads(_b64url_decode(payload_segment))
    if int(payload["exp"]) < int(time.time()):
        raise ValueError("Token expired")

    return payload

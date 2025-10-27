# src/domain/services/jwt_service.py
import jwt                # <-- make sure PyJWT is imported as `jwt`
from datetime import datetime, timedelta
from typing import Optional
from src.config.settings import settings
from typing import Any

# Quick runtime sanity check (will raise clear error if wrong jwt module loaded)
_jwt_file = getattr(jwt, "__file__", None)
if not hasattr(jwt, "encode"):
    raise RuntimeError(
        f"Wrong jwt module loaded: {_jwt_file!r}. "
        "This module has no encode(). Remove package 'jwt' and install 'PyJWT'."
    )

class TokenError(Exception):
    pass
class JWTService:
    @staticmethod
    def create_token(user_id: int, expires_hours: int = 24) -> str:
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=expires_hours),
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
        # PyJWT>=2.x returns a str; if bytes, decode to str
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        try:
            payload: dict[str, Any] = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            user_id = payload.get("user_id")
            if user_id is None:
                raise TokenError("Token payload missing subject")
            return int(user_id)
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

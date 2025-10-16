import jwt
from datetime import datetime, timedelta
from src.config.settings import settings

class JWTService:
    @staticmethod
    def create_token(user_id: int) -> str:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS)
        payload = {"sub": user_id, "exp": expire}
        return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

    @staticmethod
    def verify_token(token: str) -> int:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            return payload.get("sub")
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

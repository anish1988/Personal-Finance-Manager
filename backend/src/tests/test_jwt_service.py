# backend/src/tests/test_jwt_service.py
from domain.services.jwt_service import JWTService, TokenError
import time
from config.settings import settings

def test_create_and_decode_token():
    token = JWTService.create_token(user_id=42)
    user_id = JWTService.decode_token(token)
    assert user_id == 42

def test_decode_invalid_token():
    with pytest.raises(TokenError):
        JWTService.decode_token("not_a_token")

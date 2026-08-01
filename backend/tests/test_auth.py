"""
PulseRoute AI - Unit Tests for JWT Authentication
"""
from backend.auth.jwt_handler import create_access_token, verify_token

def test_jwt_flow():
    token = create_access_token("admin", "ADMIN")
    assert token is not None
    assert len(token.split('.')) == 3
    
    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "admin"
    assert payload["role"] == "ADMIN"

def test_invalid_jwt():
    assert verify_token("invalid.token.string") is None

import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .database import db

SECRET_KEY = "dev-secret-key-change-in-production"
ALGORITHM = "HS256"

security = HTTPBearer()

def create_token(user_data: dict) -> str:
    """Create JWT token for user"""
    payload = {
        'user_id': user_data['id'],
        'email': user_data['email'],
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")
    
    user = db.get_user_by_id(payload['user_id'])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

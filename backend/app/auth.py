import httpx
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.db_models import User
from app.config import (
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

security = HTTPBearer()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def exchange_code_for_token(code: str):
    """Exchange GitHub OAuth code for access token"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code,
                },
                headers={"Accept": "application/json"},
            )
            data = response.json()
            
            # Log the response for debugging
            print(f"GitHub OAuth Response: {data}")
            
            # Check for errors in response
            if "error" in data:
                print(f"GitHub OAuth Error: {data.get('error')} - {data.get('error_description')}")
                return None
            
            access_token = data.get("access_token")
            if not access_token:
                print(f"No access token in response: {data}")
            
            return access_token
        except Exception as e:
            print(f"Exception in exchange_code_for_token: {e}")
            import traceback
            traceback.print_exc()
            return None


async def get_github_user(access_token: str):
    """Get GitHub user info using access token"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            )
            data = response.json()
            print(f"GitHub User Response: {data}")
            
            if "message" in data:
                print(f"GitHub User API Error: {data.get('message')}")
            
            return data
        except Exception as e:
            print(f"Exception in get_github_user: {e}")
            import traceback
            traceback.print_exc()
            return {}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Verify JWT token and return current user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Convert to int if it's a string
        if isinstance(user_id, str):
            try:
                user_id = int(user_id)
            except ValueError:
                raise credentials_exception
                
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise credentials_exception
    except Exception as e:
        print(f"Token validation error: {e}")
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        print(f"User not found for id: {user_id}")
        raise credentials_exception
    
    return user

from fastapi import Depends, HTTPException, status
from fake_db import db
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from models import UserInDb, TokenData
from jose import JWTError, jwt
from secrets import SECRET_KEY, ALGORITHM


context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2scheme = OAuth2PasswordBearer(tokenUrl="login")


def verify_password(plain_password, hashed_password):
    return context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_data = db[username]
        return UserInDb(**user_data)
    
def get_user_by_email(db, email: str):
    user = None
    for i in db:
        if email == db[i]["email"]:
            user = db[i]
    user_data = user
    return UserInDb(**user_data)
    
def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def authenticate_user_by_email(db, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta or None=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate"})

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception
    
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credential_exception
    
    return user

async def get_current_active_user(current_user: UserInDb = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user


async def check_admin(current_user: str = Depends(get_current_user)):
    role = current_user.role
    if role != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Feature Restricted for Admin use only.")
    else:
        return current_user

def user_list():
    return db.keys()
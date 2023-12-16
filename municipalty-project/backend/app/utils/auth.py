from fastapi import Depends, HTTPException, status
from app.db.base import usersCol as db
# from fake_db import db
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from app.models.users import UserInDb, TokenData
from jose import JWTError, jwt
from app.core.config import SECRET_KEY, ALGORITHM
from app.core.exceptions import passwordError


context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


def verify_password(plain_password, hashed_password):
    return context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return context.hash(password)

def get_user(db, username: str):
    user_data = db.find_one({"username": f"{username}"}, {'_id':0})

    if user_data:
        return UserInDb(**user_data)
    
def get_user_by_email(db, email: str):
    user_data = db.find_one({"email": email},{'_id': 0})
    if user_data:
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
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'{e}')
    
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


def email_list():
    return [_["email"] for _ in db.find({},{'_id':0})]
def username_list():
    return [_["username"] for _ in db.find({},{'_id':0})]


def create_refresh_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def generate_password_reset_token(email):
    EMAIL_RESET_TOKEN_EXPIRE_HOURS = 10
    delta = timedelta(hours=EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email}, SECRET_KEY, algorithm=ALGORITHM
    )

    return encoded_jwt

def verify_password_reset_token(token: str):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token["sub"]
    except JWTError:
        return None
    
def is_active(username):
    user = get_user(db, username=username)
    inactive_for = datetime.now() - user.last_login
    if inactive_for.days > 30:
        db.update_one({"username": username},
                      {'$set':{'active': False},
                       '$currentDate': { 'lastUpdated': True}})
        
        return {"Action": f"{username} activity status updated!"}
    else:
        return {"No actions needed"}
    

def check_prev_pwd_similarity(email, new_hashed_password):
    user = get_user_by_email(db, email= email)
    old_hashed_password = user.hashed_password

    if not verify_password(new_hashed_password, old_hashed_password):
        return new_hashed_password
    else:
        return passwordError.error
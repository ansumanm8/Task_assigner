from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

SECRET_KEY = 'ce26dd654705344adb9af0a5cda1a126e303a761c44aea1dbaeba279da611406'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 30

# Hard coded database
db = {
    "ansuman":{
        "username":"ansuman",
        "full_name":"Ansuman Maharana",
        "disabled": False,
        "hashed_password":"$2b$12$LL8vPuVUJW6RslzErU.lgeJI8It27phmRapKtmFRdTvun5NifMsb.",
        "email":"ansuman@test.com",
        "roles":["user","admin"],
    },
    "akash":{
        "username":"akash",
        "full_name":"Akash Muni",
        "disabled": False,
        "hashed_password":"$2b$12$QCbYCPu.CU4kEih1aF9MBuLHuCX14A.mpFtmL6zj05FdsYdswFuoS",
        "email":"akash@gmail.com",
        "roles":["user","admin"],
    }
}

# Pydantic models to access data from database
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class User(BaseModel):
    username: str
    email: str or None = None
    full_name: str or None = None
    disabled: bool or None = None
    roles: list

class UserInDb(User):
    hashed_password: str

class CheckUser(BaseModel):
    username: str

context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2scheme = OAuth2PasswordBearer(tokenUrl="login")

# app
app = FastAPI()

# CORS configuration
origins = [
    "http://localhost",
    "http://127.0.0.1:*",
    "http://127.0.0.1:5000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def verify_password(plain_password, hashed_password):
    return context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_data = db[username]
        return UserInDb(**user_data)
    
def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
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

@app.post('/checkUser')
async def check_user(user: CheckUser):
    user = get_user(db, user.username)
    if user:
        return {"username": user.username, "full_name": user.full_name, "email": user.email}
    else:
        return 'User not found!'
    
@app.post('/login', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate"})
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type":"bearer"}

@app.get('/user/data', response_model= User)
async def get_user_data(current_user: User = Depends(get_current_active_user)):
    return current_user

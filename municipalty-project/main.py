from fastapi import FastAPI, Depends, HTTPException, status
import admin, users
from fastapi.security import OAuth2PasswordRequestForm
from models import Token
from services import authenticate_user_by_email, create_access_token, authenticate_user
from fake_db import db
from config import ACCESS_TOKEN_EXPIRES_MINUTES
from datetime import timedelta

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# including router
app.include_router(admin.router)
app.include_router(users.router)

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

@app.post('/login', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username.strip()
    password = form_data.password.strip()
    if "@" in username:
        email = username
        user = authenticate_user_by_email(db, email, password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate"})
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
        access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type":"bearer"}
    else:
        user = authenticate_user(db, username, password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate"})
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
        access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type":"bearer"}
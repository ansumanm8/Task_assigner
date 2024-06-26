from pydantic import BaseModel

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
    department: str or None = None
    role: str

class UserInDb(User):
    hashed_password: str

class NewUser(User):
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class passwordReset(BaseModel):
    new_password: str
    token: str

    
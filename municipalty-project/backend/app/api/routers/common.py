from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models.users import Token, RefreshTokenRequest, passwordReset
from app.utils.auth import authenticate_user_by_email, create_access_token, authenticate_user, email_list, username_list, generate_password_reset_token, get_user_by_email, verify_password_reset_token, check_prev_pwd_similarity, get_password_hash, is_active
from app.db.base import usersCol as db
# from fake_db import db
from app.core.config import ACCESS_TOKEN_EXPIRES_MINUTES, SECRET_KEY, ALGORITHM
from datetime import timedelta
from jose import JWTError, jwt

router = APIRouter(tags=['Common'])

@router.post('/login', response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username.strip()
    password = form_data.password.strip()
    
    if "@" in username:
        email = username
        if email in email_list():
            user = authenticate_user_by_email(db, email, password)
            if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate"})
            
            access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRES_MINUTES))
            access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

            # last_login scope addition
            db.update_one(
                {'email': email},
                {  '$currentDate': {'last_login': True}}
            )

            return {"access_token": access_token, "token_type":"bearer"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
    else:
        if username in username_list():
            user = authenticate_user(db, username, password)
            if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate"})
            
            access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRES_MINUTES))
            access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
            
            # last_login scope addition
            db.update_one(
                {'username': username},
                {  '$currentDate': {'last_login': True}}
            )

            return {"access_token": access_token, "token_type":"bearer"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
        


@router.post("/token/refresh", response_model=dict)
async def refresh_access_token(refresh_token_request: RefreshTokenRequest):
    try:
        decoded_token = jwt.decode(refresh_token_request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = decoded_token["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    access_token_expires = timedelta(minutes=int(access_token_expires))
    access_token = create_access_token(data={"sub": username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post('/password-recovery/{email}')
def recover_password(email: str):
    user = get_user_by_email(db, email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="No user found with mentioned username in the system"
        )
    
    password_reset_token = generate_password_reset_token(email=email)

    return {"message":"Password recovery email sent", "test": password_reset_token}

@router.post('/reset-password')
async def reset_password(data: passwordReset):
    email = verify_password_reset_token(data.token)

    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    user = get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="username does not found!"
        )
    elif not user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    check_complete = check_prev_pwd_similarity(email, newhashed_password= data.new_password)
    if check_complete != data.new_password:
        return check_complete
    else:
        hashed_password = get_password_hash(data.new_password)

        db.update_one(
            {"email": email},
            {
                '$set': { 'hashed_password': hashed_password},
                
                '$currentDate': {'lastUpdated': True}
            }
        )

        return {"message": "Password updated successfully"}
    

@router.get('/check/activeStatus')
async def check_if_active(username):
    return is_active(username=username)


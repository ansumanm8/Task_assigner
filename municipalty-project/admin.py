from fastapi import APIRouter, Depends, status, HTTPException
from models import NewUser
from fake_db import db
from services import check_admin, get_current_user, user_list, get_password_hash


router = APIRouter(prefix='/admin', tags=['Admin'], dependencies=[Depends(check_admin)])


@router.post('/addUser')
async def create_new_user(user: NewUser, admin: str = Depends(get_current_user)):
    data = user
    if data.username in user_list():
        return {"Name error": "User already exists or username already taken."}
    else:
        hashed_pwd = get_password_hash(data.password)
        payload = {f"{data.username}":{
                'username':f"{data.username}",
                'full_name':f"{data.full_name}",
                'disabled': False,
                'hashed_password':f"{hashed_pwd}",
                'email':f"{data.email}",
                'role':f"{data.role}"
        }
        }
        try:
            db.update(payload)
            return {"success":"User Registration Successful"}
        except Exception as e:
            return {"Failed":f"Something went wrong - {e}"}
        

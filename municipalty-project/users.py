from fastapi import APIRouter, Depends
from services import get_current_active_user
from models import User

router = APIRouter(prefix='/users', tags=['User'])

@router.get('/mydata', response_model= User)
async def get_user_data(current_user: User = Depends(get_current_active_user)):
    return current_user
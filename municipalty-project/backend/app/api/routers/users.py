from fastapi import APIRouter, Depends
from app.utils.auth import get_current_active_user
from app.models.users import User
from app.db.base import tasksCol as task_db, usersCol as db

router = APIRouter(prefix='/users', tags=['User'])

@router.get('/mydata', response_model= User)
async def get_user_data(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get('/myTaskList')
async def get_my_task_list(user: str = Depends(get_current_active_user), status: str | None = None):
    query = task_db.find({"assigned_to": user.username,  "status": status}, {'_id': 0})
    my_task_list = list()
    for i in query:
        my_task_list.append(i)

    return my_task_list

@router.get('/myDepartmentTaskList')
async def get_my_department_task_list(user: str = Depends(get_current_active_user), status: str | None = None):
    # user = get_user(db, user)
    if not status:
        query = task_db.find({"department": user.department},{'_id': 0})
        my_department_task_list = list()
        for i in query:
            my_department_task_list.append(i)

        return my_department_task_list
    else:
        query = task_db.find({"department": user.department, "status": status}, {'_id': 0})
        my_department_task_list = list()
        for i in query:
            my_department_task_list.append(i)

        return my_department_task_list

from fastapi import APIRouter, Depends
from app.models.users import NewUser
from app.models.items import newTask
from app.db.base import usersCol as db, tasksCol as task_db
from datetime import datetime
# from fake_db import db
from app.utils.auth import check_admin, get_current_user, get_password_hash, username_list, email_list, get_current_active_user


router = APIRouter(prefix='/admin', tags=['Admin'], dependencies=[Depends(check_admin)])


@router.post('/addUser')
async def create_new_user(user: NewUser, admin: str = Depends(get_current_user)):
    data = user
    if data.username.strip() in username_list() or data.email.strip() in email_list():
        return {"Name error": "Username/Email already exists or taken."}
    else:
        hashed_pwd = get_password_hash(data.password.strip())
        full_name = data.full_name.strip()
        datenow = str(datetime.now())
        payload = {
                'username':f"{data.username.strip()}",
                'full_name':f"{full_name.title()}",
                'email':f"{data.email.strip()}",
                'department': f"{data.department.strip()}",
                'hashed_password':f"{hashed_pwd}",
                'role':f"{data.role.strip()}",
                'createdAt': datetime.fromisoformat(datenow),
                'lastUpdated': datetime.fromisoformat(datenow),
                'last_login': datetime.fromisoformat(datenow),
                'is_active': True,
                'createdBy': f"{admin.username}"
        }

        try:
            db.insert_one(payload)
            return {"success":"User Registration Successful"}
        except Exception as e:
            return {"Failed":f"Something went wrong - {e}"}
        
@router.delete('/deleteUser')
async def delete_user(username: str):
    try:
        db.delete_one({"$or":[{"username": username},{"email": username}]})
        return {"success":"User deleted"}
    except Exception as e:
        return {"Error": f"{e}"}


@router.get('/getAllUser')
def get_all_user():
    users = list()
    for i in db.find({},{'_id': 0, 'hashed_password': 0}):
        users.append(i['username'])

    return users

@router.post('/addTask')
async def add_new_task(data: newTask, admin: str = Depends(get_current_active_user)):
    task = data
    try:
        task_db.insert_one({
            "task_id": "test_01",
            "task_name": task.task_name,
            "department": task.department,
            "assigned_to": task.assigned_to,
            "description": task.task_description,
            "status": task.status,
            "task_created_by": admin.username
        })
        return {"success": "Task created successfully"}
    except Exception as e:
        return {"error": e}
    
@router.get('/taskList')
async def get_all_task():
    query = task_db.find({},{'_id': 0})
    all_task = list()
    for i in query:
        all_task.append(i)

    return all_task


@router.delete('/deleteTask')
async def delete_task(task_id: str):
    taskId = task_id.strip()
    query = task_db.find({"task_id": taskId},{'_id': 0})

    if query:
        for i in query:
            task_db.delete_one({"task_id": i["task_id"]})
            return {"success": "Task deleted successfully"}
        
    else:
        return {"Failed": "Task not found!"}
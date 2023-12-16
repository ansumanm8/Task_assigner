from pydantic import BaseModel

class newTask(BaseModel):
    task_name: str
    department: str
    assigned_to: str
    task_description: str
    status: str
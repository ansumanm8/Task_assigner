from fastapi import APIRouter
from app.api.routers import admin, users, common

app_router = APIRouter(prefix='/api/v1')

app_router.include_router(common.router)
app_router.include_router(admin.router)
app_router.include_router(users.router)
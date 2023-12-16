from fastapi import FastAPI, Depends, HTTPException, status
from app.main import app_router
from fastapi.middleware.cors import CORSMiddleware


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

# home route
@app.get('/')
def home():
    return {"message":"Welcome to the API."}


# including router
app.include_router(app_router)


        
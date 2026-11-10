from fastapi import FastAPI, APIRouter
from .database.conn import Base,engine
from .database import users, transactions,categories,chat_message
from .api import auth,transactions,categories,ai_advisory
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(swagger_ui_parameters={"withCredentials": True})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

api_router = APIRouter(prefix='/api')

api_router.include_router(auth.router)
api_router.include_router(transactions.router)
api_router.include_router(categories.router)

api_router.include_router(ai_advisory.router)

app.include_router(api_router)
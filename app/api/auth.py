from ..database.conn import db_service
from fastapi import APIRouter,Depends,status,Response
from ..services.auth_service import AuthService
from ..models.auth import RegisterForm, LoginForm, ChangePasswordForm
from typing import Annotated
from ..utils.token_service import decode_token

router = APIRouter(prefix='/auth',tags=['Authentication'])

def get_user_service(db : db_service) -> AuthService :
    return AuthService(db_session=db)

AuthServiceDep = Annotated[AuthService , Depends(get_user_service)]

@router.post('/register',status_code=status.HTTP_200_OK)
async def register_service(user_data : RegisterForm,user_service : AuthServiceDep):
    return user_service.register_user(user_data)

@router.post('/login',status_code=status.HTTP_200_OK)
async def login_service(user_data : LoginForm,user_service : AuthServiceDep,response : Response):
    return user_service.login_user(user_data,response)

@router.get('/profile',status_code=status.HTTP_200_OK)
async def profile_data(user_service : AuthServiceDep,user : Annotated[dict,Depends(decode_token)] = None):
    return user_service.get_profile(user)

@router.post('/change-password',status_code=status.HTTP_200_OK)
async def change_password(pass_change : ChangePasswordForm,user_service : AuthServiceDep,user : Annotated[dict,Depends(decode_token)] = None):
    return user_service.change_password(passchange_form=pass_change,user=user)

@router.get('/check-auth',status_code=status.HTTP_200_OK)
async def check_auth(user_service : AuthServiceDep,user : Annotated[dict,Depends(decode_token)] = None):
    return user_service.check_login(user)

@router.get('/logout',status_code=status.HTTP_200_OK)
async def check_auth(user_service : AuthServiceDep, response:Response):
    return user_service.logout(response)
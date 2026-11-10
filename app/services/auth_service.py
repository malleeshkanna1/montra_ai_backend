from pwdlib import PasswordHash
from fastapi import HTTPException,status, Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from ..database.users import User
from ..models.auth import RegisterForm,LoginForm,ChangePasswordForm
from ..utils.token_service import encode_token
from datetime import timedelta
from ..core.config import Config

settings = Config()

passhash = PasswordHash.recommended()

class AuthService:
    def __init__(self,db_session : Session):
        self._db = db_session

    def register_user(self,user_data : RegisterForm):
        stmt = select(User).where(or_(User.username == user_data.username,User.email == user_data.email))
        available_users = self._db.scalar(stmt)
        if available_users is not None :
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,detail='User already exists')
        
        new_user = User(
            name = user_data.name,
            username = user_data.username,
            email = user_data.email,
            password = passhash.hash(user_data.password),
            wallet_balance = 0,
            target_saving_monthly = user_data.target_saving_monthly
        )

        try :
            self._db.add(new_user)
            self._db.commit()
            self._db.refresh(new_user)
        except SQLAlchemyError as exc:
            self._db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='Database cause error') from exc

        return {'status' : True, 'message' : 'User was added successfully'}

    def login_user(self,login_data : LoginForm,response : Response):
        stmt = select(User).where(or_(User.email == login_data.username_or_email,User.username == login_data.username_or_email))
        userAvail = self._db.scalar(stmt)
        if userAvail is None :
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='User not found')

        pass_verify = passhash.verify(login_data.password,userAvail.password)

        if pass_verify is not True:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid Password')

        if userAvail and pass_verify :
            expiry_time = timedelta(minutes=settings.login_expiry_min)
            token = encode_token(userAvail.id,userAvail.username,expiry_time)
            response.set_cookie(key='token',value=token,httponly=True)
            return {'status' : True, 'message' : 'Login Successfully'}

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid Username / Password')


    def get_profile(self,user):
        profile_data = self.user_profile(user)

        if profile_data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Profile Not Found')

        return {
            'status' : True,
            'data' : profile_data
        }

    def user_profile(self,user):
        user_id = user['user_id']
        stmt = select(User).where(User.id == user_id)
        profile_data = self._db.scalar(stmt)

        if profile_data is None :
            raise None

        return {
            'name' : profile_data.name,
            'username' : profile_data.username,
            'email' : profile_data.email,
            'wallet_balance' : profile_data.wallet_balance,
            'target_saving_monthly' : profile_data.target_saving_monthly,
        }

    def change_password(self,passchange_form : ChangePasswordForm ,user : dict):
        stmt = select(User).where(User.id == user['user_id'])
        user_data = self._db.scalar(stmt)

        if user_data is None :
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='User not found')

        if passchange_form.new_password != passchange_form.confirm_password :
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,detail='New Password and Confirm New passowrd is not same.. Please double check')

        check_old_pass = passhash.verify(passchange_form.old_password,user_data.password)

        if not check_old_pass:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Old password is Invalid')

        new_password = passhash.hash(passchange_form.new_password)

        user_data.password = new_password

        try :
            self._db.add(user_data)
            self._db.commit()
            self._db.refresh(user_data)

            return {'status' : True, 'message' : 'Password successfully updated'}

        except SQLAlchemyError as exc:
            self._db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='Database cause error') from exc

    def check_login(self,user:dict):
        return {'status' : True, 'message' : 'Valid'}

    def logout(self,response:Response):
        response.delete_cookie(key='token')
        return {'status' : True,'message' : 'Logout Successful'}

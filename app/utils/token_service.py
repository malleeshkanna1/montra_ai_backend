from fastapi import Cookie, HTTPException, status
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from ..core.config import Config
from typing import Annotated

settings = Config()

def encode_token(user_id : int, uname : str, exp_time : timedelta):
    now = datetime.now(timezone.utc)
    payload = {
        'id' : user_id,
        'sub' : uname,
        'iat' : now,
        'exp' : now + exp_time
    }

    token = jwt.encode(payload=payload,key=settings.secret_key,algorithm=settings.algorithm)
    return token

def decode_token(token : Annotated[str | None, Cookie()] = None):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Authorization Required')
    
    try :
        decoded_token = jwt.decode(
            token,
            key=settings.secret_key,
            algorithms=[settings.algorithm],
            options= {
                'require' : ['id','sub','iat','exp']
            }
        )

        return {
            'user_id' : decoded_token['id'],
            'username' : decoded_token['sub']
        }

    except ExpiredSignatureError as exc :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Token Expired. Please login again') from exc

    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Invalid or Expired Token') from exc


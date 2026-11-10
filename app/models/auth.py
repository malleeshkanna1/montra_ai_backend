from pydantic import BaseModel,Field,EmailStr, ConfigDict

class RegisterForm(BaseModel):
    name : str = Field(min_length=3, max_length=50)
    username : str = Field(min_length=3, max_length=50)
    email : EmailStr
    password : str = Field(min_length=8)
    target_saving_monthly : float = Field(gt=0)

    model_config = ConfigDict(json_schema_extra={
        'examples' : [
            {
                'name' : 'Malleeshkanna',
                'username' : 'malleeshkanna1',
                'email' : 'malleeshkanna1@gmail.com',
                'password' : 'M@lleesh123',
                'target_saving_monthly' : 2000
            }
        ]
    })

class LoginForm(BaseModel):
    username_or_email : str
    password : str = Field(min_length=8)

    model_config = ConfigDict(json_schema_extra={
        'examples' : [{
            'username_or_email' : 'malleeshkanna1',
            'password' : 'M@lleesh123'
        }]
    })

class ChangePasswordForm(BaseModel) :
    old_password : str = Field(min_length=8)
    new_password : str = Field(min_length=8)
    confirm_password : str = Field(min_length=8)

    model_config = ConfigDict(json_schema_extra={
        'examples' : [
            {
                'old_password' : 'M@lleesh123',
                'new_password' : 'M@lleesh345',
                'confirm_password' : 'M@lleesh345'
            }
        ]
    })
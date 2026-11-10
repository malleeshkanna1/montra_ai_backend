from .conn import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer,String,Float

class User(Base):
    __tablename__ = 'users'

    id : Mapped[int] = mapped_column(Integer,primary_key=True)
    name : Mapped[str] = mapped_column(String(50))
    username : Mapped[str] = mapped_column(String(50))
    email : Mapped[str] = mapped_column(String(50))
    password : Mapped[str] = mapped_column(String(100))
    wallet_balance : Mapped[float] = mapped_column(Float,default=0)
    target_saving_monthly : Mapped[float] = mapped_column(Float)
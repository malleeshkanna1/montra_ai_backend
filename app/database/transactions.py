from .conn import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer,String

class Transaction(Base):
    __tablename__ = 'transactions'

    id : Mapped[int] = mapped_column(Integer,primary_key=True)
    user_id : Mapped[int] = mapped_column(Integer)
    amount : Mapped[int] = mapped_column(Integer)
    date : Mapped[str] = mapped_column(String(50))
    mode : Mapped[str] = mapped_column(String(50))
    notes : Mapped[str] = mapped_column(String(50))
    payment : Mapped[str] = mapped_column(String(50))
    category : Mapped[str] = mapped_column(String(50))
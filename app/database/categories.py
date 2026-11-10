from .conn import Base
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import Integer,String
from typing import Literal

class Category(Base):
    __tablename__ = 'categories'

    id : Mapped[int] = mapped_column(Integer,primary_key=True)
    category : Mapped[str] = mapped_column(String(100))
    description : Mapped[str] = mapped_column(String(256))
    expense_type : Mapped[str] = mapped_column(String(20))
    expense_classification: Mapped[str] = mapped_column(String(100),default=None)
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from ..models.categories import AddCategoriesForm
from fastapi import HTTPException,status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from ..database.categories import Category
from typing import Literal

class CategoriesService():

    def __init__(self,session : Session):
        self._db = session

    def addCategories(self, categories_form_resp : AddCategoriesForm):
        new_category = Category(
            category= categories_form_resp.category,
            description= categories_form_resp.description,
            expense_type= categories_form_resp.expense_type,
            expense_classification= categories_form_resp.expense_classification
        )

        try:
            self._db.add(new_category)
            self._db.commit()
            self._db.refresh(new_category)
            return {'status' : True, 'message' : 'New Category Added successfully'}
        except SQLAlchemyError as exc :
            self._db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail='Some Error Occured') from exc

    def addCategoriesBulk(self,categories_form_resp: list[AddCategoriesForm]):
        new_categories = [
            Category(
                category=item.category,
                description=item.description,
                expense_type=item.expense_type,
                expense_classification=item.expense_classification
            )
            for item in categories_form_resp
        ]

        try:
            self._db.add_all(new_categories)
            self._db.commit()

            return {
                "status": True,
                "message": "Categories added successfully",
                "total": len(new_categories)
            }

        except SQLAlchemyError as exc:
            self._db.rollback()
            print(exc._message())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Some Error Occurred"
            ) from exc

    def get_categories(self, expense_type: Literal["income", "expense"]):
        stmt = select(Category).where(Category.expense_type == expense_type)
        categories_data = self._db.scalars(stmt).all()
        if not categories_data:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "status": False,
                    "message": "Categories not found"
                }
            )

        return categories_data
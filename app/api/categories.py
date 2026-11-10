from ..services.categories_service import CategoriesService
from ..database.conn import get_db
from fastapi import APIRouter,status,Depends
from sqlalchemy.orm import Session
from typing import Annotated,Literal
from ..models.categories import AddCategoriesForm
from ..utils.token_service import decode_token

router = APIRouter(prefix='/categories',tags=['Categories'])

def get_category_service(db: Session = Depends(get_db)) -> CategoriesService:
    return CategoriesService(session=db)

CategoryDeps = Annotated[CategoriesService,Depends(get_category_service)]
TokenDep = Annotated[dict,Depends(decode_token)]

@router.post('/add',status_code=status.HTTP_200_OK)
def add_categories(category_service : CategoryDeps,category_add_form : AddCategoriesForm, user : TokenDep):
    return category_service.addCategories(category_add_form)

@router.post("/bulk-add", status_code=status.HTTP_201_CREATED)
def add_categories_bulk(categories: list[AddCategoriesForm],category_service: CategoryDeps,user: TokenDep):
    return category_service.addCategoriesBulk(categories)

@router.get("/category/{expense_type}", status_code=status.HTTP_200_OK)
def get_categories_list(expense_type: Literal["income", "expense"],category_service: CategoryDeps):
    return category_service.get_categories(expense_type=expense_type)
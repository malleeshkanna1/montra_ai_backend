from fastapi import APIRouter, status, Depends,Path,Query,HTTPException
from typing import Annotated
from ..utils.token_service import decode_token
from ..services.transactions_service import TransactionsService
from ..models.transactions import AddUpdateTransactionForm, DateFilterForm
from ..database.conn import get_db
from sqlalchemy.orm import Session
from typing import Literal
from datetime import date

router = APIRouter(prefix='/transaction',tags=['Transactions'])

def get_transaction_service(db: Session = Depends(get_db)) -> TransactionsService:
    return TransactionsService(session=db)

TransactionDeps = Annotated[TransactionsService,Depends(get_transaction_service)]
TokenDep = Annotated[dict,Depends(decode_token)]

@router.get("/all", status_code=status.HTTP_200_OK)
def all_transactions(
    transaction_service: TransactionDeps,
    user: TokenDep,
    period: Literal[
        "all_time",
        "today",
        "this_week",
        "this_month",
        "this_year"
    ] = Query(default="all_time"),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
):

    if (start_date is None) != (end_date is None):
        raise HTTPException(
            status_code=400,
            detail="Both start_date and end_date are required"
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date cannot be after end date"
        )

    return transaction_service.get_all_transactions(
        user=user,
        period=period,
        start_date=start_date,
        end_date=end_date
    )


@router.get('/get/{transac_id}',status_code=status.HTTP_200_OK)
async def get_transaction_data(transac_service : TransactionDeps,user : TokenDep,transac_id : int = Path(gt=0) ):
    return transac_service.get_single_transaction(user,transac_id)

@router.get('/recent',status_code=status.HTTP_200_OK)
async def get_recent_fiv_transaction(transac_service : TransactionDeps,user:TokenDep):
    return transac_service.get_recent_fiv_transaction(user)

@router.post('/filter-by-date',status_code = status.HTTP_200_OK)
async def filter_transaction_by_date(transac_service : TransactionDeps,date_filter_form : DateFilterForm,user:TokenDep):
    return transac_service.get_transactions_based_on_date(date_filter_form,user)

@router.post('/add',status_code=status.HTTP_200_OK)
def add_transactions(transaction_service:TransactionDeps,user : TokenDep,transaction_form : AddUpdateTransactionForm):
    return transaction_service.save_transaction(transaction_form,user)

@router.put('/update/{transac_id}',status_code=status.HTTP_200_OK)
def update_transaction(transaction_service:TransactionDeps,update_form:AddUpdateTransactionForm,user : TokenDep,transac_id:int=Path(gt=0)):
    return transaction_service.update_transactions(transac_id,update_form,user)

@router.delete('/delete/{transac_id}',status_code=status.HTTP_200_OK)
def delete_transaction(transac_service : TransactionDeps, user:TokenDep, transac_id : int = Path(gt=0) ):
    return transac_service.delete_transaction(transac_id,user)
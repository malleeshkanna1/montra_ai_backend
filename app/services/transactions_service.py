from sqlalchemy import select, and_, func, case
from sqlalchemy.orm import Session
from ..database.transactions import Transaction
from ..models.transactions import AddUpdateTransactionForm, DateFilterForm
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from ..database.users import User
from datetime import date, timedelta
from typing import Literal

TransactionPeriod = Literal[
    "all_time",
    "today",
    "this_week",
    "this_month",
    "this_year",
]

class TransactionsService():
    def __init__(self, session : Session):
        self._db = session

    def save_transaction(
        self,
        transaction_form: AddUpdateTransactionForm,
        user: dict
    ):
        try:
            # Fetch the actual SQLAlchemy profile model
            stmt = select(User).where(
                User.id == user["user_id"]
            )
            user_profile = self._db.scalars(stmt).first()

            if user_profile is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )

            amount = transaction_form.amount

            # Update wallet balance
            if transaction_form.mode == "income":
                user_profile.wallet_balance += amount
            elif transaction_form.mode == "expense":
                user_profile.wallet_balance -= amount

            # Create transaction
            new_transaction = Transaction(
                user_id=user["user_id"],
                amount=amount,
                date=transaction_form.date,
                mode=transaction_form.mode,
                notes=transaction_form.notes,
                payment=transaction_form.payment,
                category=transaction_form.category,
            )

            self._db.add(new_transaction)

            # Save transaction and wallet balance together
            self._db.commit()
            self._db.refresh(new_transaction)

            return {
                "status": True,
                "message": "New transaction added successfully",
                "wallet_balance": user_profile.wallet_balance
            }

        except SQLAlchemyError as exc:
            self._db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Some error occurred"
            ) from exc

    def get_all_transactions(
        self,
        user: dict,
        period: TransactionPeriod = "all_time",
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        today = date.today()
        
        

        # Validate custom date range
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

        # Custom date range takes priority
        if start_date and end_date:
            filter_start = start_date
            filter_end = end_date + timedelta(days=1)

        else:
            filter_start = None
            filter_end = None

            if period == "today":
                filter_start = today
                filter_end = today + timedelta(days=1)

            elif period == "this_week":
                filter_start = today - timedelta(days=today.weekday())
                filter_end = filter_start + timedelta(days=7)

            elif period == "this_month":
                filter_start = today.replace(day=1)

                if today.month == 12:
                    filter_end = date(today.year + 1, 1, 1)
                else:
                    filter_end = date(today.year, today.month + 1, 1)

            elif period == "this_year":
                filter_start = date(today.year, 1, 1)
                filter_end = date(today.year + 1, 1, 1)

            elif period != "all_time":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid transaction period"
                )

        # Base query
        stmt = (
            select(
                Transaction.id,
                Transaction.amount,
                Transaction.date,
                Transaction.mode,
                Transaction.notes,
                Transaction.payment,
                Transaction.category,
            )
            .where(Transaction.user_id == user["user_id"])
        )

        # Apply date filters
        if filter_start and filter_end:
            stmt = stmt.where(
                Transaction.date >= filter_start,
                Transaction.date < filter_end
            )

        stmt = stmt.order_by(
            Transaction.date.desc(),
            Transaction.id.desc()
        )

        transactions = self._db.execute(stmt).mappings().all()
        

        return {
            "status": True,
            "data": [dict(transaction) for transaction in transactions]
        }

    def get_single_transaction(self, user : dict, transac_id : int):
        stmt = select(Transaction.id,Transaction.amount,Transaction.date,Transaction.mode,Transaction.notes,Transaction.payment).where(and_(
            Transaction.user_id == user['user_id'],
            Transaction.id == transac_id
        ))

        transaction_data = self._db.execute(stmt).mappings().first()

        if transaction_data is None :
           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Transaction Data not found")

        return {'status' : True, 'data' : transaction_data}

    def get_recent_fiv_transaction(self,user:dict):
        stmt = select(Transaction).where(Transaction.user_id == user['user_id']).order_by(
        Transaction.date.desc(),
        Transaction.id.desc()
        ).limit(5)
        transaction_data = self._db.scalars(stmt).all()
        if len(transaction_data) > 0:
            return {'status':True,'data':transaction_data}
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={'status':False,'message' : 'Transaction data not found'})


    def get_transactions_based_on_date(
        self,
        date_filter_form: DateFilterForm,
        user: dict
    ):
        user_id = user["user_id"]

        try:
            # 1. Calculate previous balance before start date
            previous_stmt = select(
                func.coalesce(
                    func.sum(
                        case(
                            (Transaction.mode == "income", Transaction.amount),
                            (Transaction.mode == "expense", -Transaction.amount),
                            else_=0
                        )
                    ),
                    0
                )
            ).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.date < date_filter_form.start_date
                )
            )

            previous_balance = self._db.scalar(previous_stmt) or 0

            # 2. Calculate total income and expenses in date range
            summary_stmt = select(
                func.coalesce(
                    func.sum(
                        case(
                            (Transaction.mode == "income", Transaction.amount),
                            else_=0
                        )
                    ),
                    0
                ).label("total_income"),

                func.coalesce(
                    func.sum(
                        case(
                            (Transaction.mode == "expense", Transaction.amount),
                            else_=0
                        )
                    ),
                    0
                ).label("total_expenses")
            ).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.date.between(
                        date_filter_form.start_date,
                        date_filter_form.end_date
                    )
                )
            )

            summary = self._db.execute(summary_stmt).one()

            total_income = summary.total_income
            total_expenses = summary.total_expenses

            # 3. Calculate total balance
            total_balance = (
                previous_balance + total_income - total_expenses
            )

            return {
                "status": True,
                "data": {
                    "previous_balance": previous_balance,
                    "total_income": total_income,
                    "total_expenses": total_expenses,
                    "total_balance": total_balance
                }
            }

        except SQLAlchemyError as exc:
            self._db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to fetch transaction summary"
            ) from exc
    
    def update_transactions(
            self,
            transac_id: int,
            update_form: AddUpdateTransactionForm,
            user: dict
        ):
        try:
            stmt = select(Transaction).where(
                and_(
                    Transaction.user_id == user["user_id"],
                    Transaction.id == transac_id
                )
            )

            transaction_data = self._db.scalars(stmt).first()

            if transaction_data is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Transaction not found"
                )

            # Fetch actual SQLAlchemy profile model
            profile_stmt = select(User).where(
                User.id == user["user_id"]
            )
            user_profile = self._db.scalars(profile_stmt).first()

            if user_profile is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )

            # 1. Reverse old transaction effect
            if transaction_data.mode == "income":
                user_profile.wallet_balance -= transaction_data.amount
            elif transaction_data.mode == "expense":
                user_profile.wallet_balance += transaction_data.amount

            # 2. Apply new transaction effect
            if update_form.mode == "income":
                user_profile.wallet_balance += update_form.amount
            elif update_form.mode == "expense":
                user_profile.wallet_balance -= update_form.amount
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid transaction type"
                )

            # 3. Update transaction details
            transaction_data.payment = update_form.payment
            transaction_data.amount = update_form.amount
            transaction_data.mode = update_form.mode
            transaction_data.notes = update_form.notes
            transaction_data.category = update_form.category
            transaction_data.date = update_form.date

            self._db.commit()
            self._db.refresh(transaction_data)

            return {
                "status": True,
                "message": "Transaction updated successfully",
                "wallet_balance": user_profile.wallet_balance
            }

        except SQLAlchemyError as exc:
            self._db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Some error happened on our side"
            ) from exc
        
    def delete_transaction(self, transaction_id: int, user: dict):

        try:
            stmt = select(Transaction).where(
                and_(
                    Transaction.id == transaction_id,
                    Transaction.user_id == user["user_id"]
                )
            )

            transaction_data = self._db.scalars(stmt).first()

            if transaction_data is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Transaction data not found"
                )

            # Fetch actual SQLAlchemy profile model
            profile_stmt = select(User).where(
                User.id == user["user_id"]
            )
            user_profile = self._db.scalars(profile_stmt).first()

            if user_profile is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )

            # Reverse the deleted transaction effect
            if transaction_data.mode == "income":
                user_profile.wallet_balance -= transaction_data.amount

            elif transaction_data.mode == "expense":
                user_profile.wallet_balance += transaction_data.amount

            self._db.delete(transaction_data)

            self._db.commit()

            return {
                "status": True,
                "message": "Transaction deleted successfully",
                "wallet_balance": user_profile.wallet_balance
            }

        except SQLAlchemyError as exc:
            self._db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Some error occurred on our side"
            ) from exc
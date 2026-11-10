from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database.conn import get_db

from ..services.transactions_service import Transaction
from ..services.categories_service import Category

from ..models.ai import AIChatRequest

from ..database.chat_message import ChatMessage
from ..services.ai_advisory_service import AIAdvisoryService
from ..utils.token_service import decode_token
from typing import Annotated


router = APIRouter(
    prefix="/ai",
    tags=["AI Advisory"]
)


def get_ai_service(
    db: Session = Depends(get_db)
):

    return AIAdvisoryService(
        db=db,
        transaction_model=Transaction,
        category_model=Category,
        chat_message_model=ChatMessage
    )

AIServiceDep = Annotated[AIAdvisoryService,Depends(get_ai_service)]
TokenDep = Annotated[dict,Depends(decode_token)]


@router.post("/chat")
def send_message(
    request: AIChatRequest,
    user: TokenDep,
    service: AIServiceDep
):

    return service.send_message(
        user=user,
        request=request
    )


@router.get("/history")
def get_history(
    user: TokenDep,
    service: AIServiceDep
):

    return service.get_chat_history(
        user=user
    )
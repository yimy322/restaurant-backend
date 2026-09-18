from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from app.database import get_session
from app.services.restaurant_service import (
    get_menu,
    get_opening_hours,
    request_table_reservation,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, session: Session = Depends(get_session)):
    # TODO: aquí se llama a la API de Claude/OpenAI pasandole request.message
    # y las 3 funciones de abajo como "tools" (function calling). El modelo
    # decide cuál ejecutar según lo que pida el usuario:
    #
    #   get_menu(session)
    #   get_opening_hours(session)
    #   request_table_reservation(session, customer_name=..., phone=..., ...)
    #
    # y luego redacta la respuesta final en lenguaje natural con el resultado.
    return ChatResponse(reply="Endpoint de chat listo, falta conectar el LLM.")
import shutil
from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import Dish, DishCreate
from pathlib import Path
from fastapi import File, HTTPException, UploadFile 

router = APIRouter(prefix="/api/dishes", tags=["dishes"])

@router.get("/", response_model=List[Dish])
def list_dishes(session: Session = Depends(get_session)):
    return session.exec(select(Dish)).all()


@router.post("/", response_model=Dish)
def create_dish(dish_in: DishCreate, session: Session = Depends(get_session)):
    dish = Dish.model_validate(dish_in)
    session.add(dish)
    session.commit()
    session.refresh(dish)
    return dish

# para las imagenes
IMAGES_DIR = Path("static/images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/{dish_id}/image", response_model=Dish)
def upload_dish_image(
    dish_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    dish = session.get(Dish, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    extension = Path(file.filename).suffix
    filename = f"dish_{dish_id}{extension}"
    file_path = IMAGES_DIR / filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    dish.image_url = f"/static/images/{filename}"
    session.add(dish)
    session.commit()
    session.refresh(dish)
    return dish
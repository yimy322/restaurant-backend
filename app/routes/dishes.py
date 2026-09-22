import shutil
from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import Dish, DishCreate
from pathlib import Path
from fastapi import File, HTTPException, UploadFile 
from app.security import get_current_admin

router = APIRouter(prefix="/api/dishes", tags=["dishes"])

@router.get("/", response_model=List[Dish])
def list_dishes(session: Session = Depends(get_session)):
    return session.exec(select(Dish)).all()

# crear plato
@router.post("/", response_model=Dish)
def create_dish(
    dish_in: DishCreate,
    session: Session = Depends(get_session),
    current_admin: str = Depends(get_current_admin),
):
    dish = Dish.model_validate(dish_in)
    session.add(dish)
    session.commit()
    session.refresh(dish)
    return dish

# actualizar plato
@router.put("/{dish_id}", response_model=Dish)
def update_dish(
    dish_id: int,
    dish_in: DishCreate,
    session: Session = Depends(get_session),
    current_admin: str = Depends(get_current_admin),
):
    dish = session.get(Dish, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    for field, value in dish_in.model_dump().items():
        setattr(dish, field, value)

    session.add(dish)
    session.commit()
    session.refresh(dish)
    return dish

# eliminar plato
@router.delete("/{dish_id}", status_code=204)
def delete_dish(
    dish_id: int,
    session: Session = Depends(get_session),
    current_admin: str = Depends(get_current_admin),
):
    dish = session.get(Dish, dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    session.delete(dish)
    session.commit()

# para las imagenes
IMAGES_DIR = Path("static/images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/{dish_id}/image", response_model=Dish)
def upload_dish_image(
    dish_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_admin: str = Depends(get_current_admin),
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
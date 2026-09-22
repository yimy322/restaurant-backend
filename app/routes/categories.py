from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Category, CategoryCreate, Dish
from app.security import get_current_admin

router = APIRouter(prefix="/api/categories", tags=["categories"])

@router.get("/", response_model=List[Category])
def list_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()

# crear categoria
@router.post("/", response_model=Category)
def create_category(
    category_in: CategoryCreate,
    session: Session = Depends(get_session),
    current_admin: str = Depends(get_current_admin),
):
    category = Category.model_validate(category_in)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

# actualizar categoria
@router.put("/{category_id}", response_model=Category)
def update_category(
    category_id: int,
    category_in: CategoryCreate,
    session: Session = Depends(get_session),
    current_admin: str = Depends(get_current_admin),
):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for field, value in category_in.model_dump().items():
        setattr(category, field, value)

    session.add(category)
    session.commit()
    session.refresh(category)
    return category

# eliminar categoria
@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    session: Session = Depends(get_session),
    current_admin: str = Depends(get_current_admin),
):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    dish_in_category = session.exec(select(Dish).where(Dish.category_id == category_id)).first()
    if dish_in_category:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar la categoría porque tiene platos asociados.",
        )

    session.delete(category)
    session.commit()
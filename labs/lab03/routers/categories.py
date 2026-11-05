from typing import Annotated
from fastapi import APIRouter, HTTPException, Path, status

from labs.lab03.repository import (
    ConflictError,
    NotFoundError,
    create_category,
    delete_category,
    get_categories,
)
from labs.lab03.schemas import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(
    "",
    response_model=list[CategoryRead],
    summary="Отримати список усіх категорій",
    description="Повертає список категорій, відсортованих за зростанням id.",
)
def list_categories() -> list[dict]:
    """Отримати всі категорії."""
    return get_categories()


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Створити нову категорію",
    responses={
        409: {"description": "Категорія з такою назвою вже існує"},
        422: {"description": "Помилка валідації назви"},
    },
)
def add_category(category_in: CategoryCreate) -> dict:
    """Створити категорію."""
    try:
        return create_category(category_in)
    except ConflictError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(err),
        ) from err


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити порожню категорію",
    responses={
        404: {"description": "Категорію не знайдено"},
        409: {"description": "Категорія містить пов'язані записи"},
    },
)
def remove_category(
    category_id: Annotated[int, Path(gt=0, description="ID категорії")],
) -> None:
    """Видалити категорію за id."""
    try:
        delete_category(category_id)
    except NotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except ConflictError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(err),
        ) from err
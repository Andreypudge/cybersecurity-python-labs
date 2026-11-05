"""Pydantic-моделі для валідації запитів та серіалізації відповідей."""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    """Базова модель для категорій."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )
    name: str = Field(
        min_length=2,
        max_length=40,
        description="Унікальна назва категорії",
    )


class CategoryCreate(CategoryBase):
    """Модель запиту для створення категорії."""

    pass


class CategoryRead(CategoryBase):
    """Модель відповіді з даними категорії."""

    id: int = Field(gt=0, description="Унікальний числовий ідентифікатор")


class RecordCreate(BaseModel):
    """Модель запиту для створення запису вимірювання."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )
    code: str = Field(
        min_length=3,
        max_length=40,
        description="Унікальний код запису",
    )
    title: str = Field(
        min_length=3,
        max_length=120,
        description="Назва запису вимірювання",
    )
    category_id: int = Field(
        gt=0,
        description="Ідентифікатор пов'язаної категорії",
    )
    value: float = Field(
        ge=0.0,
        allow_inf_nan=False,
        description="Тривалість опрацювання у хвилинах (не менше 0)",
    )
    status: Literal["new", "in_progress", "done"] = Field(
        description="Стан опрацювання повідомлення",
    )


class RecordReplace(RecordCreate):
    """Модель запиту для повної заміни полів запису (PUT)."""

    pass


class RecordRead(RecordCreate):
    """Модель відповіді з даними запису."""

    id: int = Field(gt=0, description="Унікальний числовий ідентифікатор")
    category_name: str = Field(
        description="Назва категорії, отримана через зв'язок JOIN",
    )
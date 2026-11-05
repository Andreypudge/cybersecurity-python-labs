from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI
import shared.student as student_info
from labs.lab03.config import DOMAIN_NAME, THRESHOLD, UNIT, VARIANT_NUMBER
from labs.lab03.database import initialize_database
from labs.lab03.routers.categories import router as categories_router
from labs.lab03.routers.records import router as records_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    initialize_database()
    yield


description_text = f"""
### Лабораторна робота №3 (Варіант {VARIANT_NUMBER})
**Предметна область**: {DOMAIN_NAME}

* **Одиниця вимірювання**: `{UNIT}`
* **Поріг оперативного реагування**: `{THRESHOLD}` хв
* **Категорії**: `siem`, `helpdesk`, `monitoring`
"""

app = FastAPI(
    title="Security Event Processing API",
    description=description_text,
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(categories_router)
app.include_router(records_router)


@app.get(
    "/ping",
    summary="Перевірка доступності сервісу",
    tags=["service"],
)
def ping() -> dict[str, str]:
    """Повернути стан працездатності сервісу."""
    return {"status": "ok"}


@app.get(
    "/student",
    summary="Інформація про автора роботи",
    tags=["service"],
)
def get_student() -> dict[str, Any]:
    """Повернути дані студента з shared/student.py."""
    return {
        "student_name": getattr(
            student_info,
            "student_name",
            getattr(student_info, "STUDENT_NAME", "Левченко Андрій Валерійович"),
        ),
        "group_name": getattr(
            student_info,
            "group_name",
            getattr(student_info, "GROUP_NAME", "КБ-209"),
        ),
        "variant_number": getattr(
            student_info,
            "variant_number",
            getattr(student_info, "VARIANT_NUMBER", VARIANT_NUMBER),
        ),
    }
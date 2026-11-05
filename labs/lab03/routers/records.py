"""Маршрути для роботи із записами вимірювань."""

from typing import Annotated, Literal
from fastapi import APIRouter, Body, HTTPException, Path, Query, status

from labs.lab03.repository import (
    ConflictError,
    NotFoundError,
    create_record,
    create_records_bulk,
    delete_record,
    get_record_by_id,
    get_records,
    update_record,
)
from labs.lab03.schemas import RecordCreate, RecordRead, RecordReplace

router = APIRouter(prefix="/records", tags=["records"])


@router.get(
    "",
    response_model=list[RecordRead],
    summary="Отримати вибірку записів із фільтрами",
    description="Повертає відсортований за id список записів з урахуванням фільтрів та пагінації.",
)
def list_records(
    category_id: Annotated[
        int | None, Query(gt=0, description="Фільтр за id категорії")
    ] = None,
    record_status: Annotated[
        Literal["new", "in_progress", "done"] | None,
        Query(alias="status", description="Фільтр за статусом опрацювання"),
    ] = None,
    min_value: Annotated[
        float | None,
        Query(ge=0.0, description="Фільтр мінімального часу (хв)"),
    ] = None,
    q: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=120,
            description="Буквальний пошук підрядка в назві",
        ),
    ] = None,
    limit: Annotated[
        int, Query(ge=1, le=100, description="Кількість записів на сторінку")
    ] = 20,
    offset: Annotated[
        int, Query(ge=0, description="Кількість пропущених записів")
    ] = 0,
) -> list[dict]:
    """Отримати список записів із фільтрами."""
    return get_records(
        category_id=category_id,
        status=record_status,
        min_value=min_value,
        q=q,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{record_id}",
    response_model=RecordRead,
    summary="Отримати один запис за id",
    responses={404: {"description": "Запис не знайдено"}},
)
def read_record(
    record_id: Annotated[int, Path(gt=0, description="ID запису")],
) -> dict:
    """Отримати запис за його id."""
    record = get_record_by_id(record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запис із id={record_id} не знайдено.",
        )
    return record


@router.post(
    "",
    response_model=RecordRead,
    status_code=status.HTTP_201_CREATED,
    summary="Створити окремий запис",
    responses={
        404: {"description": "Категорію не знайдено"},
        409: {"description": "Код запису вже існує"},
        422: {"description": "Помилка валідації вхідних даних"},
    },
)
def add_record(record_in: RecordCreate) -> dict:
    """Створити новий запис вимірювання."""
    try:
        return create_record(record_in)
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


@router.put(
    "/{record_id}",
    response_model=RecordRead,
    summary="Повністю замінити наявний запис (PUT)",
    responses={
        404: {"description": "Запис або категорію не знайдено"},
        409: {"description": "Код запису вже існує"},
        422: {"description": "Помилка валідації вхідних даних"},
    },
)
def replace_record(
    record_id: Annotated[int, Path(gt=0, description="ID запису")],
    record_in: RecordReplace,
) -> dict:
    """Повністю оновити поля запису."""
    try:
        return update_record(record_id, record_in)
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


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити запис за id",
    responses={404: {"description": "Запис не знайдено"}},
)
def remove_record(
    record_id: Annotated[int, Path(gt=0, description="ID запису")],
) -> None:
    """Видалити запис."""
    try:
        delete_record(record_id)
    except NotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err


@router.post(
    "/bulk",
    response_model=list[RecordRead],
    status_code=status.HTTP_201_CREATED,
    summary="Пакетне створення записів в одній транзакції",
    responses={
        404: {"description": "Одна або декілька категорій не існують"},
        409: {"description": "Дублікат коду в базі чи всередині пакета"},
        422: {"description": "Помилка валідації розміру або структури пакета"},
    },
)
def add_records_bulk(
    records_in: Annotated[
        list[RecordCreate],
        Body(
            min_length=1,
            max_length=100,
            description="Масив записів (від 1 до 100 елементів)",
        ),
    ],
) -> list[dict]:
    """Створити масив записів в атомарній транзакції."""
    try:
        return create_records_bulk(records_in)
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
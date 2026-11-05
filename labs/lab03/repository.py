import sqlite3
from contextlib import closing
from typing import Any
from labs.lab03.database import get_connection
from labs.lab03.schemas import CategoryCreate, RecordCreate, RecordReplace


class RepositoryError(Exception):
    pass


class NotFoundError(RepositoryError):
    pass


class ConflictError(RepositoryError):
    pass



def get_categories() -> list[dict[str, Any]]:
    with closing(get_connection()) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY id ASC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_category_by_id(category_id: int) -> dict[str, Any] | None:
    with closing(get_connection()) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, name FROM categories WHERE id = ?",
            (category_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def create_category(category_in: CategoryCreate) -> dict[str, Any]:
    with closing(get_connection()) as connection:
        try:
            with connection:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO categories (name) VALUES (?)",
                    (category_in.name,),
                )
                category_id = cursor.lastrowid
            return {"id": category_id, "name": category_in.name}
        except sqlite3.IntegrityError as err:
            raise ConflictError(
                f"Категорія з назвою '{category_in.name}' вже існує."
            ) from err


def delete_category(category_id: int) -> None:
    with closing(get_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM categories WHERE id = ?", (category_id,))
        if not cursor.fetchone():
            raise NotFoundError(f"Категорію з id={category_id} не знайдено.")

        try:
            with connection:
                cursor.execute(
                    "DELETE FROM categories WHERE id = ?",
                    (category_id,),
                )
        except sqlite3.IntegrityError as err:
            raise ConflictError(
                "Неможливо видалити категорію, яка містить пов'язані записи."
            ) from err


def get_record_by_id(record_id: int) -> dict[str, Any] | None:
    """Отримати запис за id разом із назвою категорії через JOIN."""
    with closing(get_connection()) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                r.id,
                r.code,
                r.title,
                r.category_id,
                r.value,
                r.status,
                c.name AS category_name
            FROM records r
            JOIN categories c ON r.category_id = c.id
            WHERE r.id = ?
            """,
            (record_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_records(
    category_id: int | None = None,
    status: str | None = None,
    min_value: float | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, Any]]:
    query = """
        SELECT
            r.id,
            r.code,
            r.title,
            r.category_id,
            r.value,
            r.status,
            c.name AS category_name
        FROM records r
        JOIN categories c ON r.category_id = c.id
    """
    conditions: list[str] = []
    params: list[Any] = []

    if category_id is not None:
        conditions.append("r.category_id = ?")
        params.append(category_id)

    if status is not None:
        conditions.append("r.status = ?")
        params.append(status)

    if min_value is not None:
        conditions.append("r.value >= ?")
        params.append(min_value)

    if q is not None:
        conditions.append("instr(r.title, ?) > 0")
        params.append(q)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY r.id ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with closing(get_connection()) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def create_record(record_in: RecordCreate) -> dict[str, Any]:
    with closing(get_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id FROM categories WHERE id = ?",
            (record_in.category_id,),
        )
        if not cursor.fetchone():
            raise NotFoundError(
                f"Категорію з id={record_in.category_id} не знайдено."
            )

        try:
            with connection:
                cursor.execute(
                    """
                    INSERT INTO records (code, title, category_id, value, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        record_in.code,
                        record_in.title,
                        record_in.category_id,
                        record_in.value,
                        record_in.status,
                    ),
                )
                record_id = cursor.lastrowid
        except sqlite3.IntegrityError as err:
            raise ConflictError(
                f"Запис із кодом '{record_in.code}' вже існує."
            ) from err

    record = get_record_by_id(record_id)
    if not record:
        raise RepositoryError("Не вдалося отримати створений запис.")
    return record


def update_record(record_id: int, record_in: RecordReplace) -> dict[str, Any]:
    """Повністю замінити змінювані поля наявного запису (PUT)."""
    with closing(get_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM records WHERE id = ?", (record_id,))
        if not cursor.fetchone():
            raise NotFoundError(f"Запис із id={record_id} не знайдено.")
        
        cursor.execute(
            "SELECT id FROM categories WHERE id = ?",
            (record_in.category_id,),
        )
        if not cursor.fetchone():
            raise NotFoundError(
                f"Категорію з id={record_in.category_id} не знайдено."
            )

        try:
            with connection:
                cursor.execute(
                    """
                    UPDATE records
                    SET code = ?, title = ?, category_id = ?, value = ?, status = ?
                    WHERE id = ?
                    """,
                    (
                        record_in.code,
                        record_in.title,
                        record_in.category_id,
                        record_in.value,
                        record_in.status,
                        record_id,
                    ),
                )
        except sqlite3.IntegrityError as err:
            raise ConflictError(
                f"Запис із кодом '{record_in.code}' вже існує."
            ) from err

    updated = get_record_by_id(record_id)
    if not updated:
        raise RepositoryError("Не вдалося отримати оновлений запис.")
    return updated


def delete_record(record_id: int) -> None:
    with closing(get_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM records WHERE id = ?", (record_id,))
        if not cursor.fetchone():
            raise NotFoundError(f"Запис із id={record_id} не знайдено.")

        with connection:
            cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))


def create_records_bulk(records_in: list[RecordCreate]) -> list[dict[str, Any]]:
    if not records_in:
        return []

    codes = [rec.code for rec in records_in]
    if len(codes) != len(set(codes)):
        raise ConflictError("Пакет містить повторювані коди (дублікати в тілі запиту).")

    with closing(get_connection()) as connection:
        cursor = connection.cursor()

        category_ids = {rec.category_id for rec in records_in}
        placeholders = ",".join("?" for _ in category_ids)
        cursor.execute(
            f"SELECT id FROM categories WHERE id IN ({placeholders})",  # noqa: S608
            tuple(category_ids),
        )
        found_category_ids = {row[0] for row in cursor.fetchall()}
        missing_categories = category_ids - found_category_ids
        if missing_categories:
            raise NotFoundError(
                f"Категорії з id {sorted(missing_categories)} не існують."
            )

        created_ids: list[int] = []
        try:
            with connection:
                for rec in records_in:
                    cursor.execute(
                        """
                        INSERT INTO records (code, title, category_id, value, status)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (rec.code, rec.title, rec.category_id, rec.value, rec.status),
                    )
                    created_ids.append(cursor.lastrowid)
        except sqlite3.IntegrityError as err:
            raise ConflictError(
            ) from err

    # 4. Отримання створених записів
    result: list[dict[str, Any]] = []
    for r_id in created_ids:
        rec = get_record_by_id(r_id)
        if rec:
            result.append(rec)
    return result
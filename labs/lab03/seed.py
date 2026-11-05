import json
import logging
import sqlite3
from contextlib import closing
from pathlib import Path

from labs.lab03.database import get_connection, initialize_database

BASE_DIR = Path(__file__).resolve().parent
SEED_PATH = BASE_DIR / "data" / "seed.json"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def seed_database() -> None:
    if not SEED_PATH.exists():
        logger.error("Файл початкових даних не знайдено: %s", SEED_PATH)
        return

    initialize_database()

    with open(SEED_PATH, encoding="utf-8") as file:
        data = json.load(file)

    categories = data.get("categories", [])
    records = data.get("records", [])

    with closing(get_connection()) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM categories")
        count = cursor.fetchone()[0]
        if count > 0:
            logger.info("База даних уже містить дані. Пропуск заповнення.")
            return

        try:
            with connection:
                connection.executemany(
                    "INSERT INTO categories (id, name) VALUES (?, ?)",
                    [(cat["id"], cat["name"]) for cat in categories],
                )
                connection.executemany(
                    """
                    INSERT INTO records (code, title, category_id, value, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            rec["code"],
                            rec["title"],
                            rec["category_id"],
                            rec["value"],
                            rec["status"],
                        )
                        for rec in records
                    ],
                )
            logger.info(
                "Успішно додано %d категорій та %d записів.",
                len(categories),
                len(records),
            )
            logger.info(
                "Успішно додано %d категорій та %d записів.",
                len(categories),
                len(records),
            )
        except sqlite3.IntegrityError as err:
            logger.error("Помилка цілісності даних при заповненні: %s", err)
            raise
        except sqlite3.Error as err:
            logger.error("Помилка SQLite: %s", err)
            raise


if __name__ == "__main__":
    seed_database()
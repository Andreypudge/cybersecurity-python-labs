import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from functools import wraps

from rich.console import Console
from rich.table import Table

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_CSV = os.path.join(DATA_DIR, "users.csv")
LOG_JSON = os.path.join(DATA_DIR, "log.json")
SALT = f"{VARIANT_NUMBER:05d}"


class ValidationError(Exception):
    pass

def generate_hash(password: str, salt: str = SALT) -> str:
    if not password or not salt:
        raise ValueError("Password and salt must not be empty.")
    if len(password) < 13:
        raise ValidationError("Password must be 13 or more symbols.")

    data = (password + salt).encode()
    return hashlib.sha224(data).hexdigest()

def create_user(username, password):
    return (username, generate_hash(password, SALT))
    
    
def create_users(users_list):
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        with open(USERS_CSV, "w", encoding="utf-8") as f:
            for username, password in users_list:
                try:
                    user, user_hash = create_user(username, password)
                    f.write(f"{user},{user_hash}\n")
                except (ValidationError, ValueError) as err:
                    print(f"{username}: {err}")
    except (PermissionError, IOError) as file_err:
        print(f"Помилка доступу до файлу CSV: {file_err}")



def load_users(filepath=USERS_CSV):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} not found!")

    users_db = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                clean_line = line.strip()
                if not clean_line:
                    continue
                username, password = clean_line.split(",")
                users_db.append((username, password))
    except (PermissionError, IOError) as file_err:
        print(f"Помилка читання файлу: {file_err}")

    return users_db






def log_event(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result:
            status = "success"
        else:
            status = "failure"
        username = args[0] if args else kwargs.get("username", "unknown")
        safe_args = [args[0], "***"] if len(args) > 1 else list(args)
        log_entry = {"event": func.__name__, "user": username, "result": status, "timestamp": datetime.now(timezone.utc).isoformat(), "args": safe_args, "kwargs": kwargs}
        if not os.path.exists(LOG_JSON):
            logs = []
        else:
            with open(LOG_JSON, "r", encoding="utf-8") as f:
                logs = json.load(f)
        logs.append(log_entry)
        with open(LOG_JSON, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)
        return result
    return wrapper



@log_event
def login(username: str, password: str):
    if not username or not password:
        raise ValueError("Login or password must not be empty")
    users_dict = dict(load_users())
    stored_hash = users_dict.get(username)
    if not stored_hash or len(password) < 13:
        return False
    else:
        return generate_hash(password, SALT) == stored_hash






def main():
    console = Console()
    if __name__ == "__main__":
        console.print(f"[bold]Студент:[/] {STUDENT_NAME} | [bold]Група:[/] {GROUP_NAME} | [bold]Варіант:[/] {VARIANT_NUMBER}\n")

    users_to_register = (
        ("alice_w", "SuperSecurePass123!"),
        ("bob_builder", "HammerTime2026#"),
        ("charlie99", "qwerty"),
        ("diana_p", "AmazonianWarrior999"),
        ("evan_test", ""),
        ("alex_g", "ForestForever2026"),
        ("george_k", "ShortPass1"),
        ("hannah_b", "SunshineAndRainbows1"),
        ("ivan_p", "SecurityMaster777"),
        ("julia_sky", "StargazingNight2026"),
    )

    create_users(users_to_register)

    table = Table(title="База користувачів (users.csv)")
    table.add_column("Логін", style="cyan", no_wrap=True)
    table.add_column("Хеш пароля (SHA-224)", style="green")

    for username, pwd_hash in load_users():
        table.add_row(username, pwd_hash)

    console.print(table)

    try:
        res1 = login("alice_w", "SuperSecurePass123!")
        print(f"alice_w (правильний пароль): {res1}")

        res2 = login("alice_w", "WrongPassword123!")
        print(f"alice_w (хибний пароль): {res2}")

        login("", "")
    except ValueError as e:
        print(f"Очікувана помилка валідації: {e}")


main()
import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Any

PBKDF2_ITERATIONS = 100_000
SESSION_TIMEOUT_SEC = 900


class User:
    def __init__(self, username: str, email: str, role: str = "user", active: bool = True):
        self.username = username
        self.email = email
        self.role = role
        self.active = active
        self.__password_salt: bytes | None = None
        self.__password_hash: bytes | None = None
        
    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value):
        EMAIL_REGEX = r"^[a-zA-Z][a-zA-Z0-9._-]{2,63}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(EMAIL_REGEX, value):
            raise ValueError("Invalid format email")
        else:
            self._email = value

    def set_password(self, password: str) -> None:
        self.__password_salt = os.urandom(16)
        self.__password_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), self.__password_salt, PBKDF2_ITERATIONS)


    def check_password(self, password: str) -> bool:
        if self.__password_hash is not None and self.__password_salt is not None:
            password_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), self.__password_salt, PBKDF2_ITERATIONS)
            return hmac.compare_digest(self.__password_hash, password_hash)
        else:
            return False
        
    def deactivate(self) -> None:
        self.active = False

    def __str__(self) -> str:
        return f"User({self.username}, email={self.email}, role={self.role}, active={self.active})"
    

class Admin(User):
    def __init__(self, username: str, email: str, permissions: set[str] | None = None):
        super().__init__(username, email, role="admin")
        self.permissions: set[str] = permissions if permissions is not None else set()

    def grant_permission(self, permission: str) -> None:
        self.permissions.add(permission)

    def revoke_permission(self, permission: str) -> None:
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def __str__(self) -> str:
        return f"Admin({self.username}, email={self.email}, role={self.role}, active={self.active}, permissions={self.permissions})"
    
    
class Session:
    def __init__(self, ip: str):
        self.ip = ip
        self.login_time: datetime = datetime.now(timezone.utc)
        self.last_activity: datetime = self.login_time

    def touch(self) -> None:
        self.last_activity = datetime.now(timezone.utc)
            
    def is_active(self, timeout_sec: int) -> bool:
        if timeout_sec <= 0:
            raise ValueError("Timeout must be bigger than 0")
        return (datetime.now(timezone.utc) - self.last_activity) <= timedelta(seconds=timeout_sec)
        
        
@dataclass
class AuditEntry:
    timestamp: datetime
    username: str
    action: str


class AuditLog:
    def __init__(self) -> None:
        self.entries: list[AuditEntry] = []

    def add_log(self, username: str, action: str) -> None:
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc),
            username=username,
            action=action,
        )
        self.entries.append(entry)

    def show_all(self) -> list[AuditEntry]:
        return self.entries
    
    

class UserAccount:
    def __init__(self, user: User, log: AuditLog | None = None):
        self.user = user
        self.session: Session | None = None
        self.log: AuditLog = log if log is not None else AuditLog()

    def login(self, username: str, password: str, ip: str) -> bool:
        if self.user.username == username and self.user.active and self.user.check_password(password):
            self.session = Session(ip)
            self.session.touch()
            self.log.add_log(self.user.username, "login_success")
            return True

        self.log.add_log(username, "login_failure")
        return False

    def is_authenticated(self) -> bool:
        return self.session is not None and self.session.is_active(SESSION_TIMEOUT_SEC)


    def logout(self) -> None:
        self.session = None
        self.log.add_log(self.user.username, "logout")

    def __getitem__(self, key: str) -> Any:
        if key == "user":
            return self.user
        elif key == "session":
            return self.session
        elif key == "log":
            return self.log
        else:
            raise KeyError(f"Invalid key: {key}")

    def __setitem__(self, key: str, value: Any) -> None:
        if key == "user":
            if isinstance(value, User):
                self.user = value
            else:
                raise TypeError("Value must be an instance of User")
                
        elif key == "session":
            if value is None or isinstance(value, Session):
                self.session = value
            else:
                raise TypeError("Value must be an instance of Session or None")

        elif key == "log":
            if isinstance(value, AuditLog):
                self.log = value
            else:
                raise TypeError("Value must be an instance of Log")
        
        else:
            raise KeyError(f"Invalid key: {key}")
import string
import random
from rich.console import Console
from rich.table import Table
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

UPPERCASE_CHARS = set(string.ascii_uppercase)
SPECIAL_CHARS = set(string.punctuation)
DIGIT_CHARS = set(string.digits)

passwords = [
    "Digital@F0r3nsics",
    "plain",
    "Encrypt10n@Key",
    "member",
    "Security@Audit2023",
    "regular",
    "Hack3r@D3fense",
    "ordinary",
    "Threat@Intel",
    "usual",
]

criteria = {
    "min_length": 8,
    "require_digits": True,
    "require_upper": True,
    "require_special": True,
}

forbidden_passwords = {"plain", "member", "regular", "ordinary", "usual", "user"}


def check_passwd(password):
    if password in forbidden_passwords or len(password) < criteria["min_length"]:
        return ("Forbidden password")

    big = 0
    spec = 0
    digit = 0

    for char in password:
        if char in UPPERCASE_CHARS:
            big += 1
        if char in SPECIAL_CHARS:
            spec += 1
        if char in DIGIT_CHARS:
            digit += 1

    has_upper = big > 0
    has_digit = digit > 0
    has_special = spec > 0
    
    all_met = has_upper and has_digit and has_special
    
    if all_met and len(password) >= (criteria["min_length"] + 4) and passwords.count(password) < 2:
        return ("Very strong password")
    elif all_met:
        return ("Strong password")
    elif len(password) >= criteria["min_length"] and ((has_upper and has_digit) or (has_digit and has_special) or (has_upper and has_special)):
        return ("Medium password")
    else:
        return ("Weak password")



passwords.extend(random.sample(passwords, 3))

table = Table(title="Результати перевірки паролів")
table.add_column("Пароль", style="cyan", no_wrap=True)
table.add_column("Рівень надійності", style="green")

for pwd in passwords:
    result = check_passwd(pwd)
    table.add_row(pwd, result)

console = Console()
if __name__ == "__main__":
    console.print(f"[bold]Студент:[/] {STUDENT_NAME} | [bold]Група:[/] {GROUP_NAME} | [bold]Варіант:[/] {VARIANT_NUMBER}\n")
console.print(table)

import os
import runpy
import sys
from rich.console import Console

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER

console = Console()
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    console.rule("[bold cyan]ЛАБОРАТОРНА РОБОТА №1[/]")
    console.print(
        f"[yellow]Студент:[/] {STUDENT_NAME} | "
        f"[yellow]Група:[/] {GROUP_NAME} | "
        f"[yellow]Варіант:[/] {VARIANT_NUMBER}\n"
    )

    console.rule("[bold green]Завдання 1: Аналізатор надійності паролів[/]")
    runpy.run_path(os.path.join(CURRENT_DIR, "task1.py"))

    console.print("\n")
    console.rule("[bold green]Завдання 2: Система контролю доступу[/]")
    runpy.run_path(os.path.join(CURRENT_DIR, "task2.py"))

    console.print("\n")
    console.rule("[bold green]Завдання 3: Хешування, CSV-база та JSON-логування[/]")
    runpy.run_path(os.path.join(CURRENT_DIR, "task3.py"))


if __name__ == "__main__":
    main()
import argparse
import logging
import time
from pathlib import Path

from labs.lab02.task1 import Admin, User, UserAccount
from labs.lab02.task2 import HeaderAuditor

logger = logging.getLogger(__name__)


def run_demo() -> None:
    print("=" * 60)
    print(" ДЕМОНСТРАЦІЯ ЗАВДАННЯ 1: МОДЕЛЬ КОРИСТУВАЧА ТА ОБЛІКОВОГО ЗАПИСУ")
    print("=" * 60)

    print("\n--- 1. Створення користувача та валідація email ---")
    user = User(username="andrii_l", email="andrii@cyber.lpnu.ua", role="user")
    user.set_password("SuperSecretPass123")
    print(f"[OK] Створено користувача: {user}")

    try:
        user.email = "bad_email@"
    except ValueError as e:
        print(f"[OK] Спіймано очікуваний ValueError при валідації email: {e}")

    print("\n--- 2. Перевірка Admin та системи прав ---")
    admin = Admin(username="root_admin", email="admin@corp.ua")
    admin.set_password("AdminSecure2026")
    admin.grant_permission("READ_LOGS")
    admin.grant_permission("DROP_DATABASE")
    print(f"[OK] Створено адміна: {admin}")
    print(f"Має право 'READ_LOGS': {admin.has_permission('READ_LOGS')}")
    admin.revoke_permission("DROP_DATABASE")
    print(
        f"Має право 'DROP_DATABASE' після відкликання: {admin.has_permission('DROP_DATABASE')}"
    )

    print("\n--- 3. Аутентифікація та AuditLog у UserAccount ---")
    account = UserAccount(user=user)

    failed = account.login(
        username="andrii_l", password="WrongPassword!", ip="192.168.1.50"
    )
    print(
        f"Спроба входу з невірним паролем: {'Успіх' if failed else 'Відхилено (Очікувано)'}"
    )

    success = account.login(
        username="andrii_l", password="SuperSecretPass123", ip="192.168.1.50"
    )
    print(f"Спроба входу з вірним паролем: {'Успіх' if success else 'Відхилено'}")
    print(f"Сеанс активний (is_authenticated): {account.is_authenticated()}")

    print("\n--- 4. Перевірка таймауту сесії ---")
    if account.session:
        print("Симуляція закінчення таймауту (перевірка з timeout_sec=1)...")
        time.sleep(1.1)
        is_active = account.session.is_active(timeout_sec=1)
        print(f"Чи активна сесія після 1.1 сек (ліміт 1 сек): {is_active}")

    print("\n--- 5. Доступ до атрибутів через account['user'] ---")
    print(f"Поточний користувач через квадратні дужки: {account['user'].username}")
    try:
        _ = account["unknown_key"]
    except KeyError as e:
        print(f"[OK] Спіймано очікуваний KeyError: {e}")

    print("\n--- 6. Завершення сесії та AuditLog ---")
    account.logout()
    print("Користувач вийшов із системи.")
    print("\nЗаписи журналу аудиту (AuditLog):")
    for entry in account.log.show_all():
        print(
            f"  [{entry.timestamp.strftime('%H:%M:%S UTC')}] User: {entry.username:<12} | Action: {entry.action}"
        )


def run_analyze(headers_file: Path, output_csv: Path, strict: bool) -> None:
    logger.info("Auditing HTTP response headers from %s...", headers_file)

    auditor = HeaderAuditor(headers_file, strict=strict)
    results = auditor.run_audit()

    print(
        f"\n{'Target Resource':<30} {'Security Score':<18} {'Status':<8} {'Missing Security Headers'}"
    )
    print("-" * 85)
    for r in results:
        missing_str = ", ".join(r.missing_headers) if r.missing_headers else "None"
        score_str = f"{r.score}/100 ({r.grade})"
        print(f"{r.url:<30} {score_str:<18} {r.status:<8} {missing_str}")

    print("\n=== Server Software Leak Alerts ===")
    leak_found = False
    for r in results:
        for leak in r.leaks:
            leak_found = True
            print(f"[LEAK] {r.url} leaks {leak}")
    if not leak_found:
        print("No software version leaks detected.")

    auditor.export_csv(output_csv)
    logger.info("Header audit report generated at %s", output_csv)


def main() -> None:
    parser = argparse.ArgumentParser(description="Cybersecurity CLI Tool (Lab 02)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("demo", help="Запустити демонстрацію Завдання 1 (ООП)")

    analyze_parser = subparsers.add_parser(
        "analyze", help="Аудит безпеки HTTP-заголовків"
    )
    analyze_parser.add_argument(
        "--headers-file",
        type=Path,
        required=True,
        help="Шлях до вхідного JSON-файлу з заголовками",
    )
    analyze_parser.add_argument(
        "--output-csv",
        type=Path,
        required=True,
        help="Шлях для вивантаження CSV-звіту",
    )
    analyze_parser.add_argument(
        "--strict",
        action="store_true",
        help="Суворий режим перевірки (FAIL при будь-якому порушенні)",
    )
    analyze_parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Рівень логування (типово: INFO)",
    )

    args = parser.parse_args()

    log_level = getattr(logging, getattr(args, "log_level", "INFO").upper())
    logging.basicConfig(level=log_level, format="[%(levelname)s] %(message)s")

    if args.command == "demo":
        run_demo()
    elif args.command == "analyze":
        run_analyze(args.headers_file, args.output_csv, args.strict)


if __name__ == "__main__":
    main()

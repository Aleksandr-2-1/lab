#Администратор	admin	Admin123!
#Сотрудник	employee1	Employee123!
#Специалист по учёту	specialist	Specialist123!
import sqlite3
import hashlib
import secrets
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "equipment.db"


def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 200000
    ).hex()
    return f"{salt}:{digest}"


def check_password(password, stored_hash):
    test_passwords = {
        "test_hash_1": "Admin123!",
        "test_hash_2": "Employee123!",
        "test_hash_3": "Specialist123!",
    }

    if stored_hash in test_passwords:
        if password == test_passwords[stored_hash]:
            return True, hash_password(password)
        return False, stored_hash

    try:
        salt, expected_hash = stored_hash.split(":")
        actual_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), 200000
        ).hex()
        return secrets.compare_digest(actual_hash, expected_hash), stored_hash
    except ValueError:
        return False, stored_hash


def ensure_specialist_account():
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "INSERT OR IGNORE INTO roles (name) VALUES (?)",
            ("Специалист по учёту",),
        )

        role_id = connection.execute(
            "SELECT role_id FROM roles WHERE name = ?",
            ("Специалист по учёту",),
        ).fetchone()[0]

        connection.execute(
            """
            INSERT OR IGNORE INTO users
                (login, password_hash, full_name, role_id)
            VALUES (?, ?, ?, ?)
            """,
            ("specialist", "test_hash_3", "Специалист по учёту", role_id),
        )


def login():
    while True:
        print("\n=== Вход в систему ===")
        username = input("Логин: ").strip()
        password = input("Пароль: ")

        with sqlite3.connect(DB_PATH) as connection:
            user = connection.execute(
                """
                SELECT users.user_id, users.password_hash,
                       users.full_name, roles.name
                FROM users
                JOIN roles ON users.role_id = roles.role_id
                WHERE users.login = ?
                """,
                (username,),
            ).fetchone()

            if user:
                user_id, stored_hash, full_name, role = user
                valid, updated_hash = check_password(password, stored_hash)

                if valid:
                    if updated_hash != stored_hash:
                        connection.execute(
                            "UPDATE users SET password_hash = ? WHERE user_id = ?",
                            (updated_hash, user_id),
                        )

                    print(f"\nДобро пожаловать, {full_name}!")
                    print(f"Ваша роль: {role}")
                    return role

        print("Неверный логин или пароль.")


def show_equipment():
    with sqlite3.connect(DB_PATH) as connection:
        items = connection.execute(
            """
            SELECT inventory_number, name, serial_number, status
            FROM equipment
            ORDER BY id
            """
        ).fetchall()

    print("\n=== Список оборудования ===")

    if not items:
        print("Оборудование не найдено.")
        return

    for number, name, serial, status in items:
        print(f"{number} | {name} | {serial or '—'} | {status}")


def add_equipment():
    number = input("Инвентарный номер: ").strip()
    name = input("Название оборудования: ").strip()
    serial = input("Серийный номер: ").strip() or None

    if not number or not name:
        print("Инвентарный номер и название обязательны.")
        return

    try:
        with sqlite3.connect(DB_PATH) as connection:
            connection.execute(
                """
                INSERT INTO equipment
                    (inventory_number, name, serial_number, status)
                VALUES (?, ?, ?, 'В наличии')
                """,
                (number, name, serial),
            )

        print("Оборудование успешно добавлено.")

    except sqlite3.IntegrityError:
        print("Ошибка: такой инвентарный или серийный номер уже существует.")


def main():
    if not DB_PATH.exists():
        print("База данных не найдена:", DB_PATH)
        return

    ensure_specialist_account()
    role = login()

    while True:
        print("\n=== Учёт оборудования ===")
        print("1. Просмотреть оборудование")

        if role in ("Администратор", "Специалист по учёту"):
            print("2. Добавить оборудование")

        print("0. Выход")

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            show_equipment()
        elif choice == "2" and role in (
            "Администратор",
            "Специалист по учёту",
        ):
            add_equipment()
        elif choice == "0":
            print("Выход из системы.")
            break
        else:
            print("Нет такого пункта меню.")


if __name__ == "__main__":
    main()
import os
import psycopg2
from config import DB_CONFIG, EMPLOYER_IDS
from hh_api import get_employer_info, get_employer_vacancies
from db_manager import DBManager


def create_database():
    """Создает базу данных, если её нет."""
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        options='-c client_encoding=UTF8'
    )
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']};")
    except psycopg2.errors.DuplicateDatabase:
        pass  # БД уже существует
    finally:
        cursor.close()
        conn.close()


def create_tables():
    """Создает таблицы в БД."""
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS employers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                url TEXT
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                id SERIAL PRIMARY KEY,
                employer_id INT REFERENCES employers(id),
                name VARCHAR(255) NOT NULL,
                salary_from INT,
                salary_to INT,
                url TEXT
            );
            """)
        conn.commit()


def fill_tables():
    """Заполняет таблицы данными с HH.ru."""
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cursor:
            # Заполнение таблицы employers
            for employer_id in EMPLOYER_IDS:
                cursor.execute("SELECT 1 FROM employers WHERE id = %s", (employer_id,))
                if cursor.fetchone():
                    continue

                employer = get_employer_info(employer_id)
                if employer:
                    cursor.execute(
                        "INSERT INTO employers (id, name, url) VALUES (%s, %s, %s)",
                        (employer_id, employer["name"], employer["alternate_url"])
                    )

            # Заполнение таблицы vacancies
            for employer_id in EMPLOYER_IDS:
                cursor.execute("SELECT 1 FROM vacancies WHERE employer_id = %s LIMIT 1", (employer_id,))
                if cursor.fetchone():
                    continue

                vacancies = get_employer_vacancies(employer_id)
                for vacancy in vacancies:
                    cursor.execute(
                        """INSERT INTO vacancies (employer_id, name, salary_from, salary_to, url)
                           VALUES (%s, %s, %s, %s, %s)""",
                        (vacancy["employer_id"], vacancy["name"],
                         vacancy["salary_from"], vacancy["salary_to"], vacancy["url"])
                    )
        conn.commit()


def display_companies_and_vacancies(companies_vacancies):
    """Отображает список компаний и количество вакансий."""
    print("\nСписок компаний и количество вакансий:")
    for item in companies_vacancies:
        print(f"{item['company']} - {item['vacancies_count']} вакансий")


def display_all_vacancies(vacancies):
    """Отображает все вакансии."""
    print("\nВсе вакансии:")
    for idx, vacancy in enumerate(vacancies, 1):
        salary = "Не указана"
        if vacancy["salary_from"] or vacancy["salary_to"]:
            salary_from = f"от {vacancy['salary_from']}" if vacancy["salary_from"] else ""
            salary_to = f"до {vacancy['salary_to']}" if vacancy["salary_to"] else ""
            salary = f"{salary_from} {salary_to}".strip()

        print(f"{idx}. {vacancy['company']} - {vacancy['vacancy']} - {salary} - {vacancy['url']}")


def display_avg_salary(avg_salary):
    """Отображает среднюю зарплату."""
    print(f"\nСредняя зарплата: {avg_salary:.2f} руб.")


def display_vacancies_with_higher_salary(vacancies):
    """Отображает вакансии с зарплатой выше средней."""
    print("\nВакансии с зарплатой выше средней:")
    for idx, vacancy in enumerate(vacancies, 1):
        avg = (vacancy["salary_from"] + vacancy["salary_to"]) / 2 if vacancy["salary_from"] and vacancy[
            "salary_to"] else 0
        print(f"{idx}. {vacancy['company']} - {vacancy['vacancy']} - {avg:.0f} руб. - {vacancy['url']}")


def display_vacancies_with_keyword(vacancies, keyword):
    """Отображает вакансии с ключевым словом."""
    print(f"\nВакансии с ключевым словом '{keyword}':")
    for idx, vacancy in enumerate(vacancies, 1):
        print(f"{idx}. {vacancy['company']} - {vacancy['vacancy']} - {vacancy['url']}")


def user_interface():
    """Интерфейс взаимодействия с пользователем."""
    db_manager = DBManager(DB_CONFIG)

    while True:
        print("\nВыберите действие:")
        print("1. Список компаний и количество вакансий")
        print("2. Все вакансии")
        print("3. Средняя зарплата")
        print("4. Вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("0. Выход")

        choice = input("Введите номер действия: ")

        if choice == "1":
            companies_vacancies = db_manager.get_companies_and_vacancies_count()
            display_companies_and_vacancies(companies_vacancies)

        elif choice == "2":
            vacancies = db_manager.get_all_vacancies()
            display_all_vacancies(vacancies)

        elif choice == "3":
            avg_salary = db_manager.get_avg_salary()
            display_avg_salary(avg_salary)

        elif choice == "4":
            avg_salary = db_manager.get_avg_salary()
            vacancies = db_manager.get_vacancies_with_higher_salary(avg_salary)
            display_vacancies_with_higher_salary(vacancies)

        elif choice == "5":
            keyword = input("Введите ключевое слово для поиска: ")
            vacancies = db_manager.get_vacancies_with_keyword(keyword)
            display_vacancies_with_keyword(vacancies, keyword)

        elif choice == "0":
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    # Создание БД и таблиц
    create_database()
    create_tables()

    # Заполнение БД данными
    fill_tables()

    # Запуск пользовательского интерфейса
    user_interface()
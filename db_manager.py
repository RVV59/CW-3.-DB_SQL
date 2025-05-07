import psycopg2
from typing import List, Dict, Any


class DBManager:
    """Класс для работы с базой данных вакансий."""

    def __init__(self, db_config):
        """Инициализация подключения к БД."""
        self.conn = psycopg2.connect(**db_config)

    def __del__(self):
        """Закрытие соединения с БД."""
        self.conn.close()

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """Получает список компаний и количество вакансий у каждой."""
        with self.conn.cursor() as cursor:
            query = """
            SELECT e.name, COUNT(v.id) AS vacancies_count
            FROM employers e
            LEFT JOIN vacancies v ON e.id = v.employer_id
            GROUP BY e.name;
            """
            cursor.execute(query)
            return [{"company": row[0], "vacancies_count": row[1]} for row in cursor.fetchall()]

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """Получает список всех вакансий с информацией о компании."""
        with self.conn.cursor() as cursor:
            query = """
            SELECT e.name, v.name, v.salary_from, v.salary_to, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.id;
            """
            cursor.execute(query)
            return [{
                "company": row[0],
                "vacancy": row[1],
                "salary_from": row[2],
                "salary_to": row[3],
                "url": row[4]
            } for row in cursor.fetchall()]

    def get_avg_salary(self) -> float:
        """Получает среднюю зарплату по всем вакансиям."""
        with self.conn.cursor() as cursor:
            query = """
            SELECT AVG((salary_from + salary_to) / 2)
            FROM vacancies
            WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL;
            """
            cursor.execute(query)
            result = cursor.fetchone()[0]
            return float(result) if result else 0.0

    def get_vacancies_with_higher_salary(self, avg_salary: float) -> List[Dict[str, Any]]:
        """Получает вакансии с зарплатой выше средней."""
        with self.conn.cursor() as cursor:
            query = """
            SELECT e.name, v.name, v.salary_from, v.salary_to, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.id
            WHERE (v.salary_from + v.salary_to) / 2 > %s;
            """
            cursor.execute(query, (avg_salary,))
            return [{
                "company": row[0],
                "vacancy": row[1],
                "salary_from": row[2],
                "salary_to": row[3],
                "url": row[4]
            } for row in cursor.fetchall()]

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Получает вакансии с ключевым словом в названии."""
        with self.conn.cursor() as cursor:
            query = """
            SELECT e.name, v.name, v.salary_from, v.salary_to, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.id
            WHERE v.name ILIKE %s;
            """
            cursor.execute(query, (f"%{keyword}%",))
            return [{
                "company": row[0],
                "vacancy": row[1],
                "salary_from": row[2],
                "salary_to": row[3],
                "url": row[4]
            } for row in cursor.fetchall()]
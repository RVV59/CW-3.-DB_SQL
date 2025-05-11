from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env
load_dotenv()

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'hh_vacancies',
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD")
}

EMPLOYER_IDS = [9694561, 2282240, 3127, 2537115, 1809605, 370, 3388, 4181, 2748, 4719104]
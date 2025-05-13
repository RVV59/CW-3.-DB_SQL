import requests


def get_employer_info(employer_id):
    """Получает информацию о компании по ID."""
    url = f"https://api.hh.ru/employers/{employer_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def get_employer_vacancies(employer_id):
    """Получает список вакансий от работодателей"""
    vacancies = []
    page = 0
    max_vacancies = 100
    per_page = 100

    while len(vacancies) < max_vacancies:
        url = "https://api.hh.ru/vacancies"
        params = {
            "employer_id": employer_id,
            "page": page,
            "per_page": min(per_page, max_vacancies - len(vacancies))
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            break
        data = response.json()
        items = data.get("items", [])
        if not items:
            break
        vacancies.extend(items)
        page += 1

    return vacancies[:max_vacancies]

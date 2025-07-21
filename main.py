import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from moodle_config import MOODLE_URL, MOODLE_TOKEN # Ссылается на другой файл с конфигуратором

# Функция для получения данных из Moodle API
def get_moodle_course_data(course_id):
    endpoint = f"{MOODLE_URL}/webservice/rest/server.php"
    params = {
        'wstoken': MOODLE_TOKEN,
        'wsfunction': 'core_enrol_get_enrolled_users',
        'moodlewsrestformat': 'json',
        'courseid': course_id
    }

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        users = response.json()

        # Подсчет статистики
        total_users = len(users)
        completed_users = sum(1 for user in users if user.get('lastcourseaccess', 0) > 0 and
                              user.get('enrolments', [{}])[0].get('status') == 0)
        in_progress_users = sum(1 for users in users if users.get('lastcourseaccess', 0) > 0 and
                                user.get('enrolments', [{}])[0].get('status') == 0)

        return {
            'total' : total_users,
            'completed' : completed_users,
            'in_progress' : in_progress_users,
        }
    except Exception as e:
        return {'error': str(e)}


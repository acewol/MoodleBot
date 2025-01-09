import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Конфигурация
MOODLE_BASE_URL = "https://your-moodle-site.com/webservice/rest/server.php"
MOODLE_TOKEN = "your_moodle_token"
TELEGRAM_TOKEN = "your_telegram_bot_token"

COURSE_ID = 12345  # ID курса, для которого нужна информация

def get_course_participants(course_id):
    """
    Получает информацию о пользователях курса из Moodle.
    :param course_id: ID курса
    :return: Словарь с количеством участников, прошедших и не прошедших курс
    """
    params = {
        "wstoken": MOODLE_TOKEN,
        "wsfunction": "core_enrol_get_enrolled_users",
        "moodlewsrestformat": "json",
        "courseid": course_id
    }
    response = requests.get(MOODLE_BASE_URL, params=params)
    if response.status_code == 200:
        users = response.json()
        total_users = len(users)
        completed_users = sum(1 for user in users if user.get('completionstatus', {}).get('state') == 1)
        looked_users = sum(1 for user in users if user.get('completionstatus', {}).get('state') == 0)
        not_completed_users = total_users - completed_users
        return {
            "looked": looked_users,
            "total": len(users),
            "completed": completed_users,
            "not_completed": not_completed_users
        }
    else:
        raise Exception(f"Ошибка API Moodle: {response.status_code} {response.text}")

async def start(update: Update, context: CallbackContext) -> None:
    """
    Команда /start.
    """
    try:
        stats = get_course_participants(COURSE_ID)
        message = (
            f"Информация по курсу:\n"
            f"Всего участников: {stats['total']}\n"
            f"Людей посмотрело курс: {stats['looked']}\n"
            f"Прошли курс: {stats['completed']}\n"
            f"Не прошли курс: {stats['not_completed']}"
        )
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")

def main():
    """
    Основная функция запуска бота.
    """
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()

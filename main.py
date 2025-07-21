import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext, CallbackQueryHandler
from config import MOODLE_URL, MOODLE_TOKEN # Ссылается на другой файл с конфигуратором

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

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Привет! Я могу прислать статистику курсов Moodle.\n'
        'Используйте команду /course <ID_курса> для получения информации.'
    )

# Команда /course
async def course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text('Пожалуйста, укажите ID курса: /course <ID_курса>')
        return

    try:
        course_id = int(context.args[0])
        data = get_moodle_course_data(course_id)

        if 'error' in data:
            await update.message.reply_text(f'Ошибка: {data["error"]}')
            return

        response = (
            f'Статистика курса ID {course_id}\n'
            f'Всего участников: {data["total"]}\n'
            f'Прошли курс: {data["completed"]}\n'
            f'Проходят курса: {data["in_progress"]}\n'
        )
        await update.message.reply_text(response)

    except ValueError:
        await update.message.reply_text('ID курса должен быть числом!')
    except Exception as e:
        await update.message.reply_text(f'Произошла ошибка: {str(e)}')

def main():
    # Заменяем YOUR_BOT_TOKEN на своего бота
    application = Application.builder().token('YOUR_BOT_TOKEN').build()

    # Добавление обработчиков команд
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('course', course))

    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()


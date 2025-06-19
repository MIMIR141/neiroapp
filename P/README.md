# Event Manager — Django

## Быстрый старт для деплоя (Render, Heroku, PythonAnywhere, VPS)

### 1. Клонируйте репозиторий и установите зависимости
```
pip install -r requirements.txt
```

### 2. Production-настройки (settings.py)
- `DEBUG = False`
- `ALLOWED_HOSTS = ['ваш_домен', 'ваш_IP']`
- `STATIC_ROOT = BASE_DIR / 'staticfiles'`
- `MEDIA_ROOT = BASE_DIR / 'media'`
- Все секретные ключи и OAuth-ключи вынести в переменные окружения

### 3. Соберите статику
```
python manage.py collectstatic
```

### 4. Миграции
```
python manage.py migrate
```

### 5. Запуск (локально или на сервере)
```
gunicorn event_manager.wsgi:application
```

### 6. Переменные окружения (пример для Render/Heroku)
- `SECRET_KEY` — секретный ключ Django
- `DATABASE_URL` — строка подключения к PostgreSQL
- `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, ... — для SMTP
- OAuth-ключи для Google/VK

### 7. Настройка OAuth
- Google: получите OAuth-клиент в Google Cloud Console, пропишите ключи в переменных окружения
- VK: зарегистрируйте приложение на dev.vk.com

### 8. Импорт и экспорт
- Экспорт событий и участников — кнопки на сайте (CSV)
- Импорт из Google Calendar — кнопка на сайте (OAuth, потребуется ключ)

### 9. Локализация
- Для полного перевода интерфейса установите GNU gettext и выполните:
```
python manage.py makemessages -l ru
python manage.py compilemessages
```

---

**Вопросы по деплою, настройке OAuth, email или локализации — пишите, помогу!** 
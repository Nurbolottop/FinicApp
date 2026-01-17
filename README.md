 # Finic Backend API

 Backend для платформы пожертвований **Finic**
 (Django + Django REST Framework)

 ---

 ## 🚀 Стек

 - Python 3.10+
 - Django
 - Django REST Framework
 - PostgreSQL
 - Redis (опционально)
 - JWT (SimpleJWT)
 - drf-spectacular (Swagger)
 - Docker / Docker Compose

 ---

 ## 📦 Основные возможности

 - Регистрация доноров и организаций
 - Кампании организаций
 - Донаты + платёжный stub
 - Отчёты организаций
 - Аналитика (донор / организация)
 - Уведомления (in-app + email stub)
 - Rate limit / throttling
 - Swagger API документация

 ---

 ## ⚙️ Переменные окружения (.env)

 ```env
 DEBUG=1
 SECRET_KEY=your-secret-key
 ALLOWED_HOSTS=*

 DATABASE_URL=postgres://user:password@db:5432/finic

 EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
 DEFAULT_FROM_EMAIL=no-reply@finic.app
 ```

 ---

 ## ▶️ Запуск через Docker

 ```bash
 docker compose up --build
 ```

 ---

 ## ▶️ Локальный запуск (без Docker)

 ```bash
 python -m venv venv
 venv\Scripts\activate
 pip install -r requirements.txt

 python app\manage.py migrate
 python app\manage.py createsuperuser
 python app\manage.py runserver
 ```

 ---

 ## 📚 API Документация (Swagger)

 После запуска доступно по адресу:

 - `/api/docs/`

 ---

 ## 🔐 Аутентификация

 Используется JWT:

 - `POST /api/auth/login/`
 - `POST /api/auth/refresh/`

 Передавать токен в заголовке:

 - `Authorization: Bearer <access_token>`

 ---

 ## 👤 Роли

 - `donor` — донор
 - `org` — организация
 - `admin` — администратор

 ---

 ## 🧩 Структура проекта

 ```text
 app/
 ├── apps/
 │   ├── accounts/
 │   └── base/
 └── core/
 docker/
 ```

 ---

 ## 🛠️ Статус проекта

 MVP backend готов.
 Готов к интеграции с frontend / mobile и реальным платёжным шлюзам.


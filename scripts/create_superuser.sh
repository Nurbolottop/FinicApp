#!/bin/bash
# Скрипт для создания суперпользователя Finic

cd "$(dirname "$0")/../app" || exit 1

# Проверка наличия миграций
if [ ! -f "apps/accounts/migrations/0001_initial.py" ]; then
    echo "Создание миграций..."
    python manage.py makemigrations
fi

# Применение миграций
echo "Применение миграций..."
python manage.py migrate

# Создание суперпользователя через shell
python manage.py shell << 'EOF'
from apps.accounts.models import User
import os

username = os.getenv('ADMIN_USERNAME', 'admin')
email = os.getenv('ADMIN_EMAIL', 'admin@finic.kg')
password = os.getenv('ADMIN_PASSWORD', 'admin123')

if User.objects.filter(username=username).exists():
    print(f"Пользователь '{username}' уже существует")
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.role = 'admin'
    user.save()
    print(f"Пароль обновлен для '{username}'")
else:
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        role='admin'
    )
    print(f"Суперпользователь '{username}' создан!")
    print(f"Email: {email}")
    print(f"Password: {password}")
EOF

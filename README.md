# Foodgram

Проект построен как REST API на Django с фронтендом на React SPA и разворачивается через Docker.

---

## О проекте

Foodgram - это веб-приложение, где пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок», который позволяет создавать список продуктов, необходимых для приготовления выбранных блюд.

---

## Возможности

- Регистрация и аутентификация пользователей
- Публикация, редактирование и удаление рецептов
- Добавление рецептов в избранное
- Составление и скачивание списка покупок
- Подписка на авторов рецептов
- Фильтрация рецептов по тегам
- Изменение аватара и смена пароля
- Администрирование через Django Admin

---

## Технологии

- Python 3.9
- Django 4.x + DRF
- PostgreSQL
- Docker & Docker Compose
- nginx
- React
- GitHub Actions для CI/CD

---

## Локальная установка

1. Клонируем репозиторий:
```bash
git  clone  git@github.com:ArtemYuvanov/foodgram.git  foodgram
cd  foodgram/infra
```

2. Настройте виртуальное окружение:
```bash
python  -m  venv  venv
source  venv/bin/activate  # Linux/MacO
# или
venv\Scripts\activate  # Windows
```

3. Установите зависимости:
```bash
cd  backend
pip  install  -r  requirements.txt
```

4. Настройте базу данных:
```bash
python  manage.py  migrate
python  manage.py  loaddata  ingredients
```

5. Создайте суперпользователя:
```bash
python  manage.py  createsuperuser
```

6. Запустите сервер:
```bash
python  manage.py  runserver
```

---

## Запуск в Docker (продакшен)

1. Соберите и запустите контейнеры:
```bash
cd  infra
docker-compose  up  -d  --build
```

2. Выполните миграции:
```bash
docker-compose  exec  backend  python  manage.py  migrate
```

3. Соберите статические файлы:
```bash
docker-compose  exec  backend  python  manage.py  collectstatic  --noinput
```

4. Загрузите ингредиенты:
```bash
docker-compose  exec  backend  python  manage.py  loaddata  ingredients
```

5. Создайте администратора:
```bash
docker-compose  exec  backend  python  manage.py  createsuperuser
```

Приложение будет доступно по адресу: http://localhost

IP сервера: 51.250.109.26

Домен сервера: foodgram.freedynamicdns.net

---

## Настройка окружения

Создайте файл .env в папке infra со следующими переменными:

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,localhost,127.0.0.1
# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=foodgram
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
DB_HOST=db
DB_PORT=5432
# Docker
DOCKER_USERNAME=your-dockerhub-username

```

---

## API Endpoints

- POST /api/users/ - регистрация
- GET /api/users/ - список пользователей
- GET /api/users/{id}/ - профиль пользователя
- GET /api/users/me/ - текущий пользователь
- POST /api/users/set_password/ - смена пароля

### Пользователи

- POST /api/users/ - регистрация
- GET /api/users/ - список пользователей
- GET /api/users/{id}/ - профиль пользователя
- GET /api/users/me/ - текущий пользователь
- POST /api/users/set_password/ - смена пароля
- PUT /api/users/me/avatar/ - загрузка аватара

### Аутентификация

- POST /api/auth/token/login/ - получение токена
- POST /api/auth/token/logout/ - удаление токена

### Рецепты

- GET /api/recipes/ - список рецептов
- POST /api/recipes/ - создание рецепта
- GET /api/recipes/{id}/ - детали рецепта
- PATCH /api/recipes/{id}/ - обновление рецепта
- DELETE /api/recipes/{id}/ - удаление рецепта
- GET /api/recipes/{id}/get-link/ - короткая ссылка

### Избранное и покупки

- POST /api/recipes/{id}/favorite/ - добавить в избранное
- DELETE /api/recipes/{id}/favorite/ - удалить из избранного
- POST /api/recipes/{id}/shopping_cart/ - добавить в покупки
- DELETE /api/recipes/{id}/shopping_cart/ - удалить из покупок
- GET /api/recipes/download_shopping_cart/ - скачать список покупок

### Подписки

- GET /api/users/subscriptions/ - мои подписки
- POST /api/users/{id}/subscribe/ - подписаться
- DELETE /api/users/{id}/subscribe/ - отписаться

### Теги и ингредиенты

- GET /api/tags/ - список тегов
- GET /api/tags/{id}/ - детали тега
- GET /api/ingredients/ - список ингредиентов
- GET /api/ingredients/{id}/ - детали ингредиента

---

## Docker образы

Проект использует следующие Docker образы:

- Backend: your-username/foodgram_backend:latest
- Frontend: your-username/foodgram_frontend:latest
- PostgreSQL: postgres:15
- Nginx: nginx:1.22

---

##  CI/CD

Настроен автоматический деплой через GitHub Actions:

- Автоматические тесты при пуше в main
- Сборка Docker образов
- Пуш образов в Docker Hub
- Деплой на сервер
- Уведомления в Telegram

---  

## Уровни доступа

### Гость (неаутентифицированный пользователь)

- Просмотр рецептов
- Просмотр профилей пользователей
- Поиск и фильтрация рецептов
- Регистрация и вход

### Аутентифицированный пользователь

- Все возможности гостя
- Создание, редактирование, удаление своих рецептов
- Добавление рецептов в избранное и список покупок
- Подписка на авторов
- Смена пароля и аватара

### Администратор

- Все возможности пользователя
- Управление всеми рецептами
- Управление пользователями
- Управление тегами и ингредиентами

---

## Автор

- Артем Юванов - [GitHub](https://github.com/ArtemYuvanov)

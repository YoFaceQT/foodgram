![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) ![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white) ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)

# **_Foodgram — бэкенд для сервиса публикации рецептов_**
Foodgram — это социальный сервис, где пользователи могут делиться рецептами, подписываться на других авторов, добавлять рецепты в избранное и формировать список покупок. Моя задача заключалась в разработке полноценного бэкенда для SPA-приложения на React.

### 🛠️ Используемые технологии

- Python 3

- Django REST Framework — каркас приложения и API

- PostgreSQL — основная база данных

- JWT-аутентификация (djangorestframework-simplejwt) — регистрация, вход, управление доступом

- Docker — контейнеризация сервисов (бэкенд, БД, фронтенд, nginx)

- Gunicorn, Nginx — продакшн-сервер и проксирование

- GitHub Actions — CI/CD (автоматическое тестирование, сборка образов, деплой на сервер)

**_Ссылка на [проект](https://yofoodgram.duckdns.org/ "Гиперссылка к проекту.")_**
(**_На 04.05.2026 Ещё находится на удалённом сервере и работает._**)
**_Ссылка на [админ-зону](https://yofoodgram.duckdns.org/admin "Гиперссылка к админке.")_**

## Проект состоит из следующих страниц
- Главная  
- Страница входа  
- Страница регистрации  
- Страница рецепта  
- Страница пользователя  
- Страница подписок  
- Избранное  
- Список покупок  
- Создание и редактирование рецепта  
- Страница смены пароля  

## 🔧 В раках учебного проекта выполнено: 

### Модели и база данных:

- Спроектированы модели: пользователь (расширенная кастомная модель), рецепт, ингредиент, тег, связь рецепт-ингредиент с количеством, подписки, избранное, список покупок.

- Настроены связи «многие ко многим» с промежуточными моделями для точного учёта ингредиентов.

### REST API (полностью соответствует предоставленной спецификации):

- Реализованы все эндпоинты для пользователей, рецептов, ингредиентов, тегов, подписок, избранного, списка покупок.

- Сериализаторы с валидацией данных (создание/редактирование рецептов, уникальность подписок и пр.).

- Пагинация и динамическая фильтрация (по тегам, автору, нахождению в избранном/покупках).

- Эндпоинт для скачивания списка покупок: ингредиенты автоматически суммируются по всем рецептам из списка покупок пользователя, результат отдаётся файлом (формат .txt или .pdf).

### Аутентификация и права доступа:

- Настроена регистрация, аутентификация по JWT-токенам, смена пароля.

- Разграничены уровни доступа: гости (только чтение), авторизованные пользователи (создание рецептов, подписки, списки), администратор (управление тегами, ингредиентами, пользователями).

- Для неавторизованных пользователей корректно возвращаются ошибки 401/403.

### Дополнительный функционал:

- Добавлена генерация прямой короткой ссылки на рецепт (не меняется при редактировании).

- Работа с аватарами: загрузка, удаление, восстановление дефолтного изображения.

- Статические страницы «О проекте» и «Технологии»: контент страниц управляется через админку или переменные, по умолчанию отключены (отдают 404).

### Интеграция и инфраструктура:

- Контейнеризированы все компоненты (Django-бэкенд, PostgreSQL, фронтенд на React, Nginx).

- Настроен CI/CD: автотесты, сборка образов, деплой на сервер при пуше в main.

- Проект успешно развёрнут на удалённом сервере, доступен по [домену](https://yofoodgram.duckdns.org/ "Гиперссылка к проекту.")_**.


## Как запустить проект с помощью Docker Compose
**Клонировать репозиторий и перейти в него в командной строке:**
```bash
git clone git@github.com:YoFaceQT/foodgram.git
```



> [!IMPORTANT]
> Необходимо создать файл `.env` с переменными окружения в корневой папке проекта.</br>
> Пример файла [.env.example](https://github.com/YoFaceQT/foodgram/blob/main/.env.example)
> [!IMPORTANT]
> Необходимо создать файл `.env` с переменными окружения в корневой папке проекта.</br>
> Пример файла [.env.example](https://github.com/YoFaceQT/foodgram/blob/main/.env.example)



**Запустить докер композ**
```
docker compose -f infra/docker-local.yml up -d --build
```
**Создать и запустить контейнеры Docker, выполнить команду на сервере (версии команд "docker compose" или "docker-compose" отличаются в зависимости от установленной версии Docker Compose):**
```
sudo docker compose up -d
```
**_Выполнить миграции:_**
```
sudo docker compose exec backend python manage.py migrate
```
**_Собрать статику:_**
```
sudo docker compose exec backend python manage.py collectstatic --noinput
```
**_Наполнить базу данных скриптом load_csv_data содержимым из файла ingredients.csv:_**
```
sudo docker compose exec backend python manage.py load_csv_data
```
**_Создать суперпользователя:_**
```
sudo docker compose exec backend python manage.py createsuperuser
```
**_Для остановки контейнеров Docker:_**
```
sudo docker compose down -v      - с их удалением
sudo docker compose stop         - без удаления
```
**_Просмотр документации к API, находясь в папке infra/ выполнить команду_**
```
docker compose up
```
**_По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API._**


## Пример запросов/ответов
**_Запрос_**
```
http://localhost/api/recipes/

{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
**_Ответ_**
```
http://localhost/api/recipes/

Status code: 201

{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Иванов",
    "is_subscribed": false,
    "avatar": "http://foodgram.example.org/media/users/image.png"
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.png",
  "text": "string",
  "cooking_time": 1
}
```

## Автор backend:

[YoFaceQT](https://www.github.com/YoFaceQT)

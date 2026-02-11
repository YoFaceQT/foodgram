# **_Foodgram_**
«Фудграм» — сайт, на котором пользователи публикуют свои рецепты, добавляют чужие рецепты в избранное и подписываются на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок», позволяющий создавать список продуктов для приготовления выбранных блюд.
![status workflow](https://github.com/krivse/Foodgram_Workflow/actions/workflows/main.yml/badge.svg)

### Используемые технологии
#### Backend
![Static Badge](https://img.shields.io/badge/Django-grey?style=plastic&logo=django&logoColor=white&labelColor=green) - Django  
![Static Badge](https://img.shields.io/badge/PostgreSQL-grey?style=plastic&logo=Postgresql&logoColor=white&labelColor=blue) - PostgreSQL  
![Static Badge](https://img.shields.io/badge/Django%20Rest%20Framework-grey?style=plastic&logo=API&logoColor=white&label=DRF&labelColor=red) - Django Rest Framework  
#### Frontend
![Static Badge](https://img.shields.io/badge/React-gray?style=plastic&logo=react&labelColor=blue) - ReactJS  
![Static Badge](https://img.shields.io/badge/JavaScript-gray?style=plastic&logo=JavaScript&labelColor=yellow) - JavaScript  
#### Infrastructure
![Static Badge](https://img.shields.io/badge/NginX-gray?style=plastic&logo=nginx&labelColor=green) - NginX  
![Static Badge](https://img.shields.io/badge/docker-grey?style=plastic&logo=docker&logoColor=white&labelColor=blue) - Docker  



**_Ссылка на [проект](https://yofoodgram.duckdns.org/ "Гиперссылка к проекту.")_**  
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
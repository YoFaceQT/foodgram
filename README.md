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

# **_Foodgram_**
«Фудграм» — сайт, на котором пользователи публикуют свои рецепты, добавляют чужие рецепты в избранное и подписываются на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок», позволяющий создавать список продуктов для приготовления выбранных блюд.

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
Клонировать репозиторий и перейти в него в командной строке:
```bash
git clone git@github.com:YoFaceQT/foodgram.git

> [!IMPORTANT]
> Необходимо создать файл `.env` с переменными окружения в корневой папке проекта.</br>
> Пример файла [.env.example](https://github.com/YoFaceQT/foodgram/blob/main/.env.example)
> [!IMPORTANT]
> Необходимо создать файл `.env` с переменными окружения в корневой папке проекта.</br>
> Пример файла [.env.example](https://github.com/YoFaceQT/foodgram/blob/main/.env.example)


```shell
# Запустить докер композ
docker compose -f infra/docker-local.yml up -d --build
```
**_Создать и запустить контейнеры Docker, выполнить команду на сервере (версии команд "docker compose" или "docker-compose" отличаются в зависимости от установленной версии Docker Compose):**_
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


## Автор backend:

[YoFaceQT](https://www.github.com/YoFaceQT)
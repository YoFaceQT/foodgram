import csv

from django.core.management.base import BaseCommand

from recipes.models import (
    Cart,
    Favorite,
    Follow,
    IngredientInRecipes,
    Ingredients,
    Recipes,
    Tags
)


CSV_FILE_PATH = '/app/recipes/management/commands/ingredients.csv'


class Command(BaseCommand):
    help = 'Загружает данные из CSV файла или очищает все данные'

    def add_arguments(self, parser):
        """Добавляем аргументы для команды"""
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить все данные перед загрузкой'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Пропущена очистка данных '
                    '(используйте --clear для очистки) '
                    'ВНИМАНИЕ КЛЮЧ --clear очистит базу полностью!!!'
                )
            )

        self.load_ingredients(options['csv_file'])

        self.stdout.write(
            self.style.SUCCESS('Все данные успешно загружены!')
        )

    def clear_data(self):
        """Очистка всех данных в правильном порядке (учитывая зависимости)"""
        models_to_clear = [
            Cart,
            Favorite,
            Follow,
            IngredientInRecipes,
            Recipes,
            Tags,
            Ingredients,
        ]

        for model in models_to_clear:
            count, _ = model.objects.all().delete()
            self.stdout.write(
                f'Очищено {count} записей из {model.__name__}'
            )

        self.stdout.write(
            self.style.SUCCESS('Все записи успешно удалены!')
        )

    def load_ingredients(self, CSV_FILE_PATH):
        """Загружает ингредиенты из CSV файла"""
        self.stdout.write(f'Загрузка ингредиентов из файла: {CSV_FILE_PATH}')

        try:
            with open(CSV_FILE_PATH, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                ingredients_created = 0

                for row in reader:
                    name, measurement_unit = row
                    name = name.strip()
                    measurement_unit = measurement_unit.strip()

                    ingredient, created = Ingredients.objects.get_or_create(
                        name=name,
                        defaults={'measurement_unit': measurement_unit}
                    )

                    if created:
                        ingredients_created += 1
                    else:

                        if ingredient.measurement_unit != measurement_unit:
                            ingredient.measurement_unit = measurement_unit
                            ingredient.save()
                            self.stdout.write(
                                f'Обновлена единица измерения для: {name}'
                            )

                    self.stdout.write(
                        f'Создано новых ингредиентов: {ingredients_created}'
                    )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Файл не найден: {CSV_FILE_PATH}')
            )
            self.stdout.write(
                'Создайте файл или укажите правильный путь --csv-file'
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при чтении файла: {e}')
            )

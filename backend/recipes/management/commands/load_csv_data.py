import csv

from django.core.management.base import BaseCommand

from recipes.models import (
    Cart,
    Favorite,
    Follow,
    Ingredient,
    IngredientInRecipes,
    Recipe,
    Tag
)


DEFAULT_CSV_PATH = '/app/recipes/management/commands/ingredients.csv'


class Command(BaseCommand):
    help = 'Загружает данные из CSV файла или очищает все данные'

    def add_arguments(self, parser):
        """Добавляем аргументы для команды"""
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить все данные перед загрузкой'
        )
        parser.add_argument(
            '--csv-file',
            type=str,
            default=DEFAULT_CSV_PATH,
            help=f'Путь к CSV файлу (по умолчанию: {DEFAULT_CSV_PATH})'
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

        csv_file_path = options['csv_file']
        self.load_ingredients(csv_file_path)

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
            Recipe,
            Tag,
            Ingredient,
        ]

        for model in models_to_clear:
            count, _ = model.objects.all().delete()
            self.stdout.write(
                f'Очищено {count} записей из {model.__name__}'
            )

        self.stdout.write(
            self.style.SUCCESS('Все записи успешно удалены!')
        )

    def load_ingredients(self, csv_file_path):
        """Загружает ингредиенты из CSV файла"""
        self.stdout.write(f'Загрузка ингредиентов из файла: {csv_file_path}')

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                ingredients_created = 0
                ingredients_updated = 0

                for row in reader:
                    name, measurement_unit = row
                    name = name.strip()
                    measurement_unit = measurement_unit.strip()

                    ingredient, created = Ingredient.objects.get_or_create(
                        name=name,
                        defaults={'measurement_unit': measurement_unit}
                    )

                    if created:
                        ingredients_created += 1
                    else:
                        if ingredient.measurement_unit != measurement_unit:
                            ingredient.measurement_unit = measurement_unit
                            ingredient.save()
                            ingredients_updated += 1
                            self.stdout.write(
                                f'Обновлена единица измерения для: {name}'
                            )

                self.stdout.write(
                    f'Создано новых ингредиентов: {ingredients_created}'
                )
                if ingredients_updated > 0:
                    self.stdout.write(
                        f'Обновлено ингредиентов: {ingredients_updated}'
                    )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Файл не найден: {csv_file_path}')
            )
            self.stdout.write(
                'Создайте файл или укажите правильный путь --csv-file'
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при чтении файла: {e}')
            )

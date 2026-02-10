import random
import string

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q


User = get_user_model()

MAX_NAME_OR_SLUG_LENGHT = 32
INGRIDIENT_MAX_LENGHT_NAME = 128
MEASURMENT_MAX = 64
MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 32000
MIN_INGREDIENT_AMOUNT = 1
MAX_INGREDIENT_AMOUNT = 32000
SHORT_HASH_LENGTH = 8
MAX_RECIPE_NAME_LENGHT = 256


class Tag(models.Model):
    """Модель Тегов"""

    name = models.CharField(
        'Название тега',
        max_length=MAX_NAME_OR_SLUG_LENGHT,
        unique=True
    )
    slug = models.SlugField(
        'Ссылка',
        max_length=MAX_NAME_OR_SLUG_LENGHT,
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'тэг'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель Ингредиентов"""

    name = models.CharField(
        'Название ингредиента',
        max_length=INGRIDIENT_MAX_LENGHT_NAME,
    )
    measurement_unit = models.CharField(
        'Eдиница измерения',
        max_length=MEASURMENT_MAX
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель Рецептов"""

    name = models.CharField(
        'Название рецепта',
        max_length=MAX_RECIPE_NAME_LENGHT,
        unique=True
    )

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipe_author', verbose_name='Автор'
    )
    text = models.TextField('Описание рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message=(
                    'Время приготовления должно быть не менее '
                    f'{MIN_COOKING_TIME} минут.'
                )
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message=(
                    'Время приготовления не должно превышать'
                    f'{MAX_COOKING_TIME} минут.'
                )
            )
        ]
    )
    short_code = models.CharField(
        'Короткий код',
        max_length=SHORT_HASH_LENGTH,
        unique=True,
        blank=True,
        null=True,
        help_text='Уникальный короткий код для ссылки'
    )
    image = models.ImageField('Картинка', upload_to='recipes/images/')
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientInRecipe', verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')

    def generate_short_code(self):
        """Генерирует короткий код для рецепта."""
        characters = string.ascii_letters + string.digits
        code_length = SHORT_HASH_LENGTH

        while True:
            code = ''.join(
                random.choice(characters) for _ in range(code_length)
            )

            if not Recipe.objects.filter(short_code=code).exists():
                return code

    def save(self, *args, **kwargs):
        """Переопределяем метод save для генерации short_code при создании."""
        if not self.short_code:
            self.short_code = self.generate_short_code()

        super().save(*args, **kwargs)

    def get_short_url(self, request=None):
        """Возвращает короткую ссылку на рецепт."""
        if not self.short_code:
            return None

        if request:
            base_url = request.build_absolute_uri('/')
            base_url = base_url.rstrip('/')
            return f"{base_url}/s/{self.short_code}"
        else:
            return f"/s/{self.short_code}"

    class Meta:
        ordering = ('name',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Модель для связи ингредиентов в рецепте"""

    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                message=(
                    'Количество ингредиента должно быть не менее '
                    f'{MIN_INGREDIENT_AMOUNT}.'
                )
            ),
            MaxValueValidator(
                MAX_INGREDIENT_AMOUNT,
                message=(
                    'Количество ингредиента не должно превышать '
                    f'{MAX_INGREDIENT_AMOUNT}.'
                )
            )
        ]
    )

    class Meta:
        ordering = ('ingredient__name',)
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return f'{self.ingredient}'


class Cart(models.Model):
    """Модель Список покупок"""

    author = models.ForeignKey(
        User,
        related_name='cart',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='cart',
        verbose_name='Рецепт для приготовления',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('recipe__name',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return f'{self.recipe}'


class Favorite(models.Model):
    """Модель Избранное"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('recipe__name',)
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.recipe}'


class Follow(models.Model):
    """Модель отслеживания подписок на авторов"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Отслеживание',
        related_name='following'
    )

    class Meta:
        verbose_name = 'Отслеживаемое'
        verbose_name_plural = 'Отслеживаемые'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='prevent_self_follow'
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user} отслеживает автора {self.author}'

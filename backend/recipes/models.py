from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

User = get_user_model()


class Tags(models.Model):
    """Модель Тегов"""

    name = models.CharField('Название тега', max_length=32, unique=True) # хардкод числа
    slug = models.SlugField('Ссылка', max_length=32, unique=True) # валидатор слага

    class Meta:
        ordering = ('id',)
        verbose_name = 'тэг'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    """Модель Ингредиентотв"""

    name = models.CharField('Название ингредиента', max_length=128, unique=True) # хардкод числа
    measurement_unit = models.CharField('Eдиница измерения', max_length=64) # хардкод числа

    class Meta:
        ordering = ('id',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    """Модель Рецептов"""

    name = models.CharField('Название рецепта', max_length=256, unique=True)

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipe_author', verbose_name='Автор'
    )
    text = models.TextField('Описание рецепта')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (в минутах)',
        validators=[MinValueValidator(1)]
    )
    image = models.ImageField('Картинка', upload_to='recipes/images/')
    ingredients = models.ManyToManyField(
        Ingredients, through='IngredientInRecipes', verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(Tags, verbose_name='Теги')

    class Meta:
        ordering = ('id',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipes(models.Model):
    """Модель для связи ингредиентов в рецепте"""

    ingredient = models.ForeignKey(
        Ingredients, on_delete=models.CASCADE, verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Количество'
        verbose_name_plural = 'Количество'

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
        Recipes,
        related_name='cart',
        verbose_name='Рецепт для приготовления',
        on_delete=models.CASCADE
    )

    class Meta:
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
        Recipes,
        on_delete=models.CASCADE,
        related_name='in_favorites',
        verbose_name='Рецепт'
    )

    class Meta:
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

    def __str__(self):
        return f'Пользователь {self.user} отслеживает автора {self.author}'

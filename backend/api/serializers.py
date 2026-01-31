import base64

from djoser.serializers import UserSerializer
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Tags, Recipes, Ingredients, IngredientInRecipes, Favorite, Cart, Follow
from users.models import User


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tags"""
    class Meta:
        model = Tags
        fields = ('id', 'name', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredients"""
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для связаной модели IngredientInRecipes."""
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Favorite."""
    class Meta:
        model = Favorite
        fields = ["user", "recipe"]

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "name": instance.recipe.name,
            "image": instance.recipe.image.url,
            "cooking_time": instance.recipe.cooking_time,
        }


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Cart."""
    id = serializers.ReadOnlyField(source="recipe.id")
    image = serializers.ReadOnlyField(source="recipe.image.url")
    name = serializers.ReadOnlyField(source="recipe.name")
    cooking_time = serializers.ReadOnlyField(source="recipe.cooking_time")

    class Meta:
        model = Cart
        fields = ["id", "image", "name", "cooking_time"]


class FollowSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели Follow. """

    class Meta:
        model = Follow
        fields = ('user', 'author',)
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author',),
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return data


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    """ Сериализатор для Favorite и Cart. """

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowDisplaySerializer(UserSerializer):
    """Сериализатор для отображения информации о пользователях,
    на которых оформлена подписка."""
    recipes = RecipeFavoriteSerializer(
        many=True,
        read_only=True,
        help_text="Список рецептов автора"
    )
    recipes_count = serializers.SerializerMethodField()
    help_text = "Общее количество рецептов автора"

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name=f"avatar.{ext}"
            )
        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)
        read_only_fields = ('id', 'email', 'username', 'first_name', 'last_name')

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class RecipeIngredientCreateSerializer(serializers.Serializer):
    """Сериализатор для создания связи рецепт-ингредиент."""
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    def validate_id(self, value):
        try:
            ingredient = Ingredients.objects.get(id=value)
            return ingredient
        except Ingredients.DoesNotExist:
            raise serializers.ValidationError(
                f'Ингредиент с id={value} не существует.'
            )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""
    ingredients = RecipeIngredientCreateSerializer(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True,
        required=True
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipes
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        for ingredient_data in ingredients_data:
            IngredientInRecipes.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            )

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            IngredientInRecipes.objects.filter(recipe=instance).delete()
            for ingredient_data in ingredients_data:
                IngredientInRecipes.objects.create(
                    recipe=instance,
                    ingredient=ingredient_data['id'],
                    amount=ingredient_data['amount']
                )

        return instance

    def to_representation(self, instance):
        """При возврате данных используем детальный сериализатор."""
        return RecipeDetailSerializer(
            instance,
            context=self.context
        ).data

    def validate(self, attrs):
        """Общая валидация для создания и обновления рецепта."""
        if 'ingredients' in attrs and not attrs['ingredients']:
            raise serializers.ValidationError({
                'ingredients': 'Это поле обязательно для заполнения.'
            })
        if 'tags' in attrs and not attrs['tags']:
            raise serializers.ValidationError({
                'tags': 'Это поле обязательно для заполнения.'
            })

        return attrs

    def validate_ingredients(self, value):
        """Проверяем, что ингредиенты не повторяются и не пусты."""
        if not value:
            raise serializers.ValidationError(
                'Список ингредиентов не может быть пустым.'
            )

        ingredients_ids = [item['id'].id for item in value]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )
        return value

    def validate_tags(self, value):
        """Проверяем, что теги не повторяются и не пусты."""
        if not value:
            raise serializers.ValidationError(
                'Список тегов не может быть пустым.'
            )
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Теги не должны повторяться.'
            )
        return value

    def validate_cooking_time(self, value):
        """Проверяем время приготовления."""
        if value <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть положительным числом.'
            )
        return value

    def validate_name(self, value):
        """Проверяем название рецепта."""
        if not value.strip():
            raise serializers.ValidationError(
                'Название рецепта не может быть пустым.'
            )
        return value

    def validate_text(self, value):
        """Проверяем описание рецепта."""
        if not value.strip():
            raise serializers.ValidationError(
                'Описание рецепта не может быть пустым.'
            )
        return value


class CustomUserSerializer(UserSerializer):
    """ Сериализатор для кастомной модели User. """
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        """Вычисляем поле is_subscribed."""
        user = self.context.get('request').user
        if user is None or user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=user,
            author=obj
        ).exists()

    def get_avatar(self, obj):
        """Возвращаем URL аватара или None."""
        request = self.context.get('request')
        if obj.avatar:
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            else:
                return obj.avatar.url
        return None


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального отображения рецепта."""
    author = CustomUserSerializer(read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    ingredients = IngredientInRecipesSerializer(
        source='ingredientinrecipes_set',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return Cart.objects.filter(author=user, recipe=obj).exists()
        return False

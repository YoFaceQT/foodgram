import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Cart,
    Favorite,
    Follow,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Tag
)
from users.models import User


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для связаной модели IngredientInRecipe."""
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
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


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

    def to_representation(self, instance):
        """Возвращаем данные автора с рецептами."""
        author = instance.author
        context = self.context.copy()
        return FollowDisplaySerializer(
            author,
            context=context
        ).data


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    """ Сериализатор для Favorite и Cart. """

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


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
        read_only_fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name'
        )

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания связи рецепт-ингредиент."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""
    ingredients = RecipeIngredientCreateSerializer(many=True, required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def create_or_update_ingredients(self, recipe, ingredients_data):
        """Создает или обновляет связи рецепта с ингредиентами."""
        recipe.ingredients.clear()

        ingredients_instances = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ]
        IngredientInRecipe.objects.bulk_create(ingredients_instances)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        author = self.context['request'].user

        recipe = Recipe.objects.create(
            author=author,
            **validated_data
        )
        recipe.tags.set(tags_data)

        self.create_or_update_ingredients(recipe, ingredients_data)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        instance = super().update(instance, validated_data)
        instance.tags.set(tags_data)
        self.create_or_update_ingredients(instance, ingredients_data)

        return instance

    def to_representation(self, instance):
        """При возврате данных используем RecipeDetailSerializer."""
        return RecipeDetailSerializer(
            instance,
            context=self.context
        ).data

    def validate(self, attrs):
        """Общая валидация для создания и обновления рецепта."""
        request = self.context['request']
        method = request.method

        if method == 'POST':
            if 'ingredients' not in attrs or not attrs['ingredients']:
                raise serializers.ValidationError({
                    'ingredients': 'Это поле обязательно для заполнения.'
                })
            if 'tags' not in attrs or not attrs['tags']:
                raise serializers.ValidationError({
                    'tags': 'Это поле обязательно для заполнения.'
                })

        if method == 'PATCH':
            if 'ingredients' not in attrs:
                raise serializers.ValidationError({
                    'ingredients': (
                        'Это поле обязательно при обновлении рецепта.'
                    )
                })
            if 'tags' not in attrs:
                raise serializers.ValidationError({
                    'tags': 'Это поле обязательно при обновлении рецепта.'
                })

        if 'ingredients' in attrs:
            ingredients = attrs['ingredients']
            if not ingredients:
                raise serializers.ValidationError({
                    'ingredients': 'Список ингредиентов не может быть пустым.'
                })

            ingredients_ids = [item['ingredient'].id for item in ingredients]
            if len(ingredients_ids) != len(set(ingredients_ids)):
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты не должны повторяться.'
                })

        if 'tags' in attrs:
            tags = attrs['tags']
            if not tags:
                raise serializers.ValidationError({
                    'tags': 'Список тегов не может быть пустым.'
                })

            tags_ids = [tag.id for tag in tags]
            if len(tags_ids) != len(set(tags_ids)):
                raise serializers.ValidationError({
                    'tags': 'Теги не должны повторяться.'
                })

        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для кастомной модели User."""
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
        request = self.context.get('request')

        return bool(
            request
            and request.user
            and request.user.is_authenticated
            and Follow.objects.filter(user=request.user, author=obj).exists()
        )

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
    author = UserSerializer(read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    ingredients = IngredientInRecipesSerializer(
        source='ingredientinrecipe_set',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
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
        """Проверяем, находится ли рецепт в избранном у пользователя."""
        request = self.context.get('request')

        return bool(
            request
            and request.user
            and request.user.is_authenticated
            and Favorite.objects.filter(user=request.user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Проверяем, находится ли рецепт в корзине у пользователя."""
        request = self.context.get('request')

        return bool(
            request
            and request.user
            and request.user.is_authenticated
            and Cart.objects.filter(author=request.user, recipe=obj).exists()
        )


class FollowDisplaySerializer(UserSerializer):
    """Сериализатор для отображения информации о пользователях,
    на которых оформлена подписка."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        """Получаем рецепты автора с поддержкой лимита."""
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit') if request else None

        recipes = obj.recipe_author.all()

        if limit:
            try:
                limit = int(limit)
                if limit > 0:
                    recipes = recipes[:limit]
            except ValueError:
                pass

        return RecipeFavoriteSerializer(
            recipes,
            many=True,
            context=self.context
        ).data

    def get_recipes_count(self, obj):
        """Получаем общее количество рецептов автора."""
        return obj.recipe_author.count()


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe',),
                message='Рецепт уже в избранном'
            )
        ]

    def to_representation(self, instance):
        """Возвращаем данные рецепта в нужном формате."""
        return RecipeFavoriteSerializer(
            instance.recipe,
            context=self.context
        ).data


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор для корзины покупок."""

    class Meta:
        model = Cart
        fields = ('author', 'recipe',)
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=('author', 'recipe',),
                message='Рецепт уже в корзине'
            )
        ]

    def to_representation(self, instance):
        """Возвращаем данные рецепта в нужном формате."""
        return RecipeFavoriteSerializer(
            instance.recipe,
            context=self.context
        ).data

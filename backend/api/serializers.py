from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import Tags, Recipes, Ingredients, IngredientInRecipes, Favorite, Cart


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


from django.contrib import admin

from recipes.models import (
    Favorite,
    IngredientInRecipes,
    Ingredients,
    Recipes,
    Tags
)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):

    list_display = ('name', 'slug')
    list_per_page = 20


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_per_page = 20


class IngredientInRecipesInline(admin.TabularInline):
    model = IngredientInRecipes


class FavoriteAdmin(admin.TabularInline):
    model = Favorite


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    """Админка для рецептов"""

    list_display = ('name', 'author', 'get_favorite_count')
    inlines = [IngredientInRecipesInline]
    filter_horizontal = ('tags',)
    search_fields = ('name', 'author')
    autocomplete_fields = ['author']
    list_per_page = 20

    @admin.display(description='В избранном')
    def get_favorite_count(self, obj):
        return obj.in_favorites.count()

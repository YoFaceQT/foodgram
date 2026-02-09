from django_filters import rest_framework as django_filters
from django_filters.rest_framework import FilterSet
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag, User


class IngredientSearchFilter(SearchFilter):
    """Поиск ингредиента по названию с частичным совпадением"""
    search_param = 'name'

    def filter_queryset(self, request, queryset, view):
        search_term = request.query_params.get(self.search_param, '').strip()

        if search_term:
            return queryset.filter(name__istartswith=search_term)

        return queryset


class RecipesFilterSet(FilterSet):
    """Фильтрация по избранному, автору, списку покупок и тегам."""
    is_favorited = django_filters.NumberFilter(method='filter_is_favorited')
    author = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация по избранным рецептам."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(in_favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация по рецептам в корзине покупок."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(cart__author=user)
        return queryset

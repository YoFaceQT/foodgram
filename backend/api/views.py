from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from api.serializers import TagsSerializer, IngredientsSerializer

from api.filters import RecipesFilterSet, IngredientSearchFilter
from recipes.models import Cart, Favorite, Follow, Ingredients, Recipes, Tags
from api.paginations import CustomPagination
from api.permissions import AdminAuthorOrReadOnly


class TagsViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Tags"""
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientsViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Ingredients"""
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = [IngredientSearchFilter]
    search_fields = ('^name',)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipes"""
    queryset = Recipes.objects.all()
    pagination_class = CustomPagination
    permission_classes = AdminAuthorOrReadOnly
    filter_class = RecipesFilterSet
    serializer_class = 
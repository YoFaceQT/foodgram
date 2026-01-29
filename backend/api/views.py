
from djoser.views import UserViewSet

from django.shortcuts import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


from api.serializers import (
    TagsSerializer,
    IngredientsSerializer,
    IngredientInRecipesSerializer,
    FavoriteSerializer,
    CartSerializer,
    FollowSerializer,
    FollowDisplaySerializer,
    RecipeFavoriteSerializer,
    AvatarSerializer,
    RecipeCreateUpdateSerializer,
    RecipeDetailSerializer,
    RecipeIngredientCreateSerializer,
    CustomUserSerializer,
)

from api.utilits import create_object, delete_object
from api.filters import RecipesFilterSet, IngredientSearchFilter
from recipes.models import Cart, Favorite, Follow, Ingredients, Recipes, Tags, IngredientInRecipes
from api.pagination import CustomPageNumberPagination
from users.models import User


from api.permissions import AdminAuthorOrReadOnly


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Tags"""
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    permission_classes = (AdminAuthorOrReadOnly,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Ingredients"""
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    permission_classes = (AdminAuthorOrReadOnly,)
    filter_backends = [IngredientSearchFilter]
    search_fields = ('^name',)


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipes"""
    queryset = Recipes.objects.all()
    pagination_class = CustomPageNumberPagination
    permission_classes = [AdminAuthorOrReadOnly]
    filterset_class = RecipesFilterSet

    def get_serializer_class(self):
        """Определяем сериализатор в зависимости от действия"""
        if self.action in ['list', 'retrieve']:
            return RecipeDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        elif self.action in ['favorite', 'shopping_cart']:
            return RecipeFavoriteSerializer
        return super().get_serializer_class()

    def get_serializer_context(self):
        """Добавляем контекст для сериализатора"""
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def perform_create(self, serializer):
        """Создание рецепта с привязкой к автору"""
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в избранное"""
        recipe = get_object_or_404(Recipes, pk=pk)
        user = request.user

        if request.method == 'POST':
            return create_object(Favorite, user, recipe, FavoriteSerializer)
        elif request.method == 'DELETE':
            return delete_object(Favorite, user, recipe)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта в список покупок"""
        recipe = get_object_or_404(Recipes, pk=pk)
        user = request.user

        if request.method == 'POST':
            return create_object(Cart, user, recipe, CartSerializer)
        elif request.method == 'DELETE':
            return delete_object(Cart, user, recipe)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок"""
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            return Response(
                {'detail': 'Список покупок пуст'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Собираем ингредиенты
        ingredients_dict = {}
        for cart_item in cart_items:
            recipe = cart_item.recipe
            ingredients = IngredientInRecipes.objects.filter(recipe=recipe)

            for ingredient_rel in ingredients:
                ingredient = ingredient_rel.ingredient
                amount = ingredient_rel.amount

                if ingredient.id in ingredients_dict:
                    ingredients_dict[ingredient.id]['amount'] += amount
                else:
                    ingredients_dict[ingredient.id] = {
                        'name': ingredient.name,
                        'measurement_unit': ingredient.measurement_unit,
                        'amount': amount
                    }

        # Формируем текстовый файл
        shopping_list = []
        shopping_list.append("Список покупок:\n")
        shopping_list.append("=" * 40 + "\n")

        for ingredient_data in ingredients_dict.values():
            shopping_list.append(
                f"• {ingredient_data['name']} "
                f"({ingredient_data['measurement_unit']}): "
                f"{ingredient_data['amount']}\n"
            )

        shopping_list.append("\n" + "=" * 40)
        shopping_list.append("\nПриятного аппетита!")

        response = HttpResponse(
            ''.join(shopping_list),
            content_type='text/plain'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )

        return response


class CustomUserViewSet(UserViewSet):
    """ Вьюсет для модели User. """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AdminAuthorOrReadOnly]

    @action(
        detail=True,
        methods=['post', 'delete'],
    )
    def subscribe(self, request, id):
        """ Метод создает/удаляет связь между пользователями. """
        if request.method == 'POST':
            serializer = create_object(
                request,
                id,
                FollowSerializer,
                FollowDisplaySerializer,
                User
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        delete_object(request, id, User, Follow)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
    )
    def subscriptions(self, request):
        """ Список подписок у пользователя. """
        user = request.user
        authors = User.objects.filter(subscribing__user=user)

        paged_queryset = self.paginate_queryset(authors)
        serializer = FollowDisplaySerializer(
            paged_queryset,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['PUT', 'PATCH', 'DELETE'],
        url_path='me/avatar',
        url_name='me-avatar',
        permission_classes=[IsAuthenticated],
    )
    def avatar(self, request):
        """Загрузка, обновление или удаление аватара текущего пользователя."""
        user = request.user

        if request.method in ['PUT', 'PATCH']:
            serializer = AvatarSerializer(
                user,
                data=request.data,
                partial=(request.method == 'PATCH')
            )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        elif request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=False)
                user.avatar = None
                user.save()
                return Response(
                    {'detail': 'Аватар успешно удален'},
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                {'detail': 'Аватар не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Получение данных текущего пользователя."""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Учетные данные не были предоставлены.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().me(request)

import datetime

from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import HttpResponse, get_object_or_404
from django.views import View
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipesFilterSet
from api.pagination import FoodgramPageNumberPagination
from api.permissions import IsAdminAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer,
    CartSerializer,
    FavoriteSerializer,
    FollowDisplaySerializer,
    FollowSerializer,
    IngredientsSerializer,
    RecipeCreateUpdateSerializer,
    RecipeDetailSerializer,
    TagsSerializer,
    UserSerializer
)
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


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Tag"""
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Ingredient"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = [IngredientSearchFilter]


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipes"""
    queryset = Recipe.objects.all().order_by('-id')
    pagination_class = FoodgramPageNumberPagination
    permission_classes = [IsAdminAuthorOrReadOnly]
    filterset_class = RecipesFilterSet
    filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        """Определяем сериализатор в зависимости от действия"""
        if self.action in ['list', 'retrieve']:
            return RecipeDetailSerializer
        else:
            return RecipeCreateUpdateSerializer

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Добавление рецепта в избранное."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        serializer = FavoriteSerializer(
            data={'user': user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        """Удаление рецепта из избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        deleted_count, _ = Favorite.objects.filter(
            user=user,
            recipe=recipe
        ).delete()

        if not deleted_count:
            return Response(
                {'detail': 'Рецепт не найден в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Добавление рецепта в корзину покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        serializer = CartSerializer(
            data={'author': user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        """Удаление рецепта из корзины покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        deleted_count, _ = Cart.objects.filter(
            author=user,
            recipe=recipe
        ).delete()

        if not deleted_count:
            return Response(
                {'detail': 'Рецепт не найден в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок в формате TXT"""
        user = request.user

        cart_items = Cart.objects.filter(author=user).select_related('recipe')

        recipe_ids = cart_items.values_list('recipe_id', flat=True)

        ingredients_list = (IngredientInRecipe.objects
                            .filter(recipe_id__in=recipe_ids)
                            .select_related('ingredient')
                            .values(
                                'ingredient__id',
                                'ingredient__name',
                                'ingredient__measurement_unit'
                            )
                            .annotate(total_amount=Sum('amount'))
                            .order_by('ingredient__name'))

        txt_content = []

        txt_content.append("СПИСОК ПОКУПОК")
        txt_content.append("=" * 50)
        txt_content.append(
            f"Пользователь: {user.get_full_name() or user.username}"
        )
        txt_content.append(
            f"Дата создания: {datetime.datetime.now():%d.%m.%Y %H:%M}"
        )
        txt_content.append("=" * 50)
        txt_content.append("")

        txt_content.append("ИНГРЕДИЕНТЫ:")
        txt_content.append("-" * 50)

        if ingredients_list:
            for idx, ingredient in enumerate(ingredients_list, 1):
                txt_content.append(
                    f"{idx}. {ingredient['ingredient__name']} - "
                    f"{ingredient['total_amount']} "
                    f"{ingredient['ingredient__measurement_unit']}"
                )
        else:
            txt_content.append("-")

        txt_content.append("")
        txt_content.append("=" * 50)
        txt_content.append("")

        txt_content.append("РЕЦЕПТЫ В КОРЗИНЕ:")
        txt_content.append("-" * 50)

        unique_recipes = {}
        for cart_item in cart_items:
            if cart_item.recipe_id not in unique_recipes:
                unique_recipes[cart_item.recipe_id] = cart_item.recipe.name

        if unique_recipes:
            for idx, recipe_name in enumerate(unique_recipes.values(), 1):
                txt_content.append(f"{idx}. {recipe_name}")
        else:
            txt_content.append("-")

        txt_content.append("")
        txt_content.append("=" * 50)
        txt_content.append("")
        txt_content.append(f"Всего рецептов: {len(unique_recipes)}")
        txt_content.append(f"Всего ингредиентов: {len(ingredients_list)}")

        txt_content_str = "\n".join(txt_content)

        filename = f"shopping_list_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt"

        response = HttpResponse(
            txt_content_str,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Cache-Control'] = 'no-cache'

        return response

    @action(
        detail=True,
        methods=['GET'],
        permission_classes=[AllowAny],
        url_path='get-link',
        url_name='get-link'
    )
    def get_short_link(self, request, pk=None):
        """Получение короткой ссылки на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        base_url = request.build_absolute_uri('/')
        base_url = base_url.rstrip('/')
        short_link = f"{base_url}/s/{recipe.short_code}"

        return Response({
            "short-link": short_link
        }, status=status.HTTP_200_OK)


class ShortLinkRedirectView(View):
    """Редирект по короткой ссылке."""

    def get(self, request, short_code):
        """Перенаправляет на страницу рецепта по короткому коду."""
        recipe = get_object_or_404(Recipe, short_code=short_code)

        base_url = request.build_absolute_uri('/')
        base_url = base_url.rstrip('/')
        recipe_url = f"{base_url}/api/recipes/{recipe.id}/"

        return HttpResponseRedirect(recipe_url)


class UserViewSet(UserViewSet):
    """ Вьюсет для модели User. """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        """Создание подписки на автора."""
        user = request.user
        author = get_object_or_404(User, id=id)

        serializer = FollowSerializer(
            data={'user': user.id, 'author': author.id},
            context={'request': request, 'author': author}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        """Удаление подписки на автора."""
        user = request.user
        author = get_object_or_404(User, id=id)

        deleted_count, _ = Follow.objects.filter(
            user=user,
            author=author
        ).delete()

        if not deleted_count:
            return Response(
                {'detail': 'Подписка не найдена'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """ Список подписок у пользователя. """
        user = request.user
        authors = User.objects.filter(following__user=user)

        paged_queryset = self.paginate_queryset(authors)
        serializer = FollowDisplaySerializer(
            paged_queryset,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['PUT'],
        url_path='me/avatar',
        url_name='me-avatar',
        permission_classes=[IsAuthenticated],
    )
    def avatar(self, request):
        """Загрузка, обновление или удаление аватара текущего пользователя."""
        user = request.user

        if request.method in ['PUT']:
            serializer = AvatarSerializer(
                user,
                data=request.data
            )

            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаление аватара текущего пользователя."""
        user = request.user

        if not user.avatar:
            return Response(
                {'detail': 'Аватар не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        user.avatar.delete(save=True)

        return Response(
            {'detail': 'Аватар успешно удален'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Получение данных текущего пользователя"""
        return super().me(request)

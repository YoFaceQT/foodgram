import base64
import datetime

from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipesFilterSet
from api.pagination import CustomPageNumberPagination
from api.permissions import AdminAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer,
    CustomUserSerializer,
    FollowDisplaySerializer,
    FollowSerializer,
    IngredientsSerializer,
    RecipeCreateUpdateSerializer,
    RecipeDetailSerializer,
    RecipeFavoriteSerializer,
    TagsSerializer
)
from api.utilits import create_object, delete_object
from recipes.models import (
    Cart,
    Favorite,
    Follow,
    IngredientInRecipes,
    Ingredients,
    Recipes,
    Tags
)
from users.models import User


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
    filter_backends = [DjangoFilterBackend]

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

    def partial_update(self, request, *args, **kwargs):
        """Редактироватирование рецепта."""
        recipe_id = self.kwargs['pk']
        recipe = get_object_or_404(Recipes, pk=recipe_id)
        self.check_object_permissions(request, recipe)
        serialazer = self.get_serializer(
            instance=recipe,
            data=request.data)
        serialazer.is_valid(raise_exception=True)
        result = serialazer.save()
        return Response(
            RecipeDetailSerializer(result, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

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
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            favorite = Favorite.objects.create(user=user, recipe=recipe)

            serializer = RecipeFavoriteSerializer(
                recipe,
                context={'request': request}
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            favorite = Favorite.objects.filter(
                user=user,
                recipe=recipe
            ).first()

            if not favorite:
                return Response(
                    {'detail': 'Рецепт не найден в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

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
            if Cart.objects.filter(author=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Cart.objects.create(author=user, recipe=recipe)

            serializer = RecipeFavoriteSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            cart_item = Cart.objects.filter(author=user, recipe=recipe).first()
            if not cart_item:
                return Response(
                    {'detail': 'Рецепт не найден в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.delete()
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
        cart_recipes = (Cart.objects
                        .filter(author=user)
                        .select_related('recipe'))

        if not cart_recipes.exists():
            return Response(
                {'detail': 'Корзина покупок пуста'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ingredients_list = (IngredientInRecipes.objects
                            .filter(recipe__cart__author=user)
                            .select_related('ingredient')
                            .values(
                                'ingredient__id',
                                'ingredient__name',
                                'ingredient__measurement_unit'
                            )
                            .annotate(total_amount=Sum('amount'))
                            .order_by('ingredient__name'))

        txt_content = (
            "СПИСОК ПОКУПОК\n"
            "=" * 50 + "\n"
            f"Пользователь: {user.get_full_name() or user.username}\n"
            f"Дата создания: {datetime.datetime.now():%d.%m.%Y %H:%M}\n"
            "=" * 50 + "\n\n"
            "ИНГРЕДИЕНТЫ:\n"
            "-" * 50 + "\n"
        )

        for idx, ingredient in enumerate(ingredients_list, 1):
            txt_content += (
                f"{idx}. {ingredient['ingredient__name']} - "
                f"{ingredient['total_amount']} "
                f"{ingredient['ingredient__measurement_unit']}\n"
            )

        txt_content += (
            "\n" + "=" * 50 + "\n"
            "\nРЕЦЕПТЫ В КОРЗИНЕ:\n"
            "-" * 50 + "\n"
        )

        for idx, cart_item in enumerate(cart_recipes, 1):
            txt_content += f"{idx}. {cart_item.recipe.name}\n"

        txt_content += (
            "\n" + "=" * 50 + "\n"
            f"\nВсего рецептов: {cart_recipes.count()}"
            f"\nВсего ингредиентов: {len(ingredients_list)}"
        )

        filename = f"shopping_list_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt"

        response = HttpResponse(
            txt_content,
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
        """Получение короткой ссылки на рецепт"""
        recipe = get_object_or_404(Recipes, pk=pk)

        recipe_id_bytes = str(recipe.id).encode('utf-8')
        short_hash = (
            base64.urlsafe_b64encode(recipe_id_bytes)
            .decode('utf-8')[:8]
        )

        domain = request.build_absolute_uri('/')[:-1]

        short_link = f"{domain}/s/{short_hash}"

        return Response({
            "short-link": short_link
        }, status=status.HTTP_200_OK)


class CustomUserViewSet(UserViewSet):
    """ Вьюсет для модели User. """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AdminAuthorOrReadOnly]

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        """ Метод создает/удаляет связь между пользователями. """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Учетные данные не были предоставлены."},
                status=status.HTTP_401_UNAUTHORIZED
            )

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

        elif request.method == 'DELETE':
            return delete_object(request, id, User, Follow)

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

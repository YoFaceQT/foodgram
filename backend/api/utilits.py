from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from api.serializers import RecipeFavoriteSerializer
from recipes.models import Follow
from users.models import User


def create_object(
        request, id,
        serializer_class,
        response_serializer_class,
        model_class
):
    """Создание объекта (для подписок)."""
    user = request.user
    author = get_object_or_404(User, id=id)
    if Follow.objects.filter(user=user, author=author).exists():
        raise ValidationError(
            {'detail': 'Вы уже подписаны на этого пользователя.'}
        )
    data = {'user': user.id, 'author': author.id}
    serializer = serializer_class(data=data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    response_serializer = response_serializer_class(
        author,
        context={'request': request}
    )
    return response_serializer


def delete_object(request, id, model_class, model):
    """Удаление объекта (для подписок)."""
    user = request.user
    author = get_object_or_404(User, id=id)
    try:
        obj = model.objects.get(user=user, author=author)
    except model.DoesNotExist:
        return Response(
            {'detail': 'Подписка не найдена'},
            status=status.HTTP_400_BAD_REQUEST
        )
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def create_favorite_cart(model, user, recipe, serializer_class):
    """Создание объекта (для избранного и корзины)."""
    if model.objects.filter(user=user, recipe=recipe).exists():
        raise ValidationError({'detail': 'Рецепт уже добавлен.'})
    obj = model.objects.create(user=user, recipe=recipe)
    serializer = RecipeFavoriteSerializer(
        recipe,
        context={
            'request': user._request if hasattr(user, '_request') else None
        }
    )
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_favorite_cart(model, user, recipe):
    """Удаление объекта (для избранного и корзины)."""
    obj = get_object_or_404(model, user=user, recipe=recipe)
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

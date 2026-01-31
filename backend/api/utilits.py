from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError


def create_object(model, user, recipe, serializer_class):
    """Создание объекта (для избранного и корзины)."""
    if model.objects.filter(author=user, recipe=recipe).exists():
        raise ValidationError({'error': 'Рецепт уже добавлен.'})
    obj = model.objects.create(author=user, recipe=recipe)

    serializer = serializer_class(
        obj,
        context={'request': user._request if hasattr(user, '_request') else None}
    )

    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_object(model, user, recipe):
    """Удаление объекта (для избранного и корзины)."""
    obj = get_object_or_404(model, author=user, recipe=recipe)
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
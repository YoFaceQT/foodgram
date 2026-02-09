from django.urls import include, path
from rest_framework import routers

from api.views import (
    CustomUserViewSet,
    IngredientsViewSet,
    RecipesViewSet,
    ShortLinkRedirectView,
    TagsViewSet
)


router = routers.DefaultRouter()
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('users', CustomUserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        's/<str:short_hash>/',
        ShortLinkRedirectView.as_view(),
        name='short_link_redirect'
    ),
]

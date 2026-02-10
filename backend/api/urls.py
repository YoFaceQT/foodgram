from django.urls import include, path
from rest_framework import routers

from api.views import (
    IngredientsViewSet,
    RecipesViewSet,
    ShortLinkRedirectView,
    TagsViewSet,
    UserViewSet
)


router = routers.DefaultRouter()
router.register('tags', TagsViewSet, basename='tags')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('s/<str:short_code>/',
         ShortLinkRedirectView.as_view(),
         name='short_link_redirect'),
]

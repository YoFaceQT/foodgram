from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import routers

from api.views import IngredientsViewSet, RecipesViewSet, TagsViewSet


router = routers.DefaultRouter()
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'recipes', RecipesViewSet, basename='recipes')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
#router.register(r'users', UserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    re_path(r'auth/', include('djoser.urls.authtoken')),
]
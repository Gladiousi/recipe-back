from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, RecipeIngredientViewSet

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', RecipeIngredientViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router.urls)),
]

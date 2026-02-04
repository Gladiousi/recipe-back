from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShoppingListViewSet, ShoppingItemViewSet

router = DefaultRouter()
router.register(r'lists', ShoppingListViewSet, basename='shopping-list')
router.register(r'items', ShoppingItemViewSet, basename='shopping-item')

urlpatterns = [
    path('', include(router.urls)),
]

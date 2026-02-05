# groups/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupViewSet, GroupInvitationViewSet

router = DefaultRouter()
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'invitations', GroupInvitationViewSet, basename='invitation')

urlpatterns = [
    path('', include(router.urls)),
]
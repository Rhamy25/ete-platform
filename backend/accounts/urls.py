from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, SessionAgentViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'sessions', SessionAgentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
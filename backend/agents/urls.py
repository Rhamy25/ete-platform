from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AgentViewSet, VehiculeViewSet, EquipeViewSet

router = DefaultRouter()
router.register(r'agents', AgentViewSet)
router.register(r'vehicules', VehiculeViewSet)
router.register(r'equipes', EquipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
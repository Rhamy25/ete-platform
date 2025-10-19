from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClientViewSet, ContratViewSet, ZoneCollecteViewSet, 
    BacPoubelleViewSet, DemandeProspectionViewSet
)

router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'contrats', ContratViewSet)
router.register(r'zones', ZoneCollecteViewSet)
router.register(r'bacs', BacPoubelleViewSet)
router.register(r'demandes-prospection', DemandeProspectionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
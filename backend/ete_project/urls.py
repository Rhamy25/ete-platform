"""
Configuration des URLs pour le projet ETE
Plateforme de gestion des ramassages d'ordures
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

# Configuration de l'admin
admin.site.site_header = "ETE - Administration"
admin.site.site_title = "ETE Admin"
admin.site.index_title = "Gestion des ramassages d'ordures"

# Router pour l'API REST
router = DefaultRouter()

urlpatterns = [
    # Page d'accueil
    path('', views.home_view, name='home'),
    path('api/status/', views.api_status, name='api_status'),
    
    # Administration Django
    path('admin/', admin.site.urls),
    
    # API REST
    path('api/', include(router.urls)),
    
    # Authentication JWT
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Authentication avec Djoser
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
    
    # URLs des applications
    path('api/accounts/', include('accounts.urls')),
    path('api/clients/', include('clients.urls')),
    path('api/agents/', include('agents.urls')),
    path('api/collectes/', include('collectes.urls')),
    path('api/paiements/', include('paiements.urls')),
    path('api/notifications/', include('notifications.urls')),
]

# Configuration pour les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

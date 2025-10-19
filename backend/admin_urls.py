from django.urls import path
import admin_views

# URLs pour l'interface d'administration personnalisée
urlpatterns = [
    # Dashboard principal
    path('dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/stats/', admin_views.admin_dashboard_stats, name='admin_dashboard_stats'),
    
    # Gestion des clients
    path('clients/', admin_views.admin_clients, name='admin_clients'),
    
    # Gestion des agents
    path('agents/', admin_views.admin_agents, name='admin_agents'),
    
    # Gestion des collectes
    path('collectes/', admin_views.admin_collectes, name='admin_collectes'),
    
    # Gestion des zones
    path('zones/', admin_views.admin_zones, name='admin_zones'),
    
    # Gestion des paiements
    path('paiements/', admin_views.admin_paiements, name='admin_paiements'),
    
    # Rapports
    path('rapports/', admin_views.admin_rapports, name='admin_rapports'),
    
    # Paramètres
    path('settings/', admin_views.admin_settings, name='admin_settings'),
    
    # Menu utilisateur
    path('profile/', admin_views.admin_profile, name='admin_profile'),
    path('preferences/', admin_views.admin_preferences, name='admin_preferences'), 
    path('notifications/', admin_views.admin_notifications, name='admin_notifications'),
    path('activity/', admin_views.admin_activity, name='admin_activity'),
    path('help/', admin_views.admin_help, name='admin_help'),
    path('support/', admin_views.admin_support, name='admin_support'),
    
    # Gestion des administrateurs
    path('add-admin/', admin_views.admin_add_admin, name='admin_add_admin'),
    
    # Page de test
    path('test/', admin_views.test_admin, name='test_admin'),
]
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta, datetime
from django.core.paginator import Paginator

from accounts.models import CustomUser
from clients.models import Client, ZoneCollecte
from agents.models import Agent, Equipe
from collectes.models import Collecte, Tournee, ReclamationCollecte
from paiements.models import Paiement

def get_sidebar_context():
    """Contexte global pour la sidebar"""
    return {
        'clients_count': Client.objects.filter(status='actif').count(),
        'agents_count': Agent.objects.filter(status='actif').count(),
        'collectes_pending': Tournee.objects.filter(status__in=['planifiee', 'en_cours']).count(),
        'zones_count': ZoneCollecte.objects.count(),
        'paiements_pending': Paiement.objects.filter(status='en_attente').count(),
    }

@staff_member_required
def admin_dashboard(request):
    """Dashboard principal de l'administration"""
    
    # Statistiques principales avec modèles disponibles
    stats = {
        'total_clients': Client.objects.count(),
        'new_clients_month': Client.objects.filter(
            date_inscription__gte=timezone.now() - timedelta(days=30)
        ).count(),
        'collectes_today': 15,  # Données statiques pour le moment
        'collectes_completed': 12,  # Données statiques
        'agents_active': Agent.objects.filter(
            user__is_active=True,
            status='actif'
        ).count(),
        'agents_on_route': 8,  # Données statiques
        'revenue_month': 125000,  # Données statiques en FCFA
        'revenue_growth': 15.2  # Données statiques
    }
    
    # Données pour les graphiques (7 derniers jours) - Données statiques
    chart_data = {
        'collectes_week': [
            {'day_short': 'Lun', 'count': 8, 'percentage': 53},
            {'day_short': 'Mar', 'count': 12, 'percentage': 80},
            {'day_short': 'Mer', 'count': 15, 'percentage': 100},
            {'day_short': 'Jeu', 'count': 10, 'percentage': 67},
            {'day_short': 'Ven', 'count': 14, 'percentage': 93},
            {'day_short': 'Sam', 'count': 6, 'percentage': 40},
            {'day_short': 'Dim', 'count': 4, 'percentage': 27},
        ]
    }
    
    # Top zones par nombre de clients
    top_zones = ZoneCollecte.objects.annotate(
        clients_count=Count('clients')
    ).order_by('-clients_count')[:5]
    
    # Ajouter couleurs et pourcentages
    total_clients_in_zones = sum(zone.clients_count for zone in top_zones)
    colors = ['#0f766e', '#14b8a6', '#5eead4', '#99f6e4', '#ccfbf1']
    
    for i, zone in enumerate(top_zones):
        zone.color = colors[i % len(colors)]
        zone.percentage = (zone.clients_count / max(1, total_clients_in_zones)) * 100 if total_clients_in_zones > 0 else 0
    
    # Données statiques pour les collectes récentes
    recent_collectes = []
    
    # Alertes système avec données disponibles
    alerts = {
        'agents_inactifs': Agent.objects.filter(
            user__last_login__lt=timezone.now() - timedelta(days=3)
        ).count(),
        'paiements_retard': 3,  # Données statiques
        'nouvelles_demandes': 5  # Données statiques
    }
    
    context = {
        'stats': stats,
        'chart_data': chart_data,
        'top_zones': top_zones,
        'recent_collectes': recent_collectes,
        'alerts': alerts,
        'clients_count': stats['total_clients'],
        'agents_count': stats['agents_active'],
        'collectes_pending': 8  # Données statiques
    }
    
    return render(request, 'admin_custom/dashboard.html', context)


@staff_member_required
def admin_dashboard_stats(request):
    """API pour mise à jour des statistiques en temps réel"""
    
    stats = {
        'total_clients': Client.objects.count(),
        'collectes_today': 15,  # Données statiques
        'agents_active': Agent.objects.filter(
            user__is_active=True,
            status='actif'
        ).count(),
        'revenue_month': 125000  # Données statiques en FCFA
    }
    
    return JsonResponse({'stats': stats})


@staff_member_required
def admin_clients(request):
    """Gestion des clients"""
    
    # Filtres de recherche
    search_query = request.GET.get('search', '')
    zone_filter = request.GET.get('zone', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset - utiliser les modèles disponibles
    clients = Client.objects.select_related('zone_collecte', 'user')
    
    # Application des filtres
    if search_query:
        clients = clients.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__phone__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(code_client__icontains=search_query)
        )
    
    if zone_filter:
        clients = clients.filter(zone_collecte_id=zone_filter)
    
    if status_filter:
        clients = clients.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(clients.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    clients_page = paginator.get_page(page_number)
    
    # Zones pour le filtre
    zones = ZoneCollecte.objects.all()
    
    context = {
        'clients': clients_page,
        'zones': zones,
        'search_query': search_query,
        'zone_filter': zone_filter,
        'status_filter': status_filter,
        'total_clients': clients.count(),
        **get_sidebar_context()
    }
    
    return render(request, 'admin_custom/clients.html', context)


@staff_member_required
def admin_agents(request):
    """Gestion des agents"""
    
    # Filtres
    search_query = request.GET.get('search', '')
    equipe_filter = request.GET.get('equipe', '')
    status_filter = request.GET.get('status', '')
    poste_filter = request.GET.get('poste', '')
    
    # Base queryset
    agents = Agent.objects.select_related('user', 'zone_principale')
    
    # Application des filtres
    if search_query:
        agents = agents.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(matricule__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    if equipe_filter:
        agents = agents.filter(equipes__id=equipe_filter)
    
    if status_filter:
        agents = agents.filter(status=status_filter)
    
    if poste_filter:
        agents = agents.filter(poste=poste_filter)
    
    # Pagination
    paginator = Paginator(agents.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    agents_page = paginator.get_page(page_number)
    
    # Équipes pour le filtre
    equipes = Equipe.objects.all()
    
    # Sessions actives (données statiques pour le moment)
    sessions_actives = []
    
    # Statistiques d'agents
    agents_actifs = Agent.objects.filter(status='actif').count()
    
    context = {
        'agents': agents_page,
        'equipes': equipes,
        'sessions_actives': sessions_actives,
        'search_query': search_query,
        'equipe_filter': equipe_filter,
        'status_filter': status_filter,
        'poste_filter': poste_filter,
        'total_agents': agents.count(),
        'agents_actifs': agents_actifs
    }
    
    return render(request, 'admin_custom/agents.html', context)


@staff_member_required
def admin_collectes(request):
    """Gestion des collectes"""
    
    # Filtres
    date_filter = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
    status_filter = request.GET.get('status', '')
    
    # Base queryset - utilisons Tournee à la place car les collectes sont liées aux tournées
    from collectes.models import Tournee
    tournees = Tournee.objects.select_related(
        'equipe_assignee', 'vehicule_assigne', 'zone_collecte'
    ).prefetch_related('collectes__client')
    
    # Application des filtres
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            tournees = tournees.filter(date_tournee=filter_date)
        except ValueError:
            pass
    
    if status_filter:
        tournees = tournees.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(tournees.order_by('-date_tournee'), 25)
    page_number = request.GET.get('page')
    tournees_page = paginator.get_page(page_number)
    
    # Données pour les filtres
    agents = Agent.objects.filter(statut='actif').select_related('user')
    zones = ZoneCollecte.objects.all()
    
    # Statistiques rapides
    stats = {
        'total': tournees.count(),
        'planifiees': tournees.filter(status='planifiee').count(),
        'en_cours': tournees.filter(status='en_cours').count(),
        'terminees': tournees.filter(status='terminee').count(),
    }
    
    context = {
        'tournees': tournees_page,
        'agents': agents,
        'zones': zones,
        'current_date': date_filter,
        'current_status': status_filter,
        'stats': stats,
        **get_sidebar_context()
    }
    
    return render(request, 'admin_custom/collectes.html', context)


@staff_member_required
@staff_member_required
def admin_zones(request):
    """Gestion des zones de collecte"""
    
    # Filtres
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset avec annotations
    zones = ZoneCollecte.objects.annotate(
        clients_count=Count('clients'),
        agents_count=Count('agents_principaux')
    ).select_related()
    
    # Application des filtres
    if search_query:
        zones = zones.filter(
            Q(nom_zone__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Le modèle ZoneCollecte n'a pas de champ is_active, on retire ce filtre pour le moment
    # if status_filter:
    #     zones = zones.filter(is_active=(status_filter == 'active'))
    
    # Tri
    zones = zones.order_by('nom_zone')
    
    # Statistiques
    total_zones = zones.count()
    zones_actives = total_zones  # Toutes les zones sont actives par défaut
    
    context = {
        'zones': zones,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_zones': total_zones,
        'zones_actives': zones_actives
    }
    
    return render(request, 'admin_custom/zones.html', context)


@staff_member_required
def admin_collectes(request):
    """Gestion des collectes et tournées"""
    
    # Filtres
    status_filter = request.GET.get('status', '')
    zone_filter = request.GET.get('zone', '')
    date_filter = request.GET.get('date', '')
    search_query = request.GET.get('q', '')
    
    # Récupérer les tournées
    tournees = Tournee.objects.select_related('equipe_assignee', 'vehicule_assigne', 'zone_collecte').all()
    
    # Appliquer les filtres
    if status_filter:
        tournees = tournees.filter(status=status_filter)
    if zone_filter:
        tournees = tournees.filter(zone_collecte_id=zone_filter)
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            tournees = tournees.filter(date_tournee=filter_date)
        except:
            pass
    if search_query:
        tournees = tournees.filter(
            Q(nom_tournee__icontains=search_query) |
            Q(equipe_assignee__nom_equipe__icontains=search_query) |
            Q(zone_collecte__nom_zone__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(tournees.order_by('-date_tournee', '-heure_debut_prevue'), 10)
    page_number = request.GET.get('page')
    tournees_page = paginator.get_page(page_number)
    
    # Statistiques
    stats = {
        'total_tournees': Tournee.objects.count(),
        'planifiees': Tournee.objects.filter(status='planifiee').count(),
        'en_cours': Tournee.objects.filter(status='en_cours').count(),
        'terminees': Tournee.objects.filter(status='terminee').count(),
        'annulees': Tournee.objects.filter(status='annulee').count(),
        'taux_completion': 0
    }
    
    # Calcul du taux de completion moyen
    tournees_terminees = Tournee.objects.filter(status='terminee')
    if tournees_terminees.exists():
        total_completion = sum(t.taux_completion for t in tournees_terminees)
        stats['taux_completion'] = round(total_completion / tournees_terminees.count(), 1)
    
    # Données pour les filtres
    zones = ZoneCollecte.objects.all()
    status_choices = Tournee.STATUS_CHOICES
    
    context = {
        'tournees': tournees_page,
        'zones': zones,
        'status_choices': status_choices,
        'stats': stats,
        'status_filter': status_filter,
        'zone_filter': zone_filter,
        'date_filter': date_filter,
        'search_query': search_query,
        **get_sidebar_context()
    }
    
    return render(request, 'admin_custom/collectes.html', context)


@staff_member_required
def admin_paiements(request):
    """Gestion des paiements"""
    
    # Filtres
    status_filter = request.GET.get('status', '')
    method_filter = request.GET.get('method', '')
    date_filter = request.GET.get('date', '')
    search_query = request.GET.get('q', '')
    
    # Base queryset
    paiements = Paiement.objects.select_related('client', 'facture')
    
    # Application des filtres
    if status_filter:
        paiements = paiements.filter(status=status_filter)
    
    if method_filter:
        paiements = paiements.filter(mode_paiement=method_filter)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            paiements = paiements.filter(date_paiement__date=filter_date)
        except ValueError:
            pass
    
    if search_query:
        paiements = paiements.filter(
            Q(numero_paiement__icontains=search_query) |
            Q(client__user__first_name__icontains=search_query) |
            Q(client__user__last_name__icontains=search_query) |
            Q(reference_transaction__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(paiements.order_by('-date_paiement'), 15)
    page_number = request.GET.get('page')
    paiements_page = paginator.get_page(page_number)
    
    # Statistiques
    stats = {
        'total_amount': paiements.filter(status='valide').aggregate(
            total=Sum('montant')
        )['total'] or 0,
        'pending_count': paiements.filter(status='en_attente').count(),
        'validated_count': paiements.filter(status='valide').count(),
        'refused_count': paiements.filter(status='refuse').count(),
    }
    
    context = {
        'paiements': paiements_page,
        'stats': stats,
        'status_filter': status_filter,
        'method_filter': method_filter,
        'date_filter': date_filter,
        'search_query': search_query,
        **get_sidebar_context()
    }
    
    return render(request, 'admin_custom/paiements.html', context)


@staff_member_required
@staff_member_required
def admin_rapports(request):
    """Page des rapports et analyses"""
    from django.utils import timezone
    from datetime import datetime, timedelta
    from django.db.models import Sum, Count, Avg, Q
    from decimal import Decimal
    import json
    
    # Récupération des paramètres de période
    periode = request.GET.get('periode', 'month')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    # Définir les dates selon la période
    today = timezone.now().date()
    
    if periode == 'today':
        date_debut = today
        date_fin = today
    elif periode == 'week':
        date_debut = today - timedelta(days=today.weekday())
        date_fin = today
    elif periode == 'month':
        date_debut = today.replace(day=1)
        date_fin = today
    elif periode == 'quarter':
        month = today.month
        quarter_start = ((month - 1) // 3) * 3 + 1
        date_debut = today.replace(month=quarter_start, day=1)
        date_fin = today
    elif periode == 'year':
        date_debut = today.replace(month=1, day=1)
        date_fin = today
    else:
        # Période personnalisée
        if date_debut:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
        else:
            date_debut = today.replace(day=1)
        
        if date_fin:
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
        else:
            date_fin = today
    
    # Import des modèles nécessaires
    from paiements.models import Paiement, Facture
    from collectes.models import Tournee, Collecte
    from clients.models import Client
    from agents.models import Agent
    from accounts.models import CustomUser
    
    # Calculs des statistiques principales
    paiements_periode = Paiement.objects.filter(
        date_paiement__date__range=[date_debut, date_fin],
        status='valide'
    )
    
    # Revenus totaux
    revenus_totaux = paiements_periode.aggregate(
        total=Sum('montant')
    )['total'] or Decimal('0')
    
    # Collectes de la période
    collectes_periode = Collecte.objects.filter(
        tournee__date_tournee__range=[date_debut, date_fin]
    )
    
    tournees_periode = Tournee.objects.filter(
        date_tournee__range=[date_debut, date_fin]
    )
    
    # Statistiques principales
    stats = {
        'revenus_totaux': revenus_totaux,
        'croissance_revenus': 15.2,  # À calculer vs période précédente
        'collectes_realisees': collectes_periode.filter(status='terminee').count(),
        'taux_realisation': 85.5,  # À calculer
        'clients_actifs': Client.objects.filter(
            paiement__date_paiement__date__range=[date_debut, date_fin],
            paiement__status='valide'
        ).distinct().count(),
        'nouveaux_clients': Client.objects.filter(
            created_at__date__range=[date_debut, date_fin]
        ).count(),
        'efficacite': 78.3,  # Indicateur global de performance
    }
    
    # Évolution des revenus (données pour graphique)
    revenus_evolution = {
        'labels': ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
        'data': [125000, 150000, 135000, 180000]
    }
    
    # Répartition des modes de paiement
    paiements_par_mode = paiements_periode.values('mode_paiement').annotate(
        count=Count('id')
    ).order_by('-count')
    
    paiements_repartition = {
        'labels': [p['mode_paiement'].replace('_', ' ').title() for p in paiements_par_mode],
        'data': [p['count'] for p in paiements_par_mode]
    }
    
    # Performance des agents
    agents_performance = []
    agents = CustomUser.objects.filter(user_type__in=['agent_ramassage', 'agent_collecte'])
    
    for agent in agents:
        # Essayons d'abord de récupérer l'agent profile
        try:
            agent_profile = agent.agent_profile
            collectes_agent = collectes_periode.filter(
                tournee__equipe_assignee__membres=agent_profile
            )
        except:
            # Si pas de profil agent, on simule des données
            collectes_agent = collectes_periode.none()
        
        paiements_agent = paiements_periode.filter(
            agent_collecteur=agent
        ).aggregate(total=Sum('montant'))['total'] or Decimal('0')
        
        performance = 85 if collectes_agent.exists() else 0  # Calcul simplifié
        
        agents_performance.append({
            'nom': agent.get_full_name() or agent.username,
            'type_agent': agent.user_type,
            'zone': 'Zone Centre',  # À adapter selon le modèle
            'collectes_realisees': collectes_agent.filter(status='terminee').count(),
            'collectes_prevues': collectes_agent.count(),
            'paiements_collectes': paiements_agent,
            'performance': performance
        })
    
    # Top zones performantes
    top_zones = [
        {
            'nom': 'Zone Centre',
            'clients_count': 25,
            'revenus': 450000,
            'taux_collecte': 92.5
        },
        {
            'nom': 'Zone Nord',
            'clients_count': 18,
            'revenus': 320000,
            'taux_collecte': 87.2
        },
        {
            'nom': 'Zone Sud',
            'clients_count': 22,
            'revenus': 380000,
            'taux_collecte': 89.1
        }
    ]
    
    # Indicateurs de qualité
    indicateurs = {
        'ponctualite': 87.5,
        'reclamations': 2.3,
        'recouvrement': 94.2,
        'satisfaction': 88.7
    }
    
    context = {
        'periode': periode,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'stats': stats,
        'revenus_evolution': json.dumps(revenus_evolution),
        'paiements_repartition': json.dumps(paiements_repartition),
        'agents_performance': agents_performance,
        'top_zones': top_zones,
        'indicateurs': indicateurs,
    }
    
    return render(request, 'admin_custom/rapports.html', context)


@staff_member_required
def admin_settings(request):
    """Paramètres système"""
    
    context = {}
    
    return render(request, 'admin_custom/settings.html', context)


@staff_member_required
def admin_profile(request):
    """Profil utilisateur"""
    context = {
        'user_stats': {
            'sessions_count': 142,
            'last_login': request.user.last_login,
            'total_actions': 1250,
            'created_at': request.user.date_joined,
        }
    }
    return render(request, 'admin_custom/profile.html', context)


@staff_member_required
def admin_preferences(request):
    """Préférences utilisateur"""
    context = {}
    return render(request, 'admin_custom/preferences.html', context)


@staff_member_required
def admin_notifications(request):
    """Page des notifications administrateur"""
    from datetime import timedelta
    
    notifications_sample = [
        {
            'id': 1,
            'type': 'collecte',
            'title': 'Collecte en retard',
            'message': 'Secteur Nord - Tournée non effectuée',
            'priority': 'haute',
            'read': False,
            'created_at': timezone.now() - timedelta(hours=2)
        },
        {
            'id': 2,
            'type': 'paiement',
            'title': 'Paiement en attente',
            'message': 'Facture #FAC-2024-156 - 25,000 FCFA',
            'priority': 'moyenne',
            'read': False,
            'created_at': timezone.now() - timedelta(hours=4)
        },
        {
            'id': 3,
            'type': 'client',
            'title': 'Nouveaux clients',
            'message': '2 inscriptions aujourd\'hui',
            'priority': 'basse',
            'read': False,
            'created_at': timezone.now() - timedelta(hours=6)
        },
        {
            'id': 4,
            'type': 'collecte',
            'title': 'Collecte terminée',
            'message': 'Secteur Centre - 45 collectes effectuées',
            'priority': 'basse',
            'read': True,
            'created_at': timezone.now() - timedelta(days=1)
        },
        {
            'id': 5,
            'type': 'systeme',
            'title': 'Mise à jour système',
            'message': 'Version 2.1.4 installée avec succès',
            'priority': 'basse',
            'read': True,
            'created_at': timezone.now() - timedelta(days=1)
        }
    ]
    
    # Calcul des statistiques
    unread_count = len([n for n in notifications_sample if not n['read']])
    today_count = len([n for n in notifications_sample if n['created_at'].date() == timezone.now().date()])
    week_count = len([n for n in notifications_sample if n['created_at'] >= timezone.now() - timedelta(days=7)])
    total_count = 156  # Simulation d'un total plus élevé
    
    context = {
        'notifications': {
            'list': notifications_sample,
            'unread_count': unread_count,
            'today_count': today_count,
            'week_count': week_count,
            'total_count': total_count
        }
    }
    return render(request, 'admin_custom/notifications.html', context)


@staff_member_required
def admin_activity(request):
    """Activité récente de l'utilisateur"""
    activities = [
        {
            'action': 'Création client',
            'target': 'Boukary Traoré',
            'time': '10 min',
            'icon': 'fa-user-plus',
            'color': 'green'
        },
        {
            'action': 'Validation paiement',
            'target': 'PAY-ABC123',
            'time': '25 min',
            'icon': 'fa-check-circle',
            'color': 'blue'
        },
        {
            'action': 'Planification tournée',
            'target': 'Zone Sud - 19/10/2025',
            'time': '1h',
            'icon': 'fa-calendar-plus',
            'color': 'purple'
        }
    ]
    context = {'activities': activities}
    return render(request, 'admin_custom/activity.html', context)


@staff_member_required
def admin_help(request):
    """Aide et documentation"""
    context = {}
    return render(request, 'admin_custom/help.html', context)


@staff_member_required
def admin_support(request):
    """Support technique"""
    context = {}
    return render(request, 'admin_custom/support.html', context)


@staff_member_required
def admin_add_admin(request):
    """Créer un nouvel administrateur"""
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone', '')
            username = request.POST.get('username')
            password = request.POST.get('password')
            admin_level = request.POST.get('admin_level', 'admin')
            permissions = request.POST.getlist('permissions')
            
            # Validation des données
            if not all([first_name, last_name, email, username, password]):
                return JsonResponse({
                    'success': False,
                    'error': 'Tous les champs obligatoires doivent être remplis'
                })
            
            # Vérifier si l'utilisateur existe déjà
            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Ce nom d\'utilisateur existe déjà'
                })
            
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Cette adresse email est déjà utilisée'
                })
            
            # Validation du mot de passe
            if len(password) < 8:
                return JsonResponse({
                    'success': False,
                    'error': 'Le mot de passe doit contenir au moins 8 caractères'
                })
            
            # Créer l'utilisateur
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type='admin',
                is_staff=True,
                is_active=True
            )
            
            # Définir les permissions selon le niveau d'admin
            if admin_level == 'superadmin':
                user.is_superuser = True
                user.save()
            
            # Créer le profil admin avec les permissions spécifiques
            # Note: Vous pouvez étendre ceci avec un modèle AdminProfile si nécessaire
            
            return JsonResponse({
                'success': True,
                'message': f'Administrateur {first_name} {last_name} créé avec succès',
                'admin_id': user.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erreur lors de la création: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})


@staff_member_required  
def test_admin(request):
    """Page de test pour l'interface admin"""
    return render(request, 'admin_custom/test_admin.html')
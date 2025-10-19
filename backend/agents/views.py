from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Avg, Q
from django.utils import timezone

from .models import Agent, Vehicule, Equipe
from .serializers import (
    AgentSerializer, VehiculeSerializer, EquipeSerializer,
    AgentPerformanceSerializer, VehiculeMaintenanceSerializer,
    EquipeStatsSerializer
)

User = get_user_model()

class AgentViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des agents"""
    
    queryset = Agent.objects.select_related('user', 'zone_principale').prefetch_related('zones_affectees')
    serializer_class = AgentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['poste', 'status', 'zone_principale']
    search_fields = ['matricule', 'user__first_name', 'user__last_name', 'user__email']
    ordering = ['matricule']
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        queryset = super().get_queryset()
        
        # Les agents ne voient que leur propre profil
        agent_types = ['agent_ramassage', 'agent_collecte', 'agent_prospection', 'agent_supervision']
        if self.request.user.user_type in agent_types:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """Liste des agents disponibles pour affectation"""
        if not (request.user.is_staff or request.user.user_type == 'agent_supervision'):
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        agents_disponibles = Agent.objects.filter(status='actif')
        serializer = AgentSerializer(agents_disponibles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def par_poste(self, request):
        """Statistiques des agents par poste"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = Agent.objects.values('poste').annotate(
            nombre=Count('id'),
            actifs=Count('id', filter=Q(status='actif'))
        ).order_by('poste')
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def affecter_zone(self, request, pk=None):
        """Affecter un agent à une zone"""
        if not (request.user.is_staff or request.user.user_type == 'agent_supervision'):
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        agent = self.get_object()
        zone_id = request.data.get('zone_id')
        
        try:
            from clients.models import ZoneCollecte
            zone = ZoneCollecte.objects.get(id=zone_id)
            
            if request.data.get('principale', False):
                agent.zone_principale = zone
            
            agent.zones_affectees.add(zone)
            agent.save()
            
            return Response({'message': 'Agent affecté à la zone avec succès'})
        except ZoneCollecte.DoesNotExist:
            return Response(
                {'error': 'Zone de collecte introuvable'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def performances(self, request, pk=None):
        """Performances d'un agent"""
        agent = self.get_object()
        
        # Calculer les performances (à adapter selon vos modèles de collecte)
        # Ici c'est un exemple, vous devrez l'adapter
        performances = {
            'agent_id': agent.id,
            'agent_name': agent.user.full_name,
            'nombre_tournees': 0,  # À calculer
            'taux_completion': 0,  # À calculer
            'note_moyenne': agent.note_evaluation or 0,
            'incidents': 0  # À calculer
        }
        
        serializer = AgentPerformanceSerializer(performances)
        return Response(serializer.data)

class VehiculeViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des véhicules"""
    
    queryset = Vehicule.objects.all()
    serializer_class = VehiculeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['type_vehicule', 'status']
    search_fields = ['numero_plaque', 'marque', 'modele']
    ordering = ['numero_plaque']
    
    @action(detail=False, methods=['get'])
    def operationnels(self, request):
        """Liste des véhicules opérationnels"""
        vehicules = Vehicule.objects.filter(status='operationnel')
        serializer = VehiculeSerializer(vehicules, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def maintenance_due(self, request):
        """Véhicules nécessitant une maintenance"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        today = timezone.now().date()
        vehicules = Vehicule.objects.filter(
            Q(prochaine_revision__lte=today) |
            Q(expiration_assurance__lte=today) |
            Q(expiration_controle_technique__lte=today)
        )
        
        serializer = VehiculeSerializer(vehicules, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def maintenance(self, request, pk=None):
        """Enregistrer une maintenance"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        vehicule = self.get_object()
        serializer = VehiculeMaintenanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Mettre à jour le véhicule selon le type de maintenance
        data = serializer.validated_data
        
        if data['type_maintenance'] == 'revision':
            vehicule.derniere_revision = data['date_maintenance']
            # Calculer prochaine révision (ex: +6 mois)
            from datetime import timedelta
            vehicule.prochaine_revision = data['date_maintenance'] + timedelta(days=180)
        
        if data.get('kilometrage'):
            vehicule.kilometrage = data['kilometrage']
        
        vehicule.save()
        
        # Ici vous pourriez créer un modèle MaintenanceRecord pour l'historique
        
        return Response({'message': 'Maintenance enregistrée avec succès'})

class EquipeViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des équipes"""
    
    queryset = Equipe.objects.select_related('chef_equipe', 'vehicule_assigne').prefetch_related('membres', 'zones_intervention')
    serializer_class = EquipeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['nom_equipe', 'chef_equipe__user__first_name', 'chef_equipe__user__last_name']
    ordering = ['nom_equipe']
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques des équipes"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = {
            'total_equipes': Equipe.objects.count(),
            'equipes_actives': Equipe.objects.filter(is_active=True).count(),
            'agents_disponibles': Agent.objects.filter(status='actif').count(),
            'vehicules_operationnels': Vehicule.objects.filter(status='operationnel').count()
        }
        
        serializer = EquipeStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def ajouter_membre(self, request, pk=None):
        """Ajouter un membre à l'équipe"""
        if not (request.user.is_staff or request.user.user_type == 'agent_supervision'):
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        equipe = self.get_object()
        agent_id = request.data.get('agent_id')
        
        try:
            agent = Agent.objects.get(id=agent_id, status='actif')
            equipe.membres.add(agent)
            
            return Response({'message': 'Membre ajouté à l\'équipe avec succès'})
        except Agent.DoesNotExist:
            return Response(
                {'error': 'Agent introuvable ou inactif'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def retirer_membre(self, request, pk=None):
        """Retirer un membre de l'équipe"""
        if not (request.user.is_staff or request.user.user_type == 'agent_supervision'):
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        equipe = self.get_object()
        agent_id = request.data.get('agent_id')
        
        try:
            agent = Agent.objects.get(id=agent_id)
            equipe.membres.remove(agent)
            
            return Response({'message': 'Membre retiré de l\'équipe avec succès'})
        except Agent.DoesNotExist:
            return Response(
                {'error': 'Agent introuvable'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def planning(self, request, pk=None):
        """Planning de l'équipe"""
        equipe = self.get_object()
        
        # Ici vous pourrez ajouter la logique pour récupérer
        # le planning/tournées de l'équipe
        
        data = {
            'equipe': EquipeSerializer(equipe).data,
            'jours_travail': equipe.jours_travail,
            'horaires': {
                'debut': equipe.heure_debut,
                'fin': equipe.heure_fin
            }
        }
        
        return Response(data)

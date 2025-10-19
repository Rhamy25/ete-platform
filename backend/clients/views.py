from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import Client, Contrat, ZoneCollecte, BacPoubelle, DemandeProspection
from .serializers import (
    ClientSerializer, ContratSerializer, ZoneCollecteSerializer,
    BacPoubelleSerializer, DemandeProspectionSerializer,
    ClientCreateFromProspectSerializer, ClientStatsSerializer
)

User = get_user_model()

class ZoneCollecteViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des zones de collecte"""
    
    queryset = ZoneCollecte.objects.all()
    serializer_class = ZoneCollecteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['nom_zone', 'code_zone']
    ordering = ['nom_zone']
    
    @action(detail=True, methods=['get'])
    def clients(self, request, pk=None):
        """Liste des clients dans cette zone"""
        zone = self.get_object()
        clients = Client.objects.filter(zone_collecte=zone)
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistiques des zones de collecte"""
        stats = ZoneCollecte.objects.annotate(
            nombre_clients=Count('clients'),
            clients_actifs=Count('clients', filter=Q(clients__status='actif'))
        ).values('id', 'nom_zone', 'nombre_clients', 'clients_actifs')
        
        return Response(stats)

class ClientViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des clients"""
    
    queryset = Client.objects.select_related('user', 'zone_collecte', 'agent_prospecteur').prefetch_related('contrats', 'bacs')
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['type_client', 'status', 'zone_collecte']
    search_fields = ['code_client', 'company_name', 'user__first_name', 'user__last_name', 'user__email']
    ordering = ['-date_inscription']
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        queryset = super().get_queryset()
        
        # Les clients ne voient que leur propre profil
        if self.request.user.user_type == 'client':
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques générales des clients"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        today = timezone.now()
        debut_mois = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        stats = {
            'total_clients': Client.objects.count(),
            'clients_actifs': Client.objects.filter(status='actif').count(),
            'clients_inactifs': Client.objects.filter(status='inactif').count(),
            'nouveaux_ce_mois': Client.objects.filter(date_inscription__gte=debut_mois).count(),
            'alertes_inactivite': Client.objects.filter(alerte_inactivite_envoyee=True).count()
        }
        
        serializer = ClientStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def inactifs(self, request):
        """Liste des clients inactifs (3 mois sans paiement)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Clients sans paiement depuis 3 mois
        limite_inactivite = timezone.now() - timedelta(days=90)
        clients_inactifs = Client.objects.filter(
            Q(dernier_paiement__lt=limite_inactivite) | Q(dernier_paiement__isnull=True)
        ).filter(status='actif')
        
        serializer = ClientSerializer(clients_inactifs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def marquer_inactif(self, request, pk=None):
        """Marquer un client comme inactif"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        client = self.get_object()
        client.status = 'inactif'
        client.alerte_inactivite_envoyee = True
        client.save()
        
        return Response({'message': 'Client marqué comme inactif'})
    
    @action(detail=True, methods=['get'])
    def historique(self, request, pk=None):
        """Historique complet du client (collectes, paiements, etc.)"""
        client = self.get_object()
        
        # Vérifier les permissions
        if client.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = {
            'client': ClientSerializer(client).data,
            'contrats': ContratSerializer(client.contrats.all(), many=True).data,
            'bacs': BacPoubelleSerializer(client.bacs.all(), many=True).data,
        }
        
        return Response(data)

class ContratViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des contrats"""
    
    queryset = Contrat.objects.select_related('client', 'client__user')
    serializer_class = ContratSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'frequence_collecte', 'client__zone_collecte']
    search_fields = ['numero_contrat', 'client__code_client', 'client__company_name']
    ordering = ['-date_debut']
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        queryset = super().get_queryset()
        
        # Les clients ne voient que leurs propres contrats
        if self.request.user.user_type == 'client':
            queryset = queryset.filter(client__user=self.request.user)
        
        return queryset

class BacPoubelleViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des bacs/poubelles"""
    
    queryset = BacPoubelle.objects.select_related('client', 'client__user')
    serializer_class = BacPoubelleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['type_bac', 'status', 'client__zone_collecte']
    search_fields = ['numero_bac', 'client__code_client']
    ordering = ['client', 'numero_bac']
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        queryset = super().get_queryset()
        
        # Les clients ne voient que leurs propres bacs
        if self.request.user.user_type == 'client':
            queryset = queryset.filter(client__user=self.request.user)
        
        return queryset

class DemandeProspectionViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des demandes de prospection"""
    
    queryset = DemandeProspection.objects.select_related('agent_assigne')
    serializer_class = DemandeProspectionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'type_service']
    search_fields = ['nom_complet', 'email', 'company_name']
    ordering = ['-date_demande']
    
    def get_permissions(self):
        """Permissions selon l'action"""
        if self.action == 'create':
            # Création libre pour les visiteurs
            return [permissions.AllowAny()]
        else:
            # Autres actions pour les utilisateurs authentifiés
            return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        queryset = super().get_queryset()
        
        # Les agents de prospection ne voient que leurs demandes assignées
        if self.request.user.user_type == 'agent_prospection':
            queryset = queryset.filter(agent_assigne=self.request.user)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def assigner(self, request, pk=None):
        """Assigner une demande à un agent de prospection"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        demande = self.get_object()
        agent_id = request.data.get('agent_id')
        
        try:
            agent = User.objects.get(id=agent_id, user_type='agent_prospection')
            demande.agent_assigne = agent
            demande.status = 'assignee'
            demande.date_assignation = timezone.now()
            demande.save()
            
            return Response({'message': 'Demande assignée avec succès'})
        except User.DoesNotExist:
            return Response(
                {'error': 'Agent de prospection introuvable'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def creer_client(self, request, pk=None):
        """Créer un client à partir d'une demande de prospection"""
        if request.user.user_type != 'agent_prospection':
            return Response(
                {'error': 'Seuls les agents de prospection peuvent créer des clients'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        demande = self.get_object()
        
        # Vérifier que l'agent est assigné à cette demande
        if demande.agent_assigne != request.user:
            return Response(
                {'error': 'Vous n\'êtes pas assigné à cette demande'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ClientCreateFromProspectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Créer l'utilisateur
        user_data = {
            'username': demande.email,
            'email': demande.email,
            'first_name': demande.nom_complet.split()[0],
            'last_name': ' '.join(demande.nom_complet.split()[1:]),
            'phone': demande.telephone,
            'user_type': 'client'
        }
        
        user = User.objects.create_user(**user_data, password='temp_password_123')
        
        # Créer le client
        client_data = {
            'user': user,
            'type_client': serializer.validated_data['type_client'],
            'company_name': demande.company_name,
            'service_address': demande.adresse,
            'service_city': demande.ville,
            'latitude': demande.latitude,
            'longitude': demande.longitude,
            'zone_collecte_id': serializer.validated_data['zone_collecte_id'],
            'agent_prospecteur': request.user,
            'status': 'actif'
        }
        
        client_serializer = ClientSerializer(data=client_data)
        client_serializer.is_valid(raise_exception=True)
        client = client_serializer.save()
        
        # Créer le contrat initial
        contrat_data = {
            'client': client,
            'frequence_collecte': serializer.validated_data['frequence_collecte'],
            'tarif_mensuel': serializer.validated_data['tarif_mensuel'],
            'jours_collecte': serializer.validated_data['jours_collecte'],
            'heure_passage': serializer.validated_data['heure_passage'],
            'types_dechets': serializer.validated_data['types_dechets'],
            'date_debut': timezone.now().date(),
            'date_fin': timezone.now().date() + timedelta(days=365),  # 1 an par défaut
            'status': 'actif'
        }
        
        contrat_serializer = ContratSerializer(data=contrat_data)
        contrat_serializer.is_valid(raise_exception=True)
        contrat_serializer.save()
        
        # Mettre à jour la demande
        demande.status = 'client_cree'
        demande.date_traitement = timezone.now()
        demande.save()
        
        return Response({
            'message': 'Client créé avec succès',
            'client_id': client.id,
            'code_client': client.code_client
        }, status=status.HTTP_201_CREATED)

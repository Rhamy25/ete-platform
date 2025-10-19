from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import UserProfile, QRCodeClient, SessionAgent
from .serializers import (
    CustomUserSerializer, UserProfileSerializer, 
    QRCodeClientSerializer, SessionAgentSerializer,
    UserRegistrationSerializer
)

User = get_user_model()

class CustomUserViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des utilisateurs"""
    
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_type', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering_fields = ['date_joined', 'last_name', 'first_name']
    ordering = ['-date_joined']
    
    def get_permissions(self):
        """Permissions selon l'action"""
        if self.action == 'create':
            # Inscription libre pour les visiteurs
            return [permissions.AllowAny()]
        elif self.action in ['list', 'retrieve']:
            # Lecture pour les utilisateurs authentifiés
            return [permissions.IsAuthenticated()]
        else:
            # Modification pour les admins uniquement
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
    
    def get_serializer_class(self):
        """Serializer selon l'action"""
        if self.action == 'register':
            return UserRegistrationSerializer
        return CustomUserSerializer
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Inscription d'un nouveau visiteur"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'Compte créé avec succès',
            'user_id': user.id,
            'email': user.email
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Récupérer le profil complet d'un utilisateur"""
        user = self.get_object()
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_profile(self, request, pk=None):
        """Mettre à jour le profil utilisateur"""
        user = self.get_object()
        
        # Vérifier que l'utilisateur modifie son propre profil ou est admin
        if user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission refusée'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        profile_data = request.data.get('profile', {})
        if profile_data and hasattr(user, 'profile'):
            profile_serializer = UserProfileSerializer(
                user.profile, 
                data=profile_data, 
                partial=True
            )
            if profile_serializer.is_valid():
                profile_serializer.save()
        
        user_serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data)
        
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def qr_code(self, request, pk=None):
        """Récupérer le QR code d'un client"""
        user = self.get_object()
        
        if user.user_type != 'client':
            return Response(
                {'error': 'QR code disponible uniquement pour les clients'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if hasattr(user, 'qr_code'):
            serializer = QRCodeClientSerializer(user.qr_code)
            return Response(serializer.data)
        
        return Response(
            {'error': 'QR code non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )

class SessionAgentViewSet(viewsets.ModelViewSet):
    """ViewSet pour les sessions d'agents"""
    
    queryset = SessionAgent.objects.all()
    serializer_class = SessionAgentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['agent__user_type', 'is_active']
    ordering = ['-heure_connexion']
    
    def get_queryset(self):
        """Filtrer selon le type d'utilisateur"""
        queryset = super().get_queryset()
        
        # Les agents ne voient que leurs propres sessions
        if self.request.user.user_type in ['agent_ramassage', 'agent_collecte', 'agent_prospection', 'agent_supervision']:
            queryset = queryset.filter(agent=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        """Créer une nouvelle session pour l'agent connecté"""
        # Fermer les sessions actives précédentes
        SessionAgent.objects.filter(
            agent=self.request.user, 
            is_active=True
        ).update(is_active=False, heure_deconnexion=timezone.now())
        
        # Créer la nouvelle session
        serializer.save(agent=self.request.user)
    
    @action(detail=False, methods=['post'])
    def start_session(self, request):
        """Démarrer une nouvelle session agent"""
        from django.utils import timezone
        
        # Vérifier que l'utilisateur est un agent
        if request.user.user_type not in ['agent_ramassage', 'agent_collecte', 'agent_prospection', 'agent_supervision']:
            return Response(
                {'error': 'Seuls les agents peuvent démarrer une session'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Fermer les sessions actives
        SessionAgent.objects.filter(
            agent=request.user, 
            is_active=True
        ).update(is_active=False, heure_deconnexion=timezone.now())
        
        # Créer nouvelle session
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = serializer.save(agent=request.user)
        
        return Response({
            'message': 'Session démarrée avec succès',
            'session_id': session.id,
            'heure_connexion': session.heure_connexion
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def end_session(self, request, pk=None):
        """Terminer une session agent"""
        from django.utils import timezone
        
        session = self.get_object()
        
        # Vérifier que c'est l'agent propriétaire de la session
        if session.agent != request.user:
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        session.is_active = False
        session.heure_deconnexion = timezone.now()
        session.save()
        
        return Response({
            'message': 'Session terminée avec succès',
            'duree_session': session.heure_deconnexion - session.heure_connexion
        })
    
    @action(detail=False, methods=['get'])
    def active_agents(self, request):
        """Liste des agents actuellement en session active"""
        # Uniquement pour les admins et superviseurs
        if not (request.user.is_staff or request.user.user_type == 'agent_supervision'):
            return Response(
                {'error': 'Permission refusée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        active_sessions = SessionAgent.objects.filter(
            is_active=True
        ).select_related('agent')
        
        serializer = SessionAgentSerializer(active_sessions, many=True)
        return Response(serializer.data)

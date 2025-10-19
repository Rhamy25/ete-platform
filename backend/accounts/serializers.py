from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, QRCodeClient, SessionAgent

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer pour les profils utilisateurs"""
    
    class Meta:
        model = UserProfile
        fields = [
            'address', 'city', 'postal_code', 'country',
            'latitude', 'longitude', 'receive_notifications', 
            'language', 'created_at', 'updated_at'
        ]

class QRCodeClientSerializer(serializers.ModelSerializer):
    """Serializer pour les QR codes clients"""
    
    class Meta:
        model = QRCodeClient
        fields = ['code_qr', 'qr_image', 'is_active', 'created_at']
        read_only_fields = ['code_qr', 'qr_image', 'created_at']

class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer pour les utilisateurs personnalisés"""
    
    profile = UserProfileSerializer(read_only=True)
    qr_code = QRCodeClientSerializer(read_only=True)
    password = serializers.CharField(write_only=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'phone', 'user_type', 'is_active', 'avatar', 
            'date_joined', 'updated_at', 'profile', 'qr_code',
            'password', 'full_name'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'date_joined': {'read_only': True},
            'updated_at': {'read_only': True},
        }
    
    def create(self, validated_data):
        """Créer un nouvel utilisateur avec mot de passe hashé"""
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """Mettre à jour l'utilisateur"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        return user

class SessionAgentSerializer(serializers.ModelSerializer):
    """Serializer pour les sessions d'agents"""
    
    agent_name = serializers.CharField(source='agent.full_name', read_only=True)
    agent_type = serializers.CharField(source='agent.user_type', read_only=True)
    
    class Meta:
        model = SessionAgent
        fields = [
            'id', 'agent', 'agent_name', 'agent_type',
            'latitude_connexion', 'longitude_connexion',
            'heure_connexion', 'heure_deconnexion', 
            'is_active', 'device_info'
        ]
        read_only_fields = ['heure_connexion']
    
    def validate(self, data):
        """Validation des données de session"""
        # Vérifier que l'agent est bien un agent de terrain
        agent_types = ['agent_ramassage', 'agent_collecte', 'agent_prospection', 'agent_supervision']
        if data['agent'].user_type not in agent_types:
            raise serializers.ValidationError(
                "Seuls les agents de terrain peuvent créer des sessions."
            )
        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription des nouveaux utilisateurs"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone', 'user_type', 'password', 'password_confirm'
        ]
    
    def validate(self, data):
        """Validation des mots de passe"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data
    
    def create(self, validated_data):
        """Créer un nouvel utilisateur"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
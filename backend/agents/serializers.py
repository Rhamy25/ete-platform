from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Agent, Vehicule, Equipe

User = get_user_model()

class AgentSerializer(serializers.ModelSerializer):
    """Serializer pour les agents"""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    zone_principale_nom = serializers.CharField(source='zone_principale.nom_zone', read_only=True)
    is_available = serializers.ReadOnlyField()
    
    # Relations imbriquées
    zones_affectees_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Agent
        fields = [
            'id', 'user', 'user_name', 'user_email', 'user_phone',
            'matricule', 'poste', 'status', 'date_embauche',
            'salaire_base', 'numero_securite_sociale', 'numero_permis',
            'type_permis', 'date_expiration_permis', 'certifications',
            'zones_affectees', 'zones_affectees_details', 'zone_principale',
            'zone_principale_nom', 'contact_urgence_nom', 'contact_urgence_phone',
            'contact_urgence_relation', 'note_evaluation', 'derniere_evaluation',
            'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['matricule']
    
    def get_zones_affectees_details(self, obj):
        """Détails des zones affectées"""
        from clients.serializers import ZoneCollecteSerializer
        return ZoneCollecteSerializer(obj.zones_affectees.all(), many=True).data
    
    def create(self, validated_data):
        """Créer un agent avec matricule automatique"""
        # Générer un matricule unique
        import uuid
        validated_data['matricule'] = f"AG-{uuid.uuid4().hex[:6].upper()}"
        return super().create(validated_data)

class VehiculeSerializer(serializers.ModelSerializer):
    """Serializer pour les véhicules"""
    
    is_operational = serializers.ReadOnlyField()
    
    class Meta:
        model = Vehicule
        fields = [
            'id', 'numero_plaque', 'marque', 'modele', 'annee',
            'type_vehicule', 'capacite_charge', 'capacite_volume',
            'status', 'kilometrage', 'derniere_revision', 'prochaine_revision',
            'numero_assurance', 'expiration_assurance', 'expiration_controle_technique',
            'equipements', 'consommation_moyenne', 'is_operational',
            'created_at', 'updated_at'
        ]

class EquipeSerializer(serializers.ModelSerializer):
    """Serializer pour les équipes"""
    
    chef_equipe_name = serializers.CharField(source='chef_equipe.user.full_name', read_only=True)
    vehicule_info = serializers.CharField(source='vehicule_assigne.numero_plaque', read_only=True)
    nombre_membres = serializers.ReadOnlyField()
    
    # Relations imbriquées
    membres_details = serializers.SerializerMethodField()
    zones_intervention_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Equipe
        fields = [
            'id', 'nom_equipe', 'chef_equipe', 'chef_equipe_name',
            'membres', 'membres_details', 'vehicule_assigne', 'vehicule_info',
            'zones_intervention', 'zones_intervention_details',
            'jours_travail', 'heure_debut', 'heure_fin', 'is_active',
            'nombre_membres', 'created_at', 'updated_at'
        ]
    
    def get_membres_details(self, obj):
        """Détails des membres de l'équipe"""
        return AgentSerializer(obj.membres.all(), many=True).data
    
    def get_zones_intervention_details(self, obj):
        """Détails des zones d'intervention"""
        from clients.serializers import ZoneCollecteSerializer
        return ZoneCollecteSerializer(obj.zones_intervention.all(), many=True).data
    
    def validate_chef_equipe(self, value):
        """Vérifier que le chef d'équipe a le bon poste"""
        if value and value.poste != 'chef_equipe':
            raise serializers.ValidationError(
                "Le chef d'équipe doit avoir le poste 'chef_equipe'."
            )
        return value
    
    def validate_vehicule_assigne(self, value):
        """Vérifier que le véhicule est opérationnel"""
        if value and not value.is_operational:
            raise serializers.ValidationError(
                "Le véhicule assigné doit être opérationnel."
            )
        return value

class AgentPerformanceSerializer(serializers.Serializer):
    """Serializer pour les performances d'agent"""
    
    agent_id = serializers.IntegerField()
    agent_name = serializers.CharField()
    nombre_tournees = serializers.IntegerField()
    taux_completion = serializers.DecimalField(max_digits=5, decimal_places=2)
    note_moyenne = serializers.DecimalField(max_digits=3, decimal_places=2)
    incidents = serializers.IntegerField()

class VehiculeMaintenanceSerializer(serializers.Serializer):
    """Serializer pour la maintenance des véhicules"""
    
    vehicule_id = serializers.IntegerField()
    type_maintenance = serializers.ChoiceField(choices=[
        ('revision', 'Révision'),
        ('reparation', 'Réparation'),
        ('controle_technique', 'Contrôle technique'),
        ('assurance', 'Renouvellement assurance')
    ])
    date_maintenance = serializers.DateField()
    description = serializers.CharField(max_length=500)
    cout = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    kilometrage = serializers.IntegerField(required=False)

class EquipeStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques d'équipe"""
    
    total_equipes = serializers.IntegerField()
    equipes_actives = serializers.IntegerField()
    agents_disponibles = serializers.IntegerField()
    vehicules_operationnels = serializers.IntegerField()
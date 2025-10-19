from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Client, Contrat, ZoneCollecte, BacPoubelle, DemandeProspection

User = get_user_model()

class ZoneCollecteSerializer(serializers.ModelSerializer):
    """Serializer pour les zones de collecte"""
    
    nombre_clients = serializers.ReadOnlyField()
    responsable_name = serializers.CharField(source='responsable.full_name', read_only=True)
    
    class Meta:
        model = ZoneCollecte
        fields = [
            'id', 'nom_zone', 'code_zone', 'description', 'couleur',
            'coordonnees_zone', 'responsable', 'responsable_name',
            'nombre_clients', 'created_at', 'updated_at'
        ]

class BacPoubelleSerializer(serializers.ModelSerializer):
    """Serializer pour les bacs/poubelles"""
    
    client_name = serializers.CharField(source='client.display_name', read_only=True)
    
    class Meta:
        model = BacPoubelle
        fields = [
            'id', 'client', 'client_name', 'numero_bac', 'type_bac',
            'capacite_litres', 'status', 'date_installation',
            'date_derniere_collecte', 'emplacement_description',
            'created_at', 'updated_at'
        ]

class ContratSerializer(serializers.ModelSerializer):
    """Serializer pour les contrats clients"""
    
    client_name = serializers.CharField(source='client.display_name', read_only=True)
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Contrat
        fields = [
            'id', 'client', 'client_name', 'numero_contrat',
            'date_debut', 'date_fin', 'frequence_collecte',
            'jours_collecte', 'heure_passage', 'tarif_mensuel',
            'devise', 'types_dechets', 'status', 'conditions_particulieres',
            'is_active', 'created_at', 'updated_at'
        ]

class ClientSerializer(serializers.ModelSerializer):
    """Serializer pour les clients"""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    zone_nom = serializers.CharField(source='zone_collecte.nom_zone', read_only=True)
    agent_prospecteur_name = serializers.CharField(source='agent_prospecteur.full_name', read_only=True)
    
    # Relations imbriquées
    contrats = ContratSerializer(many=True, read_only=True)
    bacs = BacPoubelleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Client
        fields = [
            'id', 'user', 'user_email', 'user_phone', 'user_name',
            'code_client', 'type_client', 'status', 'company_name',
            'contact_person', 'secondary_phone', 'service_address',
            'service_city', 'service_postal_code', 'latitude', 'longitude',
            'zone_collecte', 'zone_nom', 'billing_address', 'billing_city',
            'billing_postal_code', 'date_inscription', 'derniere_collecte',
            'dernier_paiement', 'notes', 'date_derniere_activite',
            'alerte_inactivite_envoyee', 'agent_prospecteur',
            'agent_prospecteur_name', 'contrats', 'bacs',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['code_client', 'date_inscription']
    
    def create(self, validated_data):
        """Créer un nouveau client avec code automatique"""
        # Générer un code client unique
        import uuid
        validated_data['code_client'] = f"CLI-{uuid.uuid4().hex[:8].upper()}"
        return super().create(validated_data)

class DemandeProspectionSerializer(serializers.ModelSerializer):
    """Serializer pour les demandes de prospection"""
    
    agent_assigne_name = serializers.CharField(source='agent_assigne.full_name', read_only=True)
    
    class Meta:
        model = DemandeProspection
        fields = [
            'id', 'nom_complet', 'email', 'telephone', 'company_name',
            'adresse', 'ville', 'latitude', 'longitude', 'type_service',
            'frequence_souhaitee', 'message', 'status', 'agent_assigne',
            'agent_assigne_name', 'date_demande', 'date_assignation',
            'date_visite_prevue', 'date_traitement', 'notes_agent',
            'raison_refus', 'created_at', 'updated_at'
        ]
        read_only_fields = ['date_demande', 'date_assignation', 'date_traitement']
    
    def validate_email(self, value):
        """Vérifier que l'email n'est pas déjà utilisé"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Un compte existe déjà avec cette adresse email."
            )
        return value

class ClientCreateFromProspectSerializer(serializers.Serializer):
    """Serializer pour créer un client à partir d'une demande de prospection"""
    
    demande_id = serializers.IntegerField()
    type_client = serializers.ChoiceField(choices=Client.CLIENT_TYPES)
    zone_collecte_id = serializers.IntegerField()
    
    # Contrat initial
    frequence_collecte = serializers.ChoiceField(choices=Contrat.FREQUENCY_CHOICES)
    tarif_mensuel = serializers.DecimalField(max_digits=10, decimal_places=2)
    jours_collecte = serializers.ListField(child=serializers.CharField())
    heure_passage = serializers.TimeField()
    types_dechets = serializers.ListField(child=serializers.CharField())
    
    def validate_demande_id(self, value):
        """Vérifier que la demande existe et est valide"""
        try:
            demande = DemandeProspection.objects.get(id=value)
            if demande.status not in ['assignee', 'en_cours']:
                raise serializers.ValidationError(
                    "Cette demande n'est pas dans un état valide pour créer un client."
                )
            return value
        except DemandeProspection.DoesNotExist:
            raise serializers.ValidationError("Demande de prospection introuvable.")
    
    def validate_zone_collecte_id(self, value):
        """Vérifier que la zone de collecte existe"""
        try:
            ZoneCollecte.objects.get(id=value)
            return value
        except ZoneCollecte.DoesNotExist:
            raise serializers.ValidationError("Zone de collecte introuvable.")

class ClientStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques clients"""
    
    total_clients = serializers.IntegerField()
    clients_actifs = serializers.IntegerField()
    clients_inactifs = serializers.IntegerField()
    nouveaux_ce_mois = serializers.IntegerField()
    alertes_inactivite = serializers.IntegerField()
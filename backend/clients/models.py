from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class Client(models.Model):
    """Modèle pour les clients d'ETE"""
    
    CLIENT_TYPES = (
        ('particulier', 'Particulier'),
        ('entreprise', 'Entreprise'),
        ('institution', 'Institution'),
    )
    
    STATUS_CHOICES = (
        ('actif', 'Actif'),
        ('en_attente', 'En attente'),
        ('inactif', 'Inactif'),
        ('suspendu', 'Suspendu'),
        ('prospect', 'Prospect'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    code_client = models.CharField(max_length=20, unique=True)
    type_client = models.CharField(max_length=15, choices=CLIENT_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='actif')
    
    # Informations de contact
    company_name = models.CharField(max_length=200, blank=True)  # Pour les entreprises
    contact_person = models.CharField(max_length=100, blank=True)
    secondary_phone = models.CharField(max_length=20, blank=True)
    
    # Adresse de service
    service_address = models.TextField()
    service_city = models.CharField(max_length=100)
    service_postal_code = models.CharField(max_length=20)
    
    # Coordonnées GPS pour la géolocalisation
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    
    # Zone de collecte assignée
    zone_collecte = models.ForeignKey(
        'ZoneCollecte', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='clients'
    )
    
    # Informations de facturation (si différente)
    billing_address = models.TextField(blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)
    
    # Métadonnées
    date_inscription = models.DateTimeField(auto_now_add=True)
    derniere_collecte = models.DateTimeField(blank=True, null=True)
    dernier_paiement = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)
    
    # Gestion de l'inactivité (règle: 3 mois sans paiement)
    date_derniere_activite = models.DateTimeField(auto_now=True)
    alerte_inactivite_envoyee = models.BooleanField(default=False)
    
    # Agent de prospection qui a créé ce client
    agent_prospecteur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'user_type': 'agent_prospection'},
        related_name='clients_prospectes'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['company_name', 'user__last_name']
    
    def __str__(self):
        if self.company_name:
            return f"{self.code_client} - {self.company_name}"
        return f"{self.code_client} - {self.user.full_name}"
    
    @property
    def display_name(self):
        return self.company_name if self.company_name else self.user.full_name


class Contrat(models.Model):
    """Contrats de service avec les clients"""
    
    FREQUENCY_CHOICES = (
        ('quotidien', 'Quotidien'),
        ('bi_hebdomadaire', 'Bi-hebdomadaire'),
        ('hebdomadaire', 'Hebdomadaire'),
        ('bi_mensuel', 'Bi-mensuel'),
        ('mensuel', 'Mensuel'),
    )
    
    STATUS_CHOICES = (
        ('actif', 'Actif'),
        ('expire', 'Expiré'),
        ('resilie', 'Résilié'),
        ('suspendu', 'Suspendu'),
    )
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contrats')
    numero_contrat = models.CharField(max_length=50, unique=True)
    
    # Détails du contrat
    date_debut = models.DateField()
    date_fin = models.DateField()
    frequence_collecte = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    jours_collecte = models.JSONField(default=list)  # Liste des jours de la semaine
    heure_passage = models.TimeField()
    
    # Tarification
    tarif_mensuel = models.DecimalField(max_digits=10, decimal_places=2)
    devise = models.CharField(max_length=3, default='TND')
    
    # Type de déchets
    types_dechets = models.JSONField(default=list)  # ['menagers', 'industriels', 'recyclables']
    
    # Statut et conditions
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='actif')
    conditions_particulieres = models.TextField(blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Contrat'
        verbose_name_plural = 'Contrats'
        ordering = ['-date_debut']
    
    def __str__(self):
        return f"Contrat {self.numero_contrat} - {self.client.display_name}"
    
    @property
    def is_active(self):
        from django.utils import timezone
        today = timezone.now().date()
        return (self.status == 'actif' and 
                self.date_debut <= today <= self.date_fin)


class ZoneCollecte(models.Model):
    """Zones de collecte pour organiser les tournées"""
    
    nom_zone = models.CharField(max_length=100)
    code_zone = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    # Couleur pour l'affichage sur la carte
    couleur = models.CharField(max_length=7, default='#1e3a8a')  # Format hex
    
    # Coordonnées du polygone de la zone
    coordonnees_zone = models.JSONField()  # Liste de coordonnées [lat, lng]
    
    # Responsable de zone
    responsable = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'user_type__in': ['manager', 'admin']}
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Zone de collecte'
        verbose_name_plural = 'Zones de collecte'
        ordering = ['nom_zone']
    
    def __str__(self):
        return f"{self.code_zone} - {self.nom_zone}"
    
    @property
    def nombre_clients(self):
        return self.clients.count()


class BacPoubelle(models.Model):
    """Bacs/poubelles associés aux clients"""
    
    TYPE_BAC_CHOICES = (
        ('plastique_120L', 'Plastique 120L'),
        ('plastique_240L', 'Plastique 240L'),
        ('metal_120L', 'Métal 120L'),
        ('metal_240L', 'Métal 240L'),
        ('conteneur_660L', 'Conteneur 660L'),
        ('conteneur_1100L', 'Conteneur 1100L'),
    )
    
    STATUS_CHOICES = (
        ('actif', 'Actif'),
        ('endommage', 'Endommagé'),
        ('perdu', 'Perdu'),
        ('remplace', 'Remplacé'),
    )
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bacs')
    numero_bac = models.CharField(max_length=50, unique=True)
    type_bac = models.CharField(max_length=20, choices=TYPE_BAC_CHOICES)
    capacite_litres = models.IntegerField()
    
    # Statut et état
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='actif')
    date_installation = models.DateField()
    date_derniere_collecte = models.DateTimeField(blank=True, null=True)
    
    # Localisation spécifique du bac
    emplacement_description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Bac/Poubelle'
        verbose_name_plural = 'Bacs/Poubelles'
        ordering = ['client', 'numero_bac']
    
    def __str__(self):
        return f"Bac {self.numero_bac} - {self.client.display_name}"


class DemandeProspection(models.Model):
    """Demandes de visiteurs pour devenir clients"""
    
    STATUS_CHOICES = (
        ('en_attente', 'En attente'),
        ('assignee', 'Assignée à un agent'),
        ('en_cours', 'En cours de traitement'),
        ('validee', 'Validée'),
        ('refusee', 'Refusée'),
        ('client_cree', 'Client créé'),
    )
    
    TYPE_SERVICE_CHOICES = (
        ('particulier_standard', 'Particulier - Service standard'),
        ('particulier_premium', 'Particulier - Service premium'),
        ('entreprise_petite', 'Entreprise - Petite structure'),
        ('entreprise_moyenne', 'Entreprise - Moyenne structure'),
        ('entreprise_grande', 'Entreprise - Grande structure'),
        ('institution', 'Institution publique'),
    )
    
    # Informations du demandeur
    nom_complet = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    company_name = models.CharField(max_length=200, blank=True)
    
    # Localisation
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    
    # Service souhaité
    type_service = models.CharField(max_length=30, choices=TYPE_SERVICE_CHOICES)
    frequence_souhaitee = models.CharField(max_length=20, blank=True)
    message = models.TextField(blank=True)
    
    # Suivi
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    agent_assigne = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'user_type': 'agent_prospection'},
        related_name='demandes_assignees'
    )
    
    # Dates
    date_demande = models.DateTimeField(auto_now_add=True)
    date_assignation = models.DateTimeField(blank=True, null=True)
    date_visite_prevue = models.DateTimeField(blank=True, null=True)
    date_traitement = models.DateTimeField(blank=True, null=True)
    
    # Notes
    notes_agent = models.TextField(blank=True)
    raison_refus = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Demande de prospection'
        verbose_name_plural = 'Demandes de prospection'
        ordering = ['-date_demande']
    
    def __str__(self):
        return f"Demande {self.nom_complet} - {self.get_status_display()}"

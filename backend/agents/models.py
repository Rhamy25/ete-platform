from django.db import models
from django.contrib.auth import get_user_model
from clients.models import ZoneCollecte

User = get_user_model()

class Agent(models.Model):
    """Modèle pour les agents de collecte"""
    
    STATUS_CHOICES = (
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('conge', 'En congé'),
        ('maladie', 'Maladie'),
        ('formation', 'En formation'),
    )
    
    POSTE_CHOICES = (
        ('chauffeur', 'Chauffeur'),
        ('collecteur', 'Collecteur'),
        ('chef_equipe', 'Chef d\'équipe'),
        ('superviseur', 'Superviseur'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    matricule = models.CharField(max_length=20, unique=True)
    poste = models.CharField(max_length=20, choices=POSTE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='actif')
    
    # Informations professionnelles
    date_embauche = models.DateField()
    salaire_base = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    numero_securite_sociale = models.CharField(max_length=50, blank=True)
    
    # Permis et certifications
    numero_permis = models.CharField(max_length=50, blank=True)
    type_permis = models.CharField(max_length=10, blank=True)  # B, C, D, etc.
    date_expiration_permis = models.DateField(blank=True, null=True)
    certifications = models.JSONField(default=list)  # Liste des certifications
    
    # Zone d'affectation
    zones_affectees = models.ManyToManyField('clients.ZoneCollecte', blank=True)
    zone_principale = models.ForeignKey(
        'clients.ZoneCollecte', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='agents_principaux'
    )
    
    # Informations d'urgence
    contact_urgence_nom = models.CharField(max_length=100, blank=True)
    contact_urgence_phone = models.CharField(max_length=20, blank=True)
    contact_urgence_relation = models.CharField(max_length=50, blank=True)
    
    # Évaluations et performances
    note_evaluation = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    derniere_evaluation = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'
        ordering = ['matricule']
    
    def __str__(self):
        return f"{self.matricule} - {self.user.full_name} ({self.get_poste_display()})"
    
    @property
    def is_available(self):
        return self.status == 'actif'


class Vehicule(models.Model):
    """Véhicules de collecte"""
    
    TYPE_VEHICULE_CHOICES = (
        ('camion_benne', 'Camion à benne'),
        ('camion_compacteur', 'Camion compacteur'),
        ('camionnette', 'Camionnette'),
        ('tracteur', 'Tracteur'),
    )
    
    STATUS_CHOICES = (
        ('operationnel', 'Opérationnel'),
        ('maintenance', 'En maintenance'),
        ('panne', 'En panne'),
        ('reforme', 'Réformé'),
    )
    
    numero_plaque = models.CharField(max_length=20, unique=True)
    marque = models.CharField(max_length=50)
    modele = models.CharField(max_length=50)
    annee = models.IntegerField()
    type_vehicule = models.CharField(max_length=20, choices=TYPE_VEHICULE_CHOICES)
    
    # Capacités
    capacite_charge = models.DecimalField(max_digits=8, decimal_places=2)  # en kg
    capacite_volume = models.DecimalField(max_digits=8, decimal_places=2)  # en m³
    
    # Statut et maintenance
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='operationnel')
    kilometrage = models.IntegerField(default=0)
    derniere_revision = models.DateField(blank=True, null=True)
    prochaine_revision = models.DateField(blank=True, null=True)
    
    # Assurance et contrôle technique
    numero_assurance = models.CharField(max_length=50, blank=True)
    expiration_assurance = models.DateField(blank=True, null=True)
    expiration_controle_technique = models.DateField(blank=True, null=True)
    
    # Équipement
    equipements = models.JSONField(default=list)  # GPS, compacteur, etc.
    
    # Consommation carburant
    consommation_moyenne = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # L/100km
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Véhicule'
        verbose_name_plural = 'Véhicules'
        ordering = ['numero_plaque']
    
    def __str__(self):
        return f"{self.numero_plaque} - {self.marque} {self.modele}"
    
    @property
    def is_operational(self):
        return self.status == 'operationnel'


class Equipe(models.Model):
    """Équipes de collecte"""
    
    nom_equipe = models.CharField(max_length=100)
    chef_equipe = models.ForeignKey(
        Agent, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='equipes_dirigees',
        limit_choices_to={'poste': 'chef_equipe'}
    )
    membres = models.ManyToManyField(Agent, related_name='equipes')
    vehicule_assigne = models.ForeignKey(
        Vehicule, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True
    )
    
    # Zone d'intervention
    zones_intervention = models.ManyToManyField('clients.ZoneCollecte')
    
    # Planification
    jours_travail = models.JSONField(default=list)  # Jours de la semaine
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    
    # Statut
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Équipe'
        verbose_name_plural = 'Équipes'
        ordering = ['nom_equipe']
    
    def __str__(self):
        return self.nom_equipe
    
    @property
    def nombre_membres(self):
        return self.membres.count()

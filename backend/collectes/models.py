from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Tournee(models.Model):
    """Tournées de collecte planifiées"""
    
    STATUS_CHOICES = (
        ('planifiee', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
        ('reportee', 'Reportée'),
    )
    
    nom_tournee = models.CharField(max_length=100)
    date_tournee = models.DateField()
    heure_debut_prevue = models.TimeField()
    heure_fin_prevue = models.TimeField()
    
    # Assignations
    equipe_assignee = models.ForeignKey('agents.Equipe', on_delete=models.CASCADE)
    vehicule_assigne = models.ForeignKey('agents.Vehicule', on_delete=models.CASCADE)
    zone_collecte = models.ForeignKey('clients.ZoneCollecte', on_delete=models.CASCADE)
    
    # Suivi temps réel
    heure_debut_reelle = models.TimeField(blank=True, null=True)
    heure_fin_reelle = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='planifiee')
    
    # Métriques
    nombre_clients_prevus = models.IntegerField(default=0)
    nombre_clients_realises = models.IntegerField(default=0)
    distance_parcourue = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    carburant_consomme = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    
    # Notes et observations
    notes = models.TextField(blank=True)
    problemes_rencontres = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tournée'
        verbose_name_plural = 'Tournées'
        ordering = ['-date_tournee', 'heure_debut_prevue']
    
    def __str__(self):
        return f"{self.nom_tournee} - {self.date_tournee}"
    
    @property
    def duree_prevue(self):
        from datetime import datetime, timedelta
        debut = datetime.combine(datetime.today(), self.heure_debut_prevue)
        fin = datetime.combine(datetime.today(), self.heure_fin_prevue)
        return fin - debut
    
    @property
    def taux_completion(self):
        if self.nombre_clients_prevus > 0:
            return (self.nombre_clients_realises / self.nombre_clients_prevus) * 100
        return 0


class Collecte(models.Model):
    """Collectes individuelles chez les clients"""
    
    STATUS_CHOICES = (
        ('planifiee', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('completee', 'Complétée'),
        ('ratee', 'Ratée'),
        ('reportee', 'Reportée'),
    )
    
    RAISON_ECHEC_CHOICES = (
        ('client_absent', 'Client absent'),
        ('acces_bloque', 'Accès bloqué'),
        ('pas_de_dechets', 'Pas de déchets'),
        ('vehicule_plein', 'Véhicule plein'),
        ('probleme_technique', 'Problème technique'),
        ('autre', 'Autre'),
    )
    
    tournee = models.ForeignKey(Tournee, on_delete=models.CASCADE, related_name='collectes')
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE)
    
    # Planification
    heure_passage_prevue = models.TimeField()
    ordre_passage = models.IntegerField()  # Ordre dans la tournée
    
    # Exécution
    heure_arrivee = models.TimeField(blank=True, null=True)
    heure_depart = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='planifiee')
    
    # Détails collecte
    types_dechets_collectes = models.JSONField(default=list)
    quantite_estimee = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)  # en kg
    nombre_contenants = models.IntegerField(default=0)
    
    # En cas d'échec
    raison_echec = models.CharField(max_length=20, choices=RAISON_ECHEC_CHOICES, blank=True)
    details_echec = models.TextField(blank=True)
    
    # Validation client
    signature_client = models.TextField(blank=True)  # Signature numérique encodée
    nom_signataire = models.CharField(max_length=100, blank=True)
    
    # Géolocalisation
    latitude_collecte = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude_collecte = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    
    # Photos et preuves
    photo_avant = models.ImageField(upload_to='collectes/photos/', blank=True, null=True)
    photo_apres = models.ImageField(upload_to='collectes/photos/', blank=True, null=True)
    
    # Notes
    notes_agent = models.TextField(blank=True)
    commentaire_client = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Collecte'
        verbose_name_plural = 'Collectes'
        ordering = ['tournee', 'ordre_passage']
    
    def __str__(self):
        return f"Collecte {self.client.display_name} - {self.tournee.date_tournee}"
    
    @property
    def duree_collecte(self):
        if self.heure_arrivee and self.heure_depart:
            from datetime import datetime, timedelta
            arrivee = datetime.combine(datetime.today(), self.heure_arrivee)
            depart = datetime.combine(datetime.today(), self.heure_depart)
            return depart - arrivee
        return None


class ReclamationCollecte(models.Model):
    """Réclamations liées aux collectes"""
    
    TYPE_RECLAMATION_CHOICES = (
        ('collecte_manquee', 'Collecte manquée'),
        ('collecte_incomplete', 'Collecte incomplète'),
        ('retard', 'Retard important'),
        ('dommage', 'Dommage matériel'),
        ('comportement', 'Comportement agent'),
        ('qualite_service', 'Qualité du service'),
        ('autre', 'Autre'),
    )
    
    STATUS_CHOICES = (
        ('ouverte', 'Ouverte'),
        ('en_traitement', 'En traitement'),
        ('resolue', 'Résolue'),
        ('fermee', 'Fermée'),
    )
    
    PRIORITE_CHOICES = (
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente'),
    )
    
    numero_reclamation = models.CharField(max_length=20, unique=True)
    collecte = models.ForeignKey(Collecte, on_delete=models.CASCADE, related_name='reclamations')
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE)
    
    # Détails réclamation
    type_reclamation = models.CharField(max_length=20, choices=TYPE_RECLAMATION_CHOICES)
    description = models.TextField()
    priorite = models.CharField(max_length=10, choices=PRIORITE_CHOICES, default='normale')
    
    # Suivi
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ouverte')
    date_ouverture = models.DateTimeField(auto_now_add=True)
    date_resolution = models.DateTimeField(blank=True, null=True)
    
    # Traitement
    assigne_a = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'user_type__in': ['manager', 'admin']}
    )
    actions_correctives = models.TextField(blank=True)
    
    # Satisfaction
    note_satisfaction = models.IntegerField(blank=True, null=True)  # 1-5
    commentaire_resolution = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Réclamation'
        verbose_name_plural = 'Réclamations'
        ordering = ['-date_ouverture']
    
    def __str__(self):
        return f"Réclamation {self.numero_reclamation} - {self.client.display_name}"

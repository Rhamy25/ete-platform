from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

User = get_user_model()

class Facture(models.Model):
    """Factures générées automatiquement selon la période de service"""
    
    STATUS_CHOICES = (
        ('brouillon', 'Brouillon'),
        ('emise', 'Émise'),
        ('payee', 'Payée'),
        ('partiellement_payee', 'Partiellement payée'),
        ('en_retard', 'En retard'),
        ('annulee', 'Annulée'),
    )
    
    PERIODE_CHOICES = (
        ('mensuel', 'Mensuel'),
        ('trimestriel', 'Trimestriel'),
        ('semestriel', 'Semestriel'),
        ('annuel', 'Annuel'),
    )
    
    numero_facture = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='factures')
    contrat = models.ForeignKey('clients.Contrat', on_delete=models.CASCADE)
    
    # Période facturée
    periode_facturation = models.CharField(max_length=15, choices=PERIODE_CHOICES, default='mensuel')
    date_debut_periode = models.DateField()
    date_fin_periode = models.DateField()
    
    # Montants
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2)
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('18.00'))
    montant_tva = models.DecimalField(max_digits=10, decimal_places=2)
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Détails services
    nombre_passages_prevu = models.IntegerField()
    nombre_passages_realise = models.IntegerField(default=0)
    quantite_collectee = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))  # en kg
    
    # Statut et dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='brouillon')
    date_emission = models.DateField()
    date_echeance = models.DateField()
    date_paiement_complet = models.DateTimeField(blank=True, null=True)
    
    # Génération automatique
    generee_automatiquement = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'
        ordering = ['-date_emission']
    
    def __str__(self):
        return f"Facture {self.numero_facture} - {self.client.display_name}"
    
    def save(self, *args, **kwargs):
        if not self.numero_facture:
            from datetime import datetime
            year = datetime.now().year
            self.numero_facture = f"ETE-{year}-{uuid.uuid4().hex[:8].upper()}"
        
        # Calcul automatique des montants
        self.montant_tva = (self.montant_ht * self.taux_tva) / 100
        self.montant_ttc = self.montant_ht + self.montant_tva
        
        super().save(*args, **kwargs)
    
    @property
    def montant_restant(self):
        """Calcule le montant restant à payer"""
        total_paye = sum(p.montant for p in self.paiements.filter(status='valide'))
        return self.montant_ttc - total_paye
    
    @property
    def is_en_retard(self):
        """Vérifie si la facture est en retard"""
        from django.utils import timezone
        return timezone.now().date() > self.date_echeance and self.status != 'payee'


class Paiement(models.Model):
    """Paiements effectués par les clients"""
    
    MODE_PAIEMENT_CHOICES = (
        ('espece', 'Espèces'),
        ('mobile_money', 'Mobile Money'),
        ('virement', 'Virement bancaire'),
        ('cheque', 'Chèque'),
        ('carte', 'Carte bancaire'),
        ('mypay_bf', 'MyPayBF (en ligne)'),
        ('abonnement_prepaye', 'Abonnement prépayé'),
    )
    
    STATUS_CHOICES = (
        ('en_attente', 'En attente de validation'),
        ('valide', 'Validé'),
        ('refuse', 'Refusé'),
        ('en_verification', 'En vérification (48h)'),
        ('annule', 'Annulé'),
    )
    
    numero_paiement = models.CharField(max_length=50, unique=True)
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='paiements')
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE)
    
    # Détails paiement
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES)
    
    # Agent collecteur (pour espèces et mobile money)
    agent_collecteur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'user_type': 'agent_collecte'},
        related_name='paiements_collectes'
    )
    
    # QR Code validation (obligatoire pour agent de collecte)
    qr_code_utilise = models.CharField(max_length=100, blank=True)
    qr_code_valide = models.BooleanField(default=False)
    
    # Géolocalisation du paiement
    latitude_paiement = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude_paiement = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    
    # Références externes
    reference_transaction = models.CharField(max_length=100, blank=True)  # Pour mobile money, MyPayBF
    numero_cheque = models.CharField(max_length=50, blank=True)
    
    # Statut et validation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    date_paiement = models.DateTimeField()
    date_validation = models.DateTimeField(blank=True, null=True)
    
    # Validation client (règle: 48h pour contester)
    valide_par_client = models.BooleanField(default=False)
    date_validation_client = models.DateTimeField(blank=True, null=True)
    conteste_par_client = models.BooleanField(default=False)
    motif_contestation = models.TextField(blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-date_paiement']
    
    def __str__(self):
        return f"Paiement {self.numero_paiement} - {self.client.display_name}"
    
    def save(self, *args, **kwargs):
        if not self.numero_paiement:
            self.numero_paiement = f"PAY-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def delai_validation_expire(self):
        """Vérifie si le délai de 48h pour validation client est expiré"""
        from django.utils import timezone
        from datetime import timedelta
        
        if self.status == 'valide' and not self.valide_par_client:
            limite = self.date_validation + timedelta(hours=48)
            return timezone.now() > limite
        return False


class Recu(models.Model):
    """Reçus générés pour chaque paiement (papier ou numérique)"""
    
    TYPE_RECU_CHOICES = (
        ('numerique', 'Numérique'),
        ('papier', 'Papier'),
        ('sms', 'SMS'),
        ('email', 'Email'),
    )
    
    paiement = models.OneToOneField(Paiement, on_delete=models.CASCADE, related_name='recu')
    numero_recu = models.CharField(max_length=50, unique=True)
    type_recu = models.CharField(max_length=15, choices=TYPE_RECU_CHOICES)
    
    # Contenu du reçu
    contenu_recu = models.JSONField()  # Stocke tous les détails du reçu
    
    # Signature numérique pour authentification
    signature_numerique = models.TextField(blank=True)
    
    # Envoi
    envoye = models.BooleanField(default=False)
    date_envoi = models.DateTimeField(blank=True, null=True)
    destinataire_email = models.EmailField(blank=True)
    destinataire_sms = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Reçu'
        verbose_name_plural = 'Reçus'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reçu {self.numero_recu}"
    
    def save(self, *args, **kwargs):
        if not self.numero_recu:
            self.numero_recu = f"REC-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)


class RapportPaiement(models.Model):
    """Rapports de collecte d'argent par agent"""
    
    agent_collecteur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'agent_collecte'}
    )
    
    date_rapport = models.DateField()
    zone_collecte = models.ForeignKey('clients.ZoneCollecte', on_delete=models.CASCADE)
    
    # Totaux de la journée
    nombre_paiements = models.IntegerField(default=0)
    montant_total_collecte = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    montant_especes = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    montant_mobile_money = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Statut
    transmis_admin = models.BooleanField(default=False)
    date_transmission = models.DateTimeField(blank=True, null=True)
    valide_par_admin = models.BooleanField(default=False)
    
    # Notes
    observations = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Rapport de paiement'
        verbose_name_plural = 'Rapports de paiement'
        unique_together = ['agent_collecteur', 'date_rapport']
        ordering = ['-date_rapport']
    
    def __str__(self):
        return f"Rapport {self.agent_collecteur.full_name} - {self.date_rapport}"

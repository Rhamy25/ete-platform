from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """Modèle utilisateur personnalisé pour ETE"""
    
    USER_TYPES = (
        ('admin', 'Administrateur ETE'),
        ('agent_ramassage', 'Agent de ramassage'),
        ('agent_collecte', 'Agent de collecte d\'argent'),
        ('agent_prospection', 'Agent de prospection'),
        ('agent_supervision', 'Agent de supervision'),
        ('client', 'Client'),
        ('visiteur', 'Visiteur'),
    )
    
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='client')
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_user_type_display()}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class UserProfile(models.Model):
    """Profil étendu pour les utilisateurs"""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Tunisie')
    
    # Coordonnées GPS
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    
    # Préférences
    receive_notifications = models.BooleanField(default=True)
    language = models.CharField(max_length=10, default='fr')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profil de {self.user.full_name}"


class QRCodeClient(models.Model):
    """QR Codes uniques pour chaque client"""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='qr_code')
    code_qr = models.CharField(max_length=100, unique=True)
    qr_image = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"QR Code - {self.user.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.code_qr:
            import uuid
            self.code_qr = f"ETE-{self.user.id}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)
        
        # Générer l'image QR code
        if not self.qr_image:
            self.generate_qr_image()
    
    def generate_qr_image(self):
        """Génère l'image QR code"""
        import qrcode
        from io import BytesIO
        from django.core.files.base import ContentFile
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.code_qr)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        filename = f'qr_{self.user.id}.png'
        self.qr_image.save(filename, ContentFile(buffer.getvalue()), save=False)
        buffer.close()
        
        super().save(update_fields=['qr_image'])


class SessionAgent(models.Model):
    """Sessions de connexion des agents sur le terrain"""
    
    agent = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        limit_choices_to={'user_type__in': ['agent_ramassage', 'agent_collecte', 'agent_prospection', 'agent_supervision']}
    )
    
    # Géolocalisation de connexion
    latitude_connexion = models.DecimalField(max_digits=10, decimal_places=8)
    longitude_connexion = models.DecimalField(max_digits=11, decimal_places=8)
    
    # Timestamps
    heure_connexion = models.DateTimeField(auto_now_add=True)
    heure_deconnexion = models.DateTimeField(null=True, blank=True)
    
    # Statut de la session
    is_active = models.BooleanField(default=True)
    
    # Métadonnées
    device_info = models.JSONField(default=dict)  # Infos sur l'appareil mobile
    
    class Meta:
        verbose_name = 'Session Agent'
        verbose_name_plural = 'Sessions Agents'
        ordering = ['-heure_connexion']
    
    def __str__(self):
        return f"Session {self.agent.full_name} - {self.heure_connexion}"

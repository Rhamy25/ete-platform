from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserProfile, QRCodeClient

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Crée automatiquement un profil utilisateur et un QR code pour les nouveaux clients"""
    if created:
        # Créer le profil utilisateur
        UserProfile.objects.create(user=instance)
        
        # Créer le QR code seulement si c'est un client (pas admin, agent, etc.)
        if instance.user_type == 'client':
            try:
                QRCodeClient.objects.create(user=instance)
            except Exception as e:
                print(f"Erreur création QR code: {e}")

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarde le profil utilisateur quand l'utilisateur est mis à jour"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
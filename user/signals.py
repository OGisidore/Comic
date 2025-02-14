from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a related profile or perform other actions
        pass

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.save()
from django.db import models  # type: ignore
import uuid

# Importations supplémentaires (facultatives)
from pygments.lexers import get_all_lexers  # type: ignore
from pygments.styles import get_all_styles  # type: ignore


class Character(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    generated_image = models.ImageField()
    referenceImage = models.ImageField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Character {self.id} - {self.userId}"


class Comic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Un tableau de Character
    genre = models.CharField(max_length=500, blank=True)
    theme = models.CharField(max_length=100, blank=True)
    author = models.CharField(max_length=500, blank=True)
    storytext = models.CharField( blank=True)
    storydetail = models.CharField(max_length=500, blank=True)
    characters = models.ImageField()
    title = models.CharField(max_length=500, blank=True)  # Utilisation d'un CharField pour limiter la longueur
    nbPages = models.IntegerField(blank=True, null=True)  # Corrigé
    nbPanelsPerPage = models.IntegerField(blank=True, null=True)  # Corrigé et renommé pour la cohérence
    # Les panels seront liés via le champ ForeignKey défini dans Panel (relation inversée)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comic {self.id} - {self.userId}"


class Panel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(blank=True)
    scenesImage = models.URLField(blank=True)  # Corrigé
    order = models.IntegerField(blank=True, null=True)  # Corrigé
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE, related_name='panels')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Panel {self.id} - {self.userId}"

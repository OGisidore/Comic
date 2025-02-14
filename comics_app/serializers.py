from rest_framework import serializers
from .models import Character, Comic, Panel

class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = ['id', 'generated_image', 'referenceImage', 'userId', 'created_at']

class PanelSerializer(serializers.ModelSerializer):
    # Pour afficher les informations des characters imbriqués dans un panel
    characters = CharacterSerializer(many=True, read_only=True)
    # Vous pouvez utiliser PrimaryKeyRelatedField pour l'écriture si besoin
    comic = serializers.PrimaryKeyRelatedField(queryset=Comic.objects.all())
    
    class Meta:
        model = Panel
        fields = [
            'id',
            'characters',
            "genre",
            'text',
            'scenesImage',
            'order',
            'comic',
            'userId',
            'created_at'
        ]

class ComicSerializer(serializers.ModelSerializer):
    # Affichage imbriqué des characters associés au comic
    characters = CharacterSerializer(many=True, read_only=True)
    # Affichage imbriqué des panels associés au comic (via related_name 'panels' défini dans Panel)
    panels = PanelSerializer(many=True, read_only=True)
    
    class Meta:
        model = Comic
        fields = [
            'id',
            'characters',
            'title',
            'nbPages',
            'nbPanelsPerPage',
            'panels',
            'userId',
            'created_at'
        ]

from rest_framework import serializers
from .models import Character, Comic, Panel

class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = ['id', 'generated_image', 'referenceImage', '', 'created_at']

class PanelSerializer(serializers.ModelSerializer):
    # Vous pouvez utiliser PrimaryKeyRelatedField pour l'écriture si besoin
    comic = serializers.PrimaryKeyRelatedField(queryset=Comic.objects.all())
    
    class Meta:
        model = Panel
        fields = [
            'id',
            'text',
            'scenesImage',
            'order',
            'comic',
            'created_at'
        ]

class ComicSerializer(serializers.ModelSerializer):
    # Affichage imbriqué des panels associés au comic (via related_name 'panels' défini dans Panel)
    panels = PanelSerializer(many=True, read_only=True)
    
    class Meta:
        model = Comic
        fields = [
            'id',
            "genre",
            "theme",
            "author",
            "storytext",
            "storydetail",
            'characters',
            'title',
            'nbPages',
            'nbPanelsPerPage',
            'panels',
            'created_at'
        ]

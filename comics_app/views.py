from django.shortcuts import render

# Create your views here.
from Comics import settings
# from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Character, Comic, Panel
from .serializer import CharacterSerializer , ComicSerializer
from django.core.files.base import ContentFile
import datetime 
import io
import os
from PIL import Image
from .ia import encode_image, generate_text_from_images, generate_image_from_text, generate_story_from_images , generate_question_from_text, get_text_from_audio, veri_response # Ajout des imports


# Placeholder function: Split the story into segments for each panel
def split_story_into_segments(story: str, total_panels: int) -> list:
    """
    Split the story into `total_panels` segments.
    This example splits the story by sentences and divides them evenly.
    You may wish to implement a more sophisticated logic.
    """
    sentences = story.split('. ')
    # Ensure that the last sentence ends with a period.
    sentences = [s if s.endswith('.') else s + '.' for s in sentences if s]
    # Calculate approximate number of sentences per panel.
    sentences_per_panel = max(1, len(sentences) // total_panels)
    segments = []
    for i in range(total_panels):
        start_index = i * sentences_per_panel
        end_index = start_index + sentences_per_panel
        segment = ' '.join(sentences[start_index:end_index]).strip()
        segments.append(segment)
    return segments

def convert_image_to_base64(image_field):
    """
    Convert an ImageField file to a base64 encoded string.
    You should implement error handling and file reading logic as required.
    """
    try:
            return encode_image(img_path)
    except Exception as e:
        return ""


class CreateCharacter(APIView):
    """
    POST /api/create-story/
    
    **Parameters (multipart/form-data)**:
    - image1: Image file (required)
    - image2: Image file (required)

    **Response (JSON)**:
    {
        "id": UUID,  # ID of the created story
        "generated_image": string,  # Name of the generated image
        "story_text": string,  # Generated story text
        "question": string,  # Generated question based on the story
        "user": string  # Username of the person who created the story
    }
    """
    def post(self, request, *args, **kwargs):

        try:
            # Extraction des images du body
            print("hello word")
            image1 = request.FILES.get('referenceImage')
            details = request.data.get('details')
            print(details)
            print(image1)
            # Sauvegarde temporaire des images pour l'encodage
            image1_path = f"temp_{image1.name}"
             # Enregistrer temporairement les images
            with open(image1_path, 'wb') as f:
                for chunk in image1.chunks():
                    f.write(chunk)
       
                prompt = "Generate a high-quality manga-style illustration of a character based on the provided reference image. The character should maintain their defining facial features and overall appearance but be transformed into a manga/anime style. Their expression, pose, and background should reflect their personality, which is described as [insert personality traits, e.g., 'confident and determined' or 'shy and kind'].The art style should resemble classic manga aesthetics, with clean line work, expressive eyes, and dynamic shading. Ensure the background complements the character’s personality—[describe an appropriate setting, e.g., 'a futuristic cyber city for a tech-savvy genius' or 'a peaceful cherry blossom garden for a calm and gentle soul']. The final image should feel like an authentic manga character portrait with vibrant details and an engaging atmosphere."
            base64_image_1 = encode_image(image1_path)
            # generated_text = generate_text_from_images(base64_image_1, base64_image_2, prompt)
            generated_image_bytes = generate_image_from_text(prompt )

 
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            generated_image_name = f"generated_image_{timestamp}.png"
            generated_image_path = os.path.join(settings.MEDIA_ROOT, generated_image_name)

            with open(generated_image_path, 'wb') as f:
                f.write(generated_image_bytes)


    
            # Enregistrer les données dans la base de données
            character = Character.objects.create(
                generated_image=generated_image_name,
                referenceImage=image1_path,
                user=request.user.username
            )

            serializer = CharacterSerializer(character)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Afficher ou logger le message d'erreur
            print("Une erreur est survenue :", str(e))
            # Vous pouvez également utiliser un module de logging ici
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class GetCommic(APIView):
    """
    GET /api/stories/
    
    **Paramètres** : Aucun

    **Réponse (JSON)** :
    [
        {
            "id": UUID,  # ID de l'histoire
            "generated_image": string,  # Nom de l'image générée
            "story_text": string,  # Texte de l'histoire
            "question": string,  # Question générée pour l'histoire
            "user": string  # Nom de l'utilisateur ayant créé l'histoire
        },
        ...
    ]
    """
    def get(self, request, comic_id):
        try:
            # Récupérer l'histoire avec l'ID
            comic = Comic.objects.get(id=comic_id)
            serializer = ComicSerializer(comic, many=False)
            return Response(serializer.data)

        except Comic.DoesNotExist:
            return Response({"error": "Story not found"}, status=status.HTTP_404_NOT_FOUND)


class GetAllCommics(APIView):
    """
    GET /api/stories/
    
    **Paramètres** : Aucun

    **Réponse (JSON)** :
    [
        {
            "id": UUID,  # ID de l'histoire
            "generated_image": string,  # Nom de l'image générée
            "story_text": string,  # Texte de l'histoire
            "question": string,  # Question générée pour l'histoire
            "user": string  # Nom de l'utilisateur ayant créé l'histoire
        },
        ...
    ]
    """
    def get(self, request):
        # Récupérer toutes les stories depuis la base de données
        stories = Comic.objects.all()
        # Sérialiser les stories
        serializer = ComicSerializer(stories, many=True)
        # Retourner la réponse au frontend sous forme de JSON
        return Response(serializer.data)




class CreateComics(APIView):
    """
    API view to create a comic based on user input.

    Process:
    1. Validate input data.
    2. Retrieve the Character objects based on provided character IDs.
    3. Construct a prompt using title, genre, nbPages, and nbPanelsPerPage.
    4. Generate a story using the prompt.
    5. Split the story into segments for each panel.
    6. For each segment, generate a panel image and create a Panel.
    7. Create a Comic instance and associate panels and characters.
    8. Return the created comic data.
    """

    def post(self, request, *args, **kwargs):
        data = request.data

        # Validate required fields: title, genre, and characters must be provided.
        if not data.get('title') or not data.get('genre') or not data.get('characters'):
            return Response(
                {'error': 'characters, genre, and title are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve Character objects based on a list of character IDs provided in the request.
        # Assuming 'characters' is a list of UUIDs.
        try:
            characters = Character.objects.filter(id__in=data.get('characters'))
            if not characters.exists():
                return Response(
                    {'error': 'No matching characters found.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve additional comic parameters from the request data.
        title = data.get('title')
        genre = data.get('genre')
        nbPages = data.get('nbPages', 1)  # Default to 1 if not provided.
        nbPanelsPerPage = data.get('nbPanelsPerPage', 4)  # Default to 1 if not provided.
        user_id = data.get('userId', 'default_user')

        # Construct a prompt to generate the story.
        # The prompt should include title, genre, number of pages, and panels per page.
        prompt = (
            f"Generate a comic story titled '{title}' in the '{genre}' genre. "
            f"The comic should have {nbPages} pages with {nbPanelsPerPage} panels per page. "
            "Each panel should contain at most 3 short sentences."
        )

        # Generate the story using an external function.
        story = generate_story(prompt)

        # Calculate total number of panels.
        total_panels = int(nbPages) * int(nbPanelsPerPage)
        # Split the generated story into segments corresponding to each panel.
        story_segments = split_story_into_segments(story, total_panels)

        # Create panels for the comic.
        panels = []
        for index, segment in enumerate(story_segments):
            # Convert associated character images to base64 strings.
            character_images_base64 = [
                convert_image_to_base64(character.generated_image) for character in characters
            ]
            # Construct a prompt to generate the panel image using the story segment and character visuals.
            panel_image_prompt = (
                f"Generate a scene image for the following story segment: '{segment}'. "
                f"Include character visuals: {character_images_base64}."
            )
            # Generate the panel image.
            panel_image = generate_panel_image(panel_image_prompt)
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            panel_image_name = f"panel_image_{timestamp}.png"
            panel_image_path = os.path.join(settings.MEDIA_ROOT, panel_image_name)

        with open(panel_image_path, 'wb') as f:
            f.write(generated_image_bytes)


            # Create a Panel instance. Note that we temporarily set comic to None; we will assign it later.
            panel = Panel.objects.create(
                text=segment,
                scenesImage=panel_image_name,  # Adjust this field if you need to handle file saving.
                order=index + 1,
                userId=user_id,
                comic=None  # Will be updated after creating the Comic.
            )
            panels.append(panel)

        # Create the Comic instance.
        comic = Comic.objects.create(
            title=title,
            nbPages=nbPages,
            nbPanelsPerPage=nbPanelsPerPage,
            userId=user_id
        )

        # Associate each Panel with the created Comic.
        for panel in panels:
            panel.comic = comic
            panel.save()

        # Associate the Character objects with the Comic (Many-to-Many relation).
        comic.characters.set(characters)
        comic.save()

        # Serialize the Comic instance to return as a response.
        response_data = ComicSerializer(comic).data

        return Response(response_data, status=status.HTTP_200_OK)

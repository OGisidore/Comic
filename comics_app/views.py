import base64
import aiohttp
from django.shortcuts import render

# Create your views here.
from Comics import settings
# from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Character, Comic, Panel
from .serializers import CharacterSerializer , ComicSerializer
# Si vous utilisez le ORM Django ou une fonction synchrone, utilisez sync_to_async
import datetime 
import io
import os
from PIL import Image
from asgiref.sync import async_to_sync, sync_to_async

from .ia import encode_image, generate_storyfromdee, generateSceneImage # Ajout des imports


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


async def convert_image_to_base64(image):
    if isinstance(image, str) and image.startswith("http"):
        # Si c'est une URL, télécharger l'image via aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(image) as response:
                if response.status == 200:
                    image_data = await response.read()
                    return base64.b64encode(image_data).decode('utf-8')
                else:
                    raise Exception(f"Erreur lors du téléchargement de l'image depuis l'URL : {response.status}")
    else:
        # Supposons qu'il s'agisse d'un objet File (issu de request.FILES)
        image_data = image.read()
        return base64.b64encode(image_data).decode('utf-8')


class CreateCharacter(APIView):
  
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
       
                prompt = f"Generate a high-quality manga-style illustration of a character based on the provided reference image. The character should maintain their defining facial features and overall appearance but be transformed into a manga/anime style. Their expression, pose, and background should reflect their personality, which is described as [insert personality traits, e.g., 'confident and determined' or 'shy and kind'] or this details {details}.The art style should resemble classic manga aesthetics, with clean line work, expressive eyes, and dynamic shading. Ensure the background complements the character’s personality—[describe an appropriate setting, e.g., 'a futuristic cyber city for a tech-savvy genius' or 'a peaceful cherry blossom garden for a calm and gentle soul'] or this details {details}. The final image should feel like an authentic manga character portrait with vibrant details and an engaging atmosphere."
            base64_image_1 = encode_image(image1_path)
            # generated_text = generate_text_from_images(base64_image_1, base64_image_2, prompt)
            generated_image_bytes = generateSceneImage(prompt,base64_image_1  )

 
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            generated_image_name = f"generated_image_{timestamp}.png"
            generated_image_path = os.path.join(settings.MEDIA_ROOT, generated_image_name)

            with open(generated_image_path, 'wb') as f:
                f.write(generated_image_bytes)


    
            # Enregistrer les données dans la base de données
            character = Character.objects.create(
                generated_image=generated_image_name,
                referenceImage=image1_path,
                # userId=request.user.username
            )

            serializer = CharacterSerializer(character)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Afficher ou logger le message d'erreur
            print("Une erreur est survenue :", str(e))
            # Vous pouvez également utiliser un module de logging ici
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class GetCommic(APIView):
 
    def get(self, request, comic_id):
        try:
            # Récupérer l'histoire avec l'ID
            comic = Comic.objects.get(id=comic_id)
            serializer = ComicSerializer(comic, many=False)
            return Response(serializer.data)

        except Comic.DoesNotExist:
            return Response({"error": "Story not found"}, status=status.HTTP_404_NOT_FOUND)


class GetAllCommics(APIView):

    def get(self, request):
        try:
            # Récupérer toutes les stories depuis la base de données
            stories = Comic.objects.all()
            
            # Sérialiser les stories
            serializer = ComicSerializer(stories, many=True)
            
            # Retourner la réponse au frontend sous forme de JSON
            return Response(serializer.data)

        except Comic.DoesNotExist:
            # En cas d'erreur liée à la récupération des objets
            return Response({"error": "Comics not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            # Capture toute autre erreur inattendue
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





# Fonctions synchrones à utiliser dans un contexte asynchrone
@sync_to_async
def create_comic_instance(title, storydetails, author, genre, story, nbPages, nbPanelsPerPage):
    return Comic.objects.create(
        title=title,
        storydetail=storydetails,
        storytext=story,
        author=author if author else "",
        genre=genre if genre else "",
        nbPages=nbPages,
        nbPanelsPerPage=nbPanelsPerPage,
    )

@sync_to_async
def create_panel_instance(segment, panel_image_name, index, comic):
    return Panel.objects.create(
        text=segment,
        scenesImage=panel_image_name,
        order=index + 1,
        comic=comic
    )

@sync_to_async
def serialize_data(comic):
    return ComicSerializer(comic).data

# Méthode pour sauvegarder le Comic après la création
@sync_to_async
def save_comic_instance(comic):
    comic.save()

# Méthode pour sauvegarder les panneaux
@sync_to_async
def save_panel_instance(panel):
    panel.save()
class CreateComics(APIView):
    """
    API view to create a comic based on user input.
    """
    
    def post(self, request, *args, **kwargs):
        # Exécution de la méthode asynchrone dans un contexte synchrone
        return async_to_sync(self._post)(request, *args, **kwargs)

    async def _post(self, request, *args, **kwargs):
        try:
            data = request.data

            # Validation des champs requis
            if not data.get('title') or not data.get('genre'):
                return Response(
                    {'error': 'title and genre are required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Récupération des images des personnages
            characters = request.FILES.getlist('characters')
            if not characters:
                # Si aucun fichier n'est uploadé, essayer de récupérer une ou plusieurs URL dans request.data
                characters = data.get('characters', [])
                if not isinstance(characters, list):
                    characters = [characters]
            
            if not characters:
                return Response(
                    {'error': 'At least one character image is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Récupération des autres paramètres du comic
            title = data.get('title')
            author = data.get('author')
            storydetails = data.get('storydetails')
            genre = data.get('genre')
            nbPages = int(data.get('nbPages', 1))
            nbPanelsPerPage = int(data.get('nbPanelsPerPage', 4))

            # Construction du prompt pour générer l'histoire
            prompt = (
                f"Generate a comic story titled '{title}' in the '{genre}' genre. and have content relate to {storydetails} "
                f"The comic should have {nbPages} pages with {nbPanelsPerPage} panels per page. "
                "Each panel should contain at most 3 short sentences."
            )

            # Génération de l'histoire
            story =  generate_storyfromdee(prompt)

            # Calcul du nombre total de panneaux et découpage de l'histoire en segments
            total_panels = int(nbPages) * int(nbPanelsPerPage)
            story_segments = split_story_into_segments(story, total_panels)

            # Création de l'instance Comic
            comic = await create_comic_instance(
                title, storydetails, author, genre, story, nbPages, nbPanelsPerPage
            )

            panels = []
            for index, segment in enumerate(story_segments):
                character_images_base64 = [
                    await convert_image_to_base64(image) for image in characters
                ]

                # Générer l'image de la scène
                panel_image_prompt = (
                    f"A highly detailed anime-style illustration depicting the scene: {segment}. "
                    "The setting is immersive, with cinematic lighting and rich details enhancing the atmosphere."
                )
                
                # Générer l'image de la scène
                panel_image_path = await generateSceneImage(panel_image_prompt, character_images_base64)
                

                # Si une image a bien été générée
                if panel_image_path:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    panel_image_name = f"panel_image_{timestamp}.webp"

                    panel_image_full_path = os.path.join(settings.MEDIA_ROOT, panel_image_name)
                    with open(panel_image_full_path, 'wb') as f:
                        with open(panel_image_path["generated_image_file_name"], 'rb') as generated_image:
                            f.write(generated_image.read())

                    # Création du panneau
                    panel = await create_panel_instance(segment, panel_image_path["image_url"], index, comic)
                    panels.append(panel)
                else:
                    print("Erreur lors de la génération de l'image pour le segment :", segment)

            for panel in panels:
                await save_panel_instance(panel)
            print("l'erreu2")

            # Sauvegarde du comic
            await save_comic_instance(comic)
            print("l'erreu3")


            # Sérialisation des données du comic
            response_data = await serialize_data(comic)
            print("l'erreu4")
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

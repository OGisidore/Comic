import base64
import requests
import openai
from openai import OpenAI
import dotenv
import os
import io
from runware import Runware, IPhotoMaker
import uuid
import aiohttp


# Load the .env file
dotenv.load_dotenv()

runware_api_key = os.getenv("API_RUNWARE_TOKEN")
deepseek_api_key= os.getenv("DEEPSEEK_API_KEY")


RUNWARE_API_URL = "https://api.runware.ai/v1"

DEEPSEEK_API_URL = "https://api.aimlapi.com/v1"

client = openai.OpenAI(
    base_url=DEEPSEEK_API_URL,
    api_key=deepseek_api_key
)
# Set headers for OpenAI API
runware_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {runware_api_key}"
}


# Set headers for OpenAI API
deepseek_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {deepseek_api_key}"
}


# Function to encode an image as base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')




def generate_storyfromdee(prompt):
    payload = {
        "model": "deepseek-ai/deepseek-llm-67b-chat",
        "messages": [
            {
                "role": "system",
                "content": "You are a story writer."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 150
    }

    try:
        response = requests.post(
            DEEPSEEK_API_URL + "/chat/completions",
            headers=deepseek_headers,
            json=payload,
            # timeout=30  # Ajout d'un timeout de 30s
        )
        response.raise_for_status()  # Déclenche une erreur en cas de réponse HTTP 4xx ou 5xx
    except requests.exceptions.Timeout:
        raise Exception("La requête a pris trop de temps. Essayez d'augmenter le timeout ou vérifiez l'API.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erreur lors de la requête à DeepSeek: {e}")

    try:
        response_json = response.json()
        # print(response_json)  # Débogage

        # Vérification du champ 'choices'
        if 'choices' in response_json and response_json['choices']:
            return response_json['choices'][0]['message']['content']
        else:
            raise Exception("Réponse invalide: 'choices' manquant ou vide.")
    except ValueError:
        raise Exception("La réponse n'est pas un JSON valide. Vérifiez le format de l'API.")


async def generateSceneImage(prompt: str, inputImagesBase64: list) -> str:
    # Décoder et sauvegarder chaque image temporairement
    image_files = []
    try:
        for i, inputImageBase64 in enumerate(inputImagesBase64):
            image_data = base64.b64decode(inputImageBase64)
            image_file = io.BytesIO(image_data)
            file_name = f"temp_input_{uuid.uuid4()}.webp"
            
            # Sauvegarde de l'image temporaire
            with open(file_name, "wb") as f:
                f.write(image_data)
            
            image_files.append(file_name)
            print(f"Image {i+1} décodée et sauvegardée temporairement sous : {file_name}")
    except Exception as e:
        print(f"Erreur lors du décodage de l'image base64 : {e}")
        return None
    
    # Connexion à Runware
    runware = Runware(api_key=runware_api_key)
    await runware.connect()
    print("connet")

    # Préparation de la requête pour générer l'image avec plusieurs images d'entrée
    request_image = IPhotoMaker(
        positivePrompt=prompt,
        steps=35,
        numberResults=1,
        height=512,
        width=512,
        model="civitai:101055@128078",
        style="Cinematic",
        strength=40,
        outputFormat="WEBP",
        includeCost=True,
        taskUUID=str(uuid.uuid4()),
        inputImages=image_files,  # Utilise la liste des fichiers temporaires
    )

    try:
        photos = await runware.photoMaker(requestPhotoMaker=request_image)

        async with aiohttp.ClientSession() as session:
            for photo in photos:
                image_url = photo.imageURL

                # Télécharger et sauvegarder l'image générée
                async with session.get(image_url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        generated_image_file_name = f"scene_{uuid.uuid4()}.webp"
                        with open(generated_image_file_name, "wb") as file:
                            file.write(image_data)
                        print(f"Image générée enregistrée sous : {generated_image_file_name}")
                        result={
                            "image_url": image_url,
                            "generated_image_file_name": generated_image_file_name
                            }
                        print("result", result)
                        return result  # Retourner le chemin de l'image générée
                    else:
                        print(f"Erreur lors du téléchargement de l'image : {response.status}")
                        result={
                            'image_url': image_url,
                            'generated_image_file_name': None
                    }
                        return result

    except Exception as e:
        print(f"Erreur lors de la génération de l'image : {e}")
        return None  # Retourne None si une erreur se produit
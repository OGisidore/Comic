import base64
import mimetypes
import requests
import openai
from openai import OpenAI
import dotenv
import os
import json
import io
from PIL import Image

# Load the .env file
dotenv.load_dotenv()

# OpenAI and HuggingFace API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
huggingface_api_key = os.getenv("API_TOKEN")

# OpenAI and HuggingFace API URLs
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"

client =openai.OpenAI()

# Set headers for OpenAI API
openai_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai_api_key}"
}

# Set headers for HuggingFace API
huggingface_headers = {
    "Authorization": f"Bearer {huggingface_api_key}"
}

# Function to encode an image as base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to generate text using OpenAI's API
def generate_text_from_images(image_1_base64, image_2_base64, prompt):
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_1_base64}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_2_base64}"}}
                ]
            }
        ],
        "max_tokens": 300
    }
    print(openai_api_key)
    response = requests.post(OPENAI_API_URL, headers=openai_headers, json=payload)
    response_json = response.json()

    print(response)
    print(response_json)
    
    # Extract the answer from the 'choices' field
    if 'choices' in response_json and len(response_json['choices']) > 0:
        return response_json['choices'][0]['message']['content']
    else:
        raise Exception("No answer found in the OpenAI response.")

def generate_story_from_images(image_1_base64, prompt):
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_1_base64}"}}
                    
                ]
            }
        ],
        "max_tokens": 300
    }
    
    response = requests.post(OPENAI_API_URL, headers=openai_headers, json=payload)
    response_json = response.json()
    
    # Extract the answer from the 'choices' field
    if 'choices' in response_json and len(response_json['choices']) > 0:
        return response_json['choices'][0]['message']['content']
    else:
        raise Exception("No answer found in the OpenAI response.")

def generate_question_from_text(text, prompt):
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "text", "questions": text}
                    
                ]
            }
        ],
        "max_tokens": 300
    }
    
    response = requests.post(OPENAI_API_URL, headers=openai_headers, json=payload)
    response_json = response.json()
    
    # Extract the answer from the 'choices' field
    if 'choices' in response_json and len(response_json['choices']) > 0:
        return response_json['choices'][0]['message']['content']
    else:
        raise Exception("No answer found in the OpenAI response.")

# Function to generate an image based on the text using Hugging Face's FLUX model
def generate_image_from_text(text):
    payload = {"inputs": text}
    
    response = requests.post(HUGGINGFACE_API_URL, headers=huggingface_headers, json=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.content  # Return image bytes if successful
    else:
        raise Exception(f"Failed to generate image: {response.status_code}, {response.text}")

def get_text_from_audio(audio_file):
   
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    return transcription.text

# def get_llm_response(prompt):
#     response = client.chat.completions.create(
#     model="gpt-4",
#     messages=[
#         {"role": "system", "content": "You are an IEP Advocate."},
#         {"role": "user", "content": prompt}
#     ]
#     )
#     response_json = response.json()
    
#     # Extract the answer from the 'choices' field
#     if 'choices' in response_json and len(response_json['choices']) > 0:
#         print( response_json['choices'][0]['message']['content'])
#         return response_json['choices'][0]['message']['content']
#     else:
#         raise Exception("No answer found in the OpenAI response.")


def veri_response( prompt):
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content":prompt
            }
        ],
        "max_tokens": 300
    }
    
    response = requests.post(OPENAI_API_URL, headers=openai_headers, json=payload)
    response_json = response.json()
    
    # Extract the answer from the 'choices' field
    if 'choices' in response_json and len(response_json['choices']) > 0:
        return response_json['choices'][0]['message']['content']
    else:
        raise Exception("No answer found in the OpenAI response.")

def get_llm_response(prompt):
    # Assurez-vous que 'client' est bien une instance valide de votre client OpenAI
    payload = {
        "model":"gpt-4o-mini",  # Utilisez le modèle correct (gpt-4 ou gpt-3.5-turbo)
        "messages":[
            {"role": "system", "content": "You are an IEP Advocate."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300
    }
    response = requests.post(OPENAI_API_URL, headers=openai_headers, json=payload)
    response_json = response.json()
    
    if 'choices' in response_json and len(response_json['choices']) > 0:
        return response_json['choices'][0]['message']['content']
    else:
        raise Exception("No answer found in the OpenAI response.")
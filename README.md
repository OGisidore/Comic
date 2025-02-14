# 📖 Comics API

## 📝 Description
Comics API is a web application that allows users to generate manga/comic-style stories from images and text. It leverages Django and Django REST Framework for the backend, integrating OpenAI and Hugging Face APIs for content generation.

---

## 🚀 Features

- 📌 **Create characters** from user-uploaded reference images.
- ✏️ **Generate stories** based on characters and prompts.
- 🎨 **Generate illustrations** in manga style using AI.
- 📖 **Structure stories into pages and panels** dynamically.
- 🔍 **Retrieve and view** saved comics and characters.
- 🔑 **JWT authentication** for secure API access.

---

## 🏗️ Technologies Used

- **Django** & **Django REST Framework** 🐍
- **OpenAI API** (GPT-4o) 🤖
- **Hugging Face FLUX Model** 🎨
- **Pillow** for image processing 🖼️
- **PostgreSQL** (or SQLite depending on the configuration) 🗄️
- **Swagger & Redoc** for API documentation 📜

---

## 📂 Project Structure

comics_project/ │── comics_app/ │ ├── models.py # Data models (Characters, Comics, Panels) │ ├── views.py # Business logic & API endpoints │ ├── serializers.py # Model serialization │ ├── urls.py # App routes │ ├── ia.py # AI functions for image & text generation │── user/ │── settings.py # Django configuration │── urls.py # Global routes │── manage.py # Django CLI command

---

## 🔧 Installation & Setup

### 1️⃣ Prerequisites

- Python 3.9+
- PostgreSQL or SQLite
- OpenAI and Hugging Face API keys

### 2️⃣ Installation

```bash
git clone https://github.com/your-repo/comics-api.git
cd comics-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
3️⃣ Environment Variables
Create a .env file and add:
OPENAI_API_KEY="your_openai_api_key"
API_TOKEN="your_huggingface_api_token"
DJANGO_SECRET_KEY="your_secret_key"
DEBUG=True

4️⃣ Apply Migrations
python manage.py migrate

5️⃣ Start the Server
python manage.py runserver

The API will be accessible at http://127.0.0.1:8000.
🛠️ API Endpoints
🔹 Authentication
POST /api/token/ → Get a JWT token
POST /api/token/refresh/ → Refresh the token
🔹 Characters
POST /api/create-character/ → Generate a character
GET /api/characters/ → Retrieve all characters
🔹 Comics
POST /api/create-comic/ → Generate a comic
GET /api/comics/ → Retrieve all comics
GET /api/comic/<id>/ → Retrieve a specific comic
📜 API Documentation
The API is documented via Swagger and ReDoc:

📄 Swagger: http://127.0.0.1:8000/swagger/
📘 ReDoc: http://127.0.0.1:8000/redoc/
🤝 Contribution
Fork the repository
Clone the project
Create a new branch: git checkout -b feature-new-functionality
Add your changes and commit: git commit -m "Added new feature"
Push to your repo: git push origin feature-new-functionality
Create a Pull Request 🚀
📜 License
This project is licensed under the MIT License. You are free to use and modify it.

📞 Contact
For any questions, contact me at: contact@example.com



This README covers all essential information about your project in a clear and structured way! 🚀


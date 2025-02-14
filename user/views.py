from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
import jwt
from django.conf import settings
from rest_framework.permissions import AllowAny

# Helper function to generate JWT token
def generate_token(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# class RegisterUserView(APIView):
#     permission_classes = [AllowAny]
#     def post(self, request):
#         data = request.data
#         print(data)
#         try:
#             password = make_password(data['password'])  # Hash password before saving
#             user = User.objects.create(
#                 username=data['username'],
#                 email=data['email'],
#                 password=password,
#             )
#             user.save()
#             return Response({'message': 'User registered successfully!', "isSuccess":"true", "data":user}, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        # Validation des champs requis
        if not data.get('username') or not data.get('password') or not data.get('email'):
            return Response({'error': 'Username, password, and email are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validation du format de l'email
        try:
            validate_email(data['email'])
        except ValidationError:
            return Response({'error': 'Invalid email format.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Créer l'utilisateur
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
            )
            user.save()

            # Renvoyer une réponse avec des champs spécifiques
            return Response({
                'message': 'User registered successfully!',
                "isSuccess": True,
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
            }, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            # Erreur liée à une contrainte d'unicité
            return Response({'error': 'Username or email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Gestion des autres erreurs
            return Response({'error': 'An unexpected error occurred.', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class RegisterUserView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         data = request.data
#         # print(data)

#         # Validation de base
#         if not data.get('username') or not data.get('password') or not data.get('email'):
#             return Response({'error': 'Username, password, and email are required.'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Créer l'utilisateur
#             user = User.objects.create_user(
#                 username=data['username'],
#                 email=data['email'],
#                 password=data['password'],
#             )
#             user.save()
#             print(user)

#             return Response({'message': 'User registered successfully!', "isSuccess": "true", "data": user}, status=status.HTTP_201_CREATED)

#         except IntegrityError as e:
#             print(e)
#             # Erreur liée à une contrainte d'unicité (ex: nom d'utilisateur ou email déjà utilisé)
#             return Response({'error': 'Username or email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             # Autres erreurs
#             print(e)
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class AuthenticateUserView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        print(username)
        print(password)
        
        
        user = authenticate(username=username, password=password)
        if user is not None:
            token = generate_token(user)  # Generate JWT token
            response = Response({
                'userId': user.id,
                'token': token,
                'message': 'Login successful',
                'isSuccess': 'true'
            }, status=status.HTTP_200_OK)
            
            # Set secure cookies
            response.set_cookie(
                key='refresh_token',
                value=token['refresh'],
                httponly=True,
                # secure=True,
                samesite='Lax'
            )
            response.set_cookie(
                key='access_token',
                value=token['access'],
                httponly=True,
                # secure=True,
                samesite='Lax'
            )
            
            return response
        else:
            raise AuthenticationFailed('Invalid credentials')

#check if the user is authenticated by checking the token in the cookie 
class CheckUserView(APIView):
    def get(self, request):
        try:
            refresh_token = request.COOKIES["refresh_token"]
            print(refresh_token)
            token = RefreshToken(refresh_token)
            user = User.objects.get(id=token['user_id'])
            return Response({'message': 'User is authenticated', 'isAuthenticated': 'true', 'user': user.username}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e), 'isAuthenticated': 'false'}, status=status.HTTP_400_BAD_REQUEST)
        
 

# refreshToken

class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Refresh token not found in cookies'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            new_access_token = str(token.access_token)
            # Set secure cookie
            response = Response({'access': new_access_token}, status=status.HTTP_200_OK)
            response.isSucess = True
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RequestResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user = get_object_or_404(User, email=email)
        
        reset_code = get_random_string(length=6, allowed_chars='1234567890')  # Generate 6-digit code
        partial_token = jwt.encode({'user_id': user.id}, settings.SECRET_KEY, algorithm='HS256')  # Partial token

        # Simulate sending email (replace with actual send_mail for production)
        send_mail(
            'Reset Your Password',
            f'Your reset code is {reset_code}. Use it along with this token: {partial_token}.',
            'no-reply@example.com',
            [email],
            fail_silently=False,
        )
        
        user.profile.reset_code = reset_code  # Assuming a user profile for reset codes
        user.profile.save()
        
        return Response({'message': 'Reset code sent to your email'}, status=status.HTTP_200_OK)

class VerifyCodeView(APIView):
    def post(self, request):
        user_id = jwt.decode(request.data.get('partial_token'), settings.SECRET_KEY, algorithms=['HS256'])['user_id']
        user = get_object_or_404(User, id=user_id)
        reset_code = request.data.get('reset_code')
        
        if user.profile.reset_code == reset_code:
            return Response({'message': 'Code verified, you can now reset your password'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid reset code'}, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    def post(self, request):
        user_id = jwt.decode(request.data.get('partial_token'), settings.SECRET_KEY, algorithms=['HS256'])['user_id']
        user = get_object_or_404(User, id=user_id)
        new_password = request.data.get('new_password')
        
        user.password = make_password(new_password)  # Hash new password
        user.save()
        
        return Response({'message': 'Password reset successfully!'}, status=status.HTTP_200_OK)

class GetUserByIdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetAllUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# update users
class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        data = request.data

        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        if 'password' in data:
            user.password = make_password(data['password'])

        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)




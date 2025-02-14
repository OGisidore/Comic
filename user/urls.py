from django.urls import path
from .views import RegisterUserView, AuthenticateUserView,RequestResetPasswordView,VerifyCodeView,ResetPasswordView,GetUserByIdView,GetAllUserView, UpdateUserView, RefreshTokenView, CheckUserView

urlpatterns = [
    path('register-user/', RegisterUserView.as_view(), name='register-user'),
    path('authentication/', AuthenticateUserView.as_view(), name='authentication'),
    path('request-reset-password/', RequestResetPasswordView.as_view(), name='request-reset-password'),
    path('Verify-code/', VerifyCodeView.as_view(), name='Verify-code'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('users/<int:user_id>/', GetUserByIdView.as_view(), name='get-user'),
    path('users/', GetAllUserView.as_view(), name='get-users'),
    path('users/<int:user_id>/', UpdateUserView.as_view(), name='update-user'),
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh-token'),
    path('check-auth/', CheckUserView.as_view(), name='check-auth'),
]
from django.urls import path
from .views import CreateCharacter, CreateComics,GetAllCommics, GetCommic

urlpatterns = [
    path('create-character/', CreateCharacter.as_view(), name='create-character'),
    path('create-comic/', CreateComics.as_view(), name='create-comic'),
    path('get_comics/', GetAllCommics.as_view(), name='get_all_comics'),
    path('get_comic/<str:story_id>/', GetCommic.as_view(), name='get_comic')

]


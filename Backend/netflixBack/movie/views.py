from rest_framework import viewsets
from .models import Movie
from .serializers import MovieSerializer
from django.http import HttpResponse 

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


#Эта функция предназначена для теста. Ее можно удалить
def home(request):
    return HttpResponse("<h1>Welcome to Netflix Clone</h1>")
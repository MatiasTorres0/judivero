from django.shortcuts import render
from .models import Comando, Nota

# Create your views here.
def inicio(request):
    comandos = Comando.objects.all()
    return render(request, 'core/inicio.html', {'comandos': comandos})

def notas_view(request):
    todas_las_notas = Nota.objects.all()
    return render(request, 'core/notas.html', {'notas': todas_las_notas})

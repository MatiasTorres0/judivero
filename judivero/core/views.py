from django.shortcuts import render
from .models import Comando, Nota, Baneos
from .forms import ComandoForm, NotaForm, BaneoForm
from django.shortcuts import redirect

# Create your views here.
def inicio(request):
    comandos = Comando.objects.all()
    Baneos_qs = Baneos.objects.all()
    return render(request, 'core/inicio.html', {'comandos': comandos, 'Baneos': Baneos_qs})

def notas_view(request):
    todas_las_notas = Nota.objects.all()
    return render(request, 'core/notas.html', {'notas': todas_las_notas})

def agregar_nota(request):
    if request.method == 'POST':
        form = NotaForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.user = request.user  # Asignar el usuario actual
            nota.save()
            return redirect('notas_view')
    else:
        form = NotaForm()
    return render(request, 'core/agregar_nota.html', {'form': form})

def agregar_comando(request):
    if request.method == 'POST':
        form = ComandoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inicio')
    else:
        form = ComandoForm()
    return render(request, 'core/agregar_comandos.html', {'form': form})

def agregar_baneo(request):
    if request.method == 'POST':
        form = BaneoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inicio')
    else:
        form = BaneoForm()
    return render(request, 'core/agregar_baneo.html', {'form': form})
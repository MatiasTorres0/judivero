from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Comando, Nota, Baneos, CanalTwitch
from .forms import ComandoForm, NotaForm, BaneoForm

def get_canal_actual(request):
    """Obtiene el canal actual de la sesión o el primero disponible"""
    canal_id = request.session.get('canal_actual_id')
    
    if canal_id:
        try:
            return CanalTwitch.objects.get(id=canal_id, activo=True)
        except CanalTwitch.DoesNotExist:
            pass
    
    # Si no hay canal en sesión o no existe, obtener el primero activo
    canal = CanalTwitch.objects.filter(activo=True).first()
    if canal:
        request.session['canal_actual_id'] = canal.id
    return canal


def cambiar_canal(request, canal_id):
    """Vista para cambiar de canal"""
    canal = get_object_or_404(CanalTwitch, id=canal_id, activo=True)
    request.session['canal_actual_id'] = canal.id
    
    # Obtener la página anterior o redirigir a inicio
    next_url = request.GET.get('next', 'inicio')
    return redirect(next_url)


def inicio(request):
    canal_actual = get_canal_actual(request)
    canales = CanalTwitch.objects.filter(activo=True)
    
    if not canal_actual:
        # No hay canales, mostrar mensaje o redirigir a crear uno
        return render(request, 'core/sin_canales.html', {'canales': canales})
    
    comandos = Comando.objects.filter(canal=canal_actual)
    baneos = Baneos.objects.filter(canal=canal_actual)
    
    context = {
        'comandos': comandos,
        'baneos': baneos,
        'canal_actual': canal_actual,
        'canales': canales,
    }
    return render(request, 'core/inicio.html', context)


def notas_view(request):
    canal_actual = get_canal_actual(request)
    canales = CanalTwitch.objects.filter(activo=True)
    
    if not canal_actual:
        return render(request, 'core/sin_canales.html', {'canales': canales})
    
    todas_las_notas = Nota.objects.filter(canal=canal_actual)
    
    context = {
        'notas': todas_las_notas,
        'canal_actual': canal_actual,
        'canales': canales,
    }
    return render(request, 'core/notas.html', context)


def agregar_nota(request):
    canal_actual = get_canal_actual(request)
    
    if not canal_actual:
        return redirect('inicio')
    
    if request.method == 'POST':
        form = NotaForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.canal = canal_actual
            if request.user.is_authenticated:
                nota.user = request.user
            nota.save()
            return redirect('notas')
    else:
        form = NotaForm()
    
    return render(request, 'core/agregar_nota.html', {
        'form': form,
        'canal_actual': canal_actual
    })


def agregar_comando(request):
    canal_actual = get_canal_actual(request)
    
    if not canal_actual:
        return redirect('inicio')
    
    if request.method == 'POST':
        form = ComandoForm(request.POST)
        if form.is_valid():
            comando = form.save(commit=False)
            comando.canal = canal_actual
            comando.save()
            return redirect('inicio')
    else:
        form = ComandoForm()
    
    return render(request, 'core/agregar_comandos.html', {
        'form': form,
        'canal_actual': canal_actual
    })


def agregar_baneo(request):
    canal_actual = get_canal_actual(request)
    
    if not canal_actual:
        return redirect('inicio')
    
    if request.method == 'POST':
        form = BaneoForm(request.POST)
        if form.is_valid():
            baneo = form.save(commit=False)
            baneo.canal = canal_actual
            if request.user.is_authenticated:
                baneo.user = request.user
            baneo.save()
            return redirect('inicio')
    else:
        form = BaneoForm()
    
    return render(request, 'core/agregar_baneo.html', {
        'form': form,
        'canal_actual': canal_actual
    })
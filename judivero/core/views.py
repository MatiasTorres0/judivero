from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
import tempfile
import os
from .models import Comando, Nota, Baneos, CanalTwitch
from .forms import ComandoForm, NotaForm, BaneoForm, CustomLoginForm
from django.template.loader import render_to_string
from django.http import HttpResponse
from io import BytesIO
from xhtml2pdf import pisa
import os

@login_required
def get_canal_actual(request):
    """Obtiene el canal actual de la sesión o el primero disponible"""
    canal_id = request.session.get('canal_actual_id')
    
    if canal_id:
        try:
            return CanalTwitch.objects.get(id=canal_id, activo=True)
        except CanalTwitch.DoesNotExist:
            pass
    
    canal = CanalTwitch.objects.filter(activo=True).first()
    if canal:
        request.session['canal_actual_id'] = canal.id
    return canal

@login_required
def cambiar_canal(request, canal_id):
    """Vista para cambiar de canal"""
    canal = get_object_or_404(CanalTwitch, id=canal_id, activo=True)
    request.session['canal_actual_id'] = canal.id
    next_url = request.GET.get('next', 'inicio')
    return redirect(next_url)

@login_required
def inicio(request):
    canal_actual = get_canal_actual(request)
    canales = CanalTwitch.objects.filter(activo=True)
    
    if not canal_actual:
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

@login_required
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

@login_required
def agregar_nota(request):
    canal_actual = get_canal_actual(request)
    canales = CanalTwitch.objects.filter(activo=True)
    
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
        'canal_actual': canal_actual,
        'canales': canales,
    })

@login_required
def agregar_comando(request):
    canal_actual = get_canal_actual(request)
    canales = CanalTwitch.objects.filter(activo=True)
    
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
        'canal_actual': canal_actual,
        'canales': canales,
    })

@login_required
def agregar_baneo(request):
    canal_actual = get_canal_actual(request)
    canales = CanalTwitch.objects.filter(activo=True)
    
    if not canal_actual:
        return redirect('inicio')
    
    if request.method == 'POST':
        form = BaneoForm(request.POST, request.FILES)
        
        if form.is_valid():
            baneo = form.save(commit=False)
            baneo.canal = canal_actual
            
            if request.user.is_authenticated:
                baneo.user = request.user
            
            baneo.save()
            return redirect('inicio')
        else:
            print(f"Errores del formulario: {form.errors}")
    else:
        form = BaneoForm()
    
    return render(request, 'core/agregar_baneo.html', {
        'form': form,
        'canal_actual': canal_actual,
        'canales': canales,
    })

@login_required
def perfil_usuario(request, nombre_usuario):
    """Vista del perfil completo de un usuario con su historial"""
    canal_actual = get_canal_actual(request)
    canales = CanalTwitch.objects.filter(activo=True)
    
    if not canal_actual:
        return redirect('inicio')
    
    baneos = Baneos.objects.filter(
        canal=canal_actual,
        nombre_usuario=nombre_usuario
    ).order_by('-fecha_baneo')
    
    total_baneos = baneos.count()
    baneos_activos = baneos.filter(activo=True).count()
    
    context = {
        'nombre_usuario': nombre_usuario,
        'baneos': baneos,
        'total_baneos': total_baneos,
        'baneos_activos': baneos_activos,
        'canal_actual': canal_actual,
        'canales': canales,
    }
    
    return render(request, 'core/perfil_usuario.html', context)

@login_required
def generar_reporte_pdf(request, nombre_usuario):
    """Genera un PDF usando xhtml2pdf (compatible con Windows)"""
    canal_actual = get_canal_actual(request)
    
    if not canal_actual:
        return HttpResponse('No hay canal seleccionado', status=400)
    
    baneos = Baneos.objects.filter(
        canal=canal_actual,
        nombre_usuario=nombre_usuario
    ).order_by('-fecha_baneo')
    
    if not baneos.exists():
        return HttpResponse('No se encontraron registros para este usuario', status=404)
    
    total_baneos = baneos.count()
    baneos_activos = baneos.filter(activo=True).count()
    es_reincidente = total_baneos > 1

    # Renderizar el template HTML
    html_string = render_to_string('core/pdf/reporte_baneo.html', {
        'nombre_usuario': nombre_usuario,
        'canal': canal_actual,
        'fecha_reporte': timezone.now(),
        'baneos': baneos,
        'total_baneos': total_baneos,
        'baneos_activos': baneos_activos,
        'es_reincidente': es_reincidente,
    })

    # Crear PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_{nombre_usuario}_{canal_actual.nombre}_{timezone.now().strftime("%Y%m%d_%H%M")}.pdf"'
        return response
    
    return HttpResponse('Error al generar el PDF: %s' % pdf.err, status=500)

@login_required
def buscar_usuario(request):
    """Vista para buscar un usuario en todos los canales"""
    canal_actual = get_canal_actual(request)
    canales = CanalTwitch.objects.filter(activo=True)
    
    username = request.GET.get('q', '').strip()
    resultados = []
    
    if username:
        baneos = Baneos.objects.filter(
            canal=canal_actual,
            nombre_usuario__icontains=username
        ).order_by('-fecha_baneo')
        
        usuarios = {}
        for baneo in baneos:
            if baneo.nombre_usuario not in usuarios:
                usuarios[baneo.nombre_usuario] = {
                    'nombre': baneo.nombre_usuario,
                    'total_baneos': 0,
                    'baneos_activos': 0,
                    'ultimo_baneo': None
                }
            
            usuarios[baneo.nombre_usuario]['total_baneos'] += 1
            if baneo.activo:
                usuarios[baneo.nombre_usuario]['baneos_activos'] += 1
            
            if not usuarios[baneo.nombre_usuario]['ultimo_baneo']:
                usuarios[baneo.nombre_usuario]['ultimo_baneo'] = baneo
        
        resultados = list(usuarios.values())
    
    context = {
        'username': username,
        'resultados': resultados,
        'canal_actual': canal_actual,
        'canales': canales,
    }
    
    return render(request, 'core/buscar_usuario.html', context)

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('inicio')
    else:
        form = CustomLoginForm()
    
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')
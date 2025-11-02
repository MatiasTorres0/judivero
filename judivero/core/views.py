from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Q
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime

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
    
    canal = CanalTwitch.objects.filter(activo=True).first()
    if canal:
        request.session['canal_actual_id'] = canal.id
    return canal


def cambiar_canal(request, canal_id):
    """Vista para cambiar de canal"""
    canal = get_object_or_404(CanalTwitch, id=canal_id, activo=True)
    request.session['canal_actual_id'] = canal.id
    next_url = request.GET.get('next', 'inicio')
    return redirect(next_url)


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
            
            # Verificar si es reincidente
            baneos_previos = Baneos.objects.filter(
                canal=canal_actual,
                nombre_usuario=baneo.nombre_usuario
            ).exclude(id=baneo.id if baneo.id else None)
            
            if baneos_previos.exists():
                baneo.es_reincidente = True
                baneo.numero_infracciones = baneos_previos.count() + 1
            
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


# ==================== NUEVAS VISTAS PARA REPORTES ====================

def perfil_usuario(request, nombre_usuario):
    """Vista del perfil completo de un usuario con su historial"""
    canal_actual = get_canal_actual(request)
    canales = CanalTwitch.objects.filter(activo=True)
    
    if not canal_actual:
        return redirect('inicio')
    
    # Obtener todos los baneos del usuario en este canal
    baneos = Baneos.objects.filter(
        canal=canal_actual,
        nombre_usuario=nombre_usuario
    ).order_by('-fecha_baneo')
    
    # Estadísticas
    total_baneos = baneos.count()
    baneos_activos = baneos.filter(activo=True).count()
    
    # Baneos por tipo
    por_tipo = baneos.values('tipo_baneo').annotate(total=Count('id'))
    
    # Baneos por severidad
    por_severidad = baneos.values('severidad').annotate(total=Count('id'))
    
    context = {
        'nombre_usuario': nombre_usuario,
        'baneos': baneos,
        'total_baneos': total_baneos,
        'baneos_activos': baneos_activos,
        'por_tipo': por_tipo,
        'por_severidad': por_severidad,
        'canal_actual': canal_actual,
        'canales': canales,
    }
    
    return render(request, 'core/perfil_usuario.html', context)


def generar_reporte_pdf(request, nombre_usuario):
    """Genera un PDF con el historial completo de baneos de un usuario"""
    canal_actual = get_canal_actual(request)
    
    if not canal_actual:
        return HttpResponse('No hay canal seleccionado', status=400)
    
    # Obtener todos los baneos del usuario
    baneos = Baneos.objects.filter(
        canal=canal_actual,
        nombre_usuario=nombre_usuario
    ).order_by('-fecha_baneo')
    
    if not baneos.exists():
        return HttpResponse('No se encontraron registros para este usuario', status=404)
    
    # Crear el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    # Contenedor para los elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, fontSize=10))
    
    # Título principal
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#764ba2'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph(f"Reporte de Moderación", title_style))
    elements.append(Paragraph(f"Canal: {canal_actual.nombre}", styles['Center']))
    elements.append(Spacer(1, 12))
    
    # Información del usuario
    user_info_style = ParagraphStyle(
        'UserInfo',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=12
    )
    
    elements.append(Paragraph(f"Usuario: {nombre_usuario}", user_info_style))
    elements.append(Paragraph(f"Fecha del reporte: {timezone.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Resumen estadístico
    total_baneos = baneos.count()
    baneos_activos = baneos.filter(activo=True).count()
    
    elements.append(Paragraph("Resumen de Infracciones", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    resumen_data = [
        ['Métrica', 'Cantidad'],
        ['Total de Infracciones', str(total_baneos)],
        ['Sanciones Activas', str(baneos_activos)],
        ['Sanciones Completadas', str(total_baneos - baneos_activos)],
        ['Estado', 'REINCIDENTE' if total_baneos > 1 else 'Primera infracción'],
    ]
    
    resumen_table = Table(resumen_data, colWidths=[3*inch, 2*inch])
    resumen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))
    
    elements.append(resumen_table)
    elements.append(Spacer(1, 30))
    
    # Historial detallado
    elements.append(Paragraph("Historial Detallado de Sanciones", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    for idx, baneo in enumerate(baneos, 1):
        # Sección para cada baneo
        baneo_title = Paragraph(
            f"<b>Infracción #{idx}</b> - {baneo.get_tipo_baneo_display()} "
            f"({'⚠️ ACTIVO' if baneo.activo else '✓ Completado'})",
            styles['Heading3']
        )
        elements.append(baneo_title)
        elements.append(Spacer(1, 8))
        
        # Detalles del baneo en tabla
        baneo_data = [
            ['Fecha', baneo.fecha_baneo.strftime('%d/%m/%Y %H:%M')],
            ['Tipo de Sanción', baneo.get_tipo_baneo_display()],
            ['Severidad', baneo.get_severidad_display()],
            ['Estado', 'ACTIVO' if baneo.activo else 'Completado'],
        ]
        
        if baneo.desbaneo:
            baneo_data.append(['Fecha de Desbaneo', baneo.desbaneo.strftime('%d/%m/%Y %H:%M')])
        
        if baneo.user:
            baneo_data.append(['Moderador', str(baneo.user.username)])
        
        baneo_table = Table(baneo_data, colWidths=[2*inch, 3.5*inch])
        baneo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(baneo_table)
        elements.append(Spacer(1, 8))
        
        # Motivo del baneo
        elements.append(Paragraph("<b>Motivo:</b>", styles['Normal']))
        motivo_text = Paragraph(baneo.motivo, styles['Justify'])
        elements.append(motivo_text)
        
        # Notas adicionales si existen
        if baneo.notas_adicionales:
            elements.append(Spacer(1, 8))
            elements.append(Paragraph("<b>Notas Adicionales:</b>", styles['Normal']))
            notas_text = Paragraph(baneo.notas_adicionales, styles['Justify'])
            elements.append(notas_text)
        
        elements.append(Spacer(1, 20))
        
        # Añadir página nueva cada 2 baneos (excepto el último)
        if idx % 2 == 0 and idx < len(baneos):
            elements.append(PageBreak())
    
    # Pie de página con información
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(
        f"Reporte generado por Sistema de Moderación Judivero - {canal_actual.nombre}",
        footer_style
    ))
    elements.append(Paragraph(
        f"Este documento contiene información confidencial de moderación",
        footer_style
    ))
    
    # Construir el PDF
    doc.build(elements)
    
    # Obtener el valor del buffer y crear la respuesta
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{nombre_usuario}_{canal_actual.nombre}_{timezone.now().strftime("%Y%m%d")}.pdf"'
    response.write(pdf)
    
    return response


def buscar_usuario(request):
    """Vista para buscar un usuario en todos los canales"""
    canal_actual = get_canal_actual(request)
    canales = CanalTwitch.objects.filter(activo=True)
    
    username = request.GET.get('q', '').strip()
    resultados = []
    
    if username:
        # Buscar en el canal actual
        baneos = Baneos.objects.filter(
            canal=canal_actual,
            nombre_usuario__icontains=username
        ).order_by('-fecha_baneo')
        
        # Agrupar por usuario
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
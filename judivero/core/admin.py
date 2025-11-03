from django.contrib import admin
from django import forms
from .models import Comando, Nota, Baneos, CanalTwitch

# Form personalizado para Baneos en el admin
class BaneosAdminForm(forms.ModelForm):
    class Meta:
        model = Baneos
        fields = '__all__'
        widgets = {
            'desbaneo': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar el formato del campo desbaneo si tiene valor
        if self.instance and self.instance.desbaneo:
            self.initial['desbaneo'] = self.instance.desbaneo.strftime('%Y-%m-%dT%H:%M')

@admin.register(CanalTwitch)
class CanalTwitchAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'streamer', 'activo', 'fecha_inicio_moderacion', 'total_comandos', 'total_baneos_activos']
    list_filter = ['activo', 'fecha_inicio_moderacion']
    search_fields = ['nombre', 'streamer', 'descripcion']
    ordering = ['nombre']
    readonly_fields = ['total_comandos', 'total_baneos_activos', 'fecha_inicio_moderacion']
    
    fieldsets = (
        ('Información del Canal', {
            'fields': ('nombre', 'streamer', 'descripcion', 'url_twitch')
        }),
        ('Configuración', {
            'fields': ('color_distintivo', 'activo')
        }),
        ('Estadísticas', {
            'fields': ('total_comandos', 'total_baneos_activos', 'fecha_inicio_moderacion'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Comando)
class ComandoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'canal', 'juego_o_significado', 'nivel_minimo', 'activo', 'fecha_creacion']
    list_filter = ['canal', 'nivel_minimo', 'activo', 'fecha_creacion']
    search_fields = ['nombre', 'juego_o_significado']
    ordering = ['canal', 'nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('canal', 'nombre', 'juego_o_significado')
        }),
        ('Configuración', {
            'fields': ('nivel_minimo', 'activo')
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'ultima_modificacion'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['fecha_creacion', 'ultima_modificacion']

@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'canal', 'tipo', 'importante', 'etiqueta', 'fecha_creacion']
    list_filter = ['canal', 'tipo', 'importante', 'fecha_creacion']
    search_fields = ['titulo', 'nota', 'etiqueta']
    ordering = ['-fecha_creacion']
    
    fieldsets = (
        ('Canal y Tipo', {
            'fields': ('canal', 'tipo', 'importante')
        }),
        ('Contenido', {
            'fields': ('titulo', 'nota', 'etiqueta')
        }),
        ('Información', {
            'fields': ('user', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']

@admin.register(Baneos)
class BaneosAdmin(admin.ModelAdmin):
    form = BaneosAdminForm  # Usar el formulario personalizado
    list_display = ['nombre_usuario', 'canal', 'activo', 'fecha_baneo', 'desbaneo']
    list_filter = ['canal', 'activo', 'fecha_baneo']
    search_fields = ['nombre_usuario', 'motivo']
    ordering = ['-fecha_baneo']
    
    fieldsets = (
        ('Usuario y Canal', {
            'fields': ('canal', 'nombre_usuario', 'user')
        }),
        ('Detalles del Baneo', {
            'fields': ('motivo', 'activo')
        }),
        ('Fechas', {
            'fields': ('fecha_baneo', 'desbaneo'),
            'description': 'La fecha de baneo se registra automáticamente. El desbaneo es opcional.'
        }),
    )
    readonly_fields = ['fecha_baneo']
    
    actions = ['desactivar_baneos', 'activar_baneos']
    
    def desactivar_baneos(self, request, queryset):
        queryset.update(activo=False)
        self.message_user(request, f'{queryset.count()} baneo(s) desactivado(s).')
    desactivar_baneos.short_description = "Desactivar baneos seleccionados"
    
    def activar_baneos(self, request, queryset):
        queryset.update(activo=True)
        self.message_user(request, f'{queryset.count()} baneo(s) activado(s).')
    activar_baneos.short_description = "Activar baneos seleccionados"
from django.contrib import admin
from .models import Comando, Nota, Baneos, CanalTwitch

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
    list_display = ['nombre_usuario', 'canal', 'activo', 'fecha_baneo']
    list_filter = ['canal', 'activo', 'fecha_baneo']
    search_fields = ['nombre_usuario', 'motivo']
    ordering = ['-fecha_baneo']
    
    fieldsets = (
        ('Usuario y Canal', {
            'fields': ('canal', 'nombre_usuario', 'user')
        }),
        ('Detalles', {
            'fields': ('motivo', 'activo', 'fecha_baneo', 'desbaneo')
        }),
    )
    readonly_fields = ['fecha_baneo']
    
    actions = ['desactivar_baneos']
    
    def desactivar_baneos(self, request, queryset):
        queryset.update(activo=False)
        self.message_user(request, f'{queryset.count()} baneo(s) desactivado(s).')
    desactivar_baneos.short_description = "Desactivar baneos seleccionados"
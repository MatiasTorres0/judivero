from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import FileExtensionValidator
# Modelo para Canales de Twitch donde eres moderador
class CanalTwitch(models.Model):
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre del canal de Twitch")
    streamer = models.CharField(max_length=100, help_text="Nombre del streamer/dueño del canal")
    descripcion = models.TextField(blank=True, null=True, help_text="Notas sobre el canal o reglas especiales")
    url_twitch = models.URLField(blank=True, null=True)
    color_distintivo = models.CharField(max_length=7, default="#9147ff", help_text="Color hex para identificar el canal")
    activo = models.BooleanField(default=True, help_text="¿Sigues siendo mod en este canal?")
    fecha_inicio_moderacion = models.DateTimeField(auto_now_add=True)
    
    # Estadísticas de moderación
    total_comandos = models.IntegerField(default=0, editable=False)
    total_baneos_activos = models.IntegerField(default=0, editable=False)
    
    class Meta:
        verbose_name = 'Canal de Twitch (Moderación)'
        verbose_name_plural = 'Canales de Twitch (Moderación)'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} (@{self.streamer})"
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas del canal"""
        self.total_comandos = self.comandos.count()
        self.total_baneos_activos = self.baneos.filter(activo=True).count()
        self.save(update_fields=['total_comandos', 'total_baneos_activos'])


class Comando(models.Model):
    NIVEL = [
        ('EVERYONE', 'Everyone'),
        ('VIPS', 'Vips'),
        ('MODS', 'Mods'),
        ('SUPERMODS', 'SuperMods'),
        ('STREAMER', 'Streamer'),
    ]
    canal = models.ForeignKey(
        CanalTwitch,
        on_delete=models.CASCADE,
        related_name='comandos',
        null=True,
        help_text="Canal donde aplica este comando"
    )
    nombre = models.CharField(max_length=200, help_text="Ej: !hola, !reglas, !discord")
    juego_o_significado = models.CharField(max_length=200, help_text="Descripción o respuesta del comando")
    nivel_minimo = models.CharField(max_length=200, choices=NIVEL, default='EVERYONE')
    activo = models.BooleanField(default=True, help_text="¿El comando está activo en el canal?")
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        # Evitar comandos duplicados en el mismo canal
        unique_together = ['canal', 'nombre']
        ordering = ['nombre']

    def __str__(self):
        canal_nombre = self.canal.nombre if self.canal else "Sin canal"
        return f"[{canal_nombre}] {self.nombre} - {self.nivel_minimo}"


class Nota(models.Model):
    TIPO_NOTA = [
        ('GENERAL', 'General'),
        ('REGLA', 'Regla del Canal'),
        ('INCIDENTE', 'Incidente'),
        ('RECORDATORIO', 'Recordatorio'),
        ('VIEWER', 'Info de Viewer'),
    ]
    
    canal = models.ForeignKey(
        CanalTwitch,
        on_delete=models.CASCADE,
        related_name='notas',
        null=True,
        help_text="Canal al que pertenece esta nota"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notas_usuario',
        null=True
    )
    tipo = models.CharField(max_length=20, choices=TIPO_NOTA, default='GENERAL')
    titulo = models.CharField(max_length=200, blank=True)
    nota = models.TextField(help_text="Detalles de la nota, incidente, regla, etc.")
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    etiqueta = models.CharField(max_length=50, blank=True, help_text="Ej: troll, spam, viewer-vip")
    importante = models.BooleanField(default=False, help_text="Marcar para referencia rápida")

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Nota de Moderación'
        verbose_name_plural = 'Notas de Moderación'

    def __str__(self):
        canal_nombre = self.canal.nombre if self.canal else "Sin canal"
        return f"[{canal_nombre}] {self.get_tipo_display()}: {self.titulo or self.nota[:50]}"


class Baneos(models.Model):
    canal = models.ForeignKey(
        CanalTwitch,
        on_delete=models.CASCADE,
        related_name='baneos',
        null=True  # Para migración, luego quitar
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='baneos_usuario',
        null=True
    )
    nombre_usuario = models.CharField(max_length=200)
    fecha_baneo = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField()
    desbaneo = models.DateTimeField(null=True, blank=True)    
    activo = models.BooleanField(default=True)
    # Por esta:
    imagen = models.ImageField(
        upload_to='baneos/imagenes/',
        validators=[FileExtensionValidator(['svg', 'png', 'jpg', 'jpeg'])],
        blank=True,
        null=True,
        help_text="Imagen relacionada con el baneo"
    )
    class Meta:
        verbose_name = 'Baneo'
        verbose_name_plural = 'Baneos'
        ordering = ['-fecha_baneo']

    def esta_baneado(self):
        if self.desbaneo and self.desbaneo <= timezone.now():
            self.activo = False
            self.save(update_fields=['activo'])
            return False
        return self.activo

    def desbanear(self):
        self.desbaneo = timezone.now()
        self.activo = False
        self.save(update_fields=['desbaneo', 'activo'])

    def __str__(self):
        canal_nombre = self.canal.nombre if self.canal else "Sin canal"
        estado = "Activo" if self.activo else "Inactivo"
        return f"[{canal_nombre}] {self.nombre_usuario} - {estado} ({self.fecha_baneo.strftime('%d/%m/%Y')})"

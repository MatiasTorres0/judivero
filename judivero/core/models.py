from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

# Create your models here.
class Comando(models.Model):
    NIVEL = [
        ('EVERYONE', 'Everyone'),
        ('VIPS', 'Vips'),
        ('MODS', 'Mods'),
        ('SUPERMODS', 'SuperMods'),
        ('STREAMER', 'Streamer'),
    ]
    nombre = models.CharField(max_length=200)
    juego_o_significado = models.CharField(max_length=200)
    nivel_minimo = models.CharField(max_length=200, choices=NIVEL, default='EVERYONE')

    def __str__(self):
        return f"{self.nombre} - {self.juego_o_significado} - {self.nivel_minimo}"

class Nota(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notas_usuario',
        null=True
    )
    titulo = models.CharField(max_length=200, blank=True)
    nota = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    etiqueta = models.CharField(max_length=50, blank=True)
    importante = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'

    def save(self, *args, **kwargs):
        if not self.pk and not self.user_id:
            # Si estamos en un contexto con request, podemos obtener el usuario actual
            # Esto debe manejarse en la vista, no aquí
            pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.titulo or 'Sin título'} - {self.nota[:50]}{'...' if len(self.nota) > 50 else ''} ({self.fecha_creacion.strftime('%d/%m/%Y')})"


class Baneos(models.Model):
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

    def esta_baneado(self):
        # Si hay fecha de desbaneo y ya pasó, el baneo está inactivo
        if self.desbaneo and self.desbaneo <= timezone.now():
            self.activo = False
            self.save(update_fields=['activo'])
            return False
        return self.activo

    def desbanear(self):
        self.desbaneo = timezone.now()
        self.activo = False
        self.save(update_fields=['desbaneo', 'activo'])


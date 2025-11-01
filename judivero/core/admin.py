from django.contrib import admin

# Register your models here.
from .models import Comando, Nota

admin.site.register(Comando)
admin.site.register(Nota)
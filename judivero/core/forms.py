from django import forms
from .models import Nota, Comando, Baneos


class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['titulo', 'nota', 'etiqueta', 'importante']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la nota'
            }),
            'nota': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Escribe el contenido aquí...'
            }),
            'etiqueta': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Etiqueta (opcional)'
            }),
            'importante': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'titulo': 'Título',
            'nota': 'Contenido',
            'etiqueta': 'Etiqueta',
            'importante': 'Marcar como importante'
        }


class ComandoForm(forms.ModelForm):
    class Meta:
        model = Comando
        fields = ['nombre', 'juego_o_significado', 'nivel_minimo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del comando (ej: !hola)'
            }),
            'juego_o_significado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Juego o descripción del comando'
            }),
            'nivel_minimo': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'nombre': 'Nombre del Comando',
            'juego_o_significado': 'Juego o Significado',
            'nivel_minimo': 'Nivel Mínimo Requerido'
        }


class BaneoForm(forms.ModelForm):
    class Meta:
        model = Baneos
        fields = ['nombre_usuario', 'motivo', 'desbaneo']
        widgets = {
            'nombre_usuario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }),
            'motivo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe el motivo del baneo...'
            }),
            'desbaneo': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),
        }
        labels = {
            'nombre_usuario': 'Nombre de usuario',
            'motivo': 'Motivo del baneo',
            'desbaneo': 'Fecha de desbaneo',
        }
        help_texts = {
            'desbaneo': 'Deja en blanco si el baneo es permanente.',
        }
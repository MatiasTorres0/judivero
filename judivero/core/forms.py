from django import forms
from .models import Nota, Comando, Baneos


class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['titulo', 'nota', 'etiqueta', 'importante']
        exclude = ['user', 'fecha_creacion', 'fecha_actualizacion']
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


class ComandoForm(forms.ModelForm):
    class Meta:
        model = Comando
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del comando'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe qué hace este comando...'
            }),
            'codigo': forms.Textarea(attrs={
                'class': 'form-control font-monospace',
                'rows': 6,
                'placeholder': 'Pega aquí el código del comando...'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_creacion': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),
            'autor': forms.Select(attrs={
                'class': 'form-select'
            })
        }

class BaneoForm(forms.ModelForm):
    class Meta:
        model = Baneos
        fields = '__all__'
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
            'motivo': 'Motivo',
            'desbaneo': 'Fecha de desbaneo',
        }
        help_texts = {
            'desbaneo': 'Deja en blanco si el baneo es permanente.',
        }
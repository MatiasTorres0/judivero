from django import forms
from .models import Nota, Comando


class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = '__all__'
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la nota'
            }),
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Escribe el contenido aquí...'
            }),
            'fecha_creacion': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),
            'autor': forms.Select(attrs={
                'class': 'form-select'
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

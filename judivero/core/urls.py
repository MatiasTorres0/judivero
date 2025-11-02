from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('notas/', views.notas_view, name='notas'),
    path('agregar_nota/', views.agregar_nota, name='agregar_nota'),
    path('agregar_comando/', views.agregar_comando, name='agregar_comando'),
    path('agregar_baneo/', views.agregar_baneo, name='agregar_baneo'),
    path('cambiar_canal/<int:canal_id>/', views.cambiar_canal, name='cambiar_canal'),
]
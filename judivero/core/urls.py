from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('notas/', views.notas_view, name='notas'),
    path('agregar_nota/', views.agregar_nota, name='agregar_nota'),
    path('agregar_comando/', views.agregar_comando, name='agregar_comando'),
    path('agregar_baneo/', views.agregar_baneo, name='agregar_baneo'),
    path('cambiar_canal/<int:canal_id>/', views.cambiar_canal, name='cambiar_canal'),
    path('buscar/', views.buscar_usuario, name='buscar_usuario'),
    path('perfil/<str:nombre_usuario>/', views.perfil_usuario, name='perfil_usuario'),
    path('reporte/<str:nombre_usuario>/', views.generar_reporte_pdf, name='generar_reporte_pdf'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
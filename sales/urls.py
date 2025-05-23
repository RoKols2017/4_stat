from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('export/', views.export_report, name='export_report'),
] 
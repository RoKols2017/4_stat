from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('export/', views.export_report, name='export_report'),
    path('top-products/', views.top_products, name='top_products'),
    path('top-regions/', views.top_regions, name='top_regions'),
    path('avg-receipt/', views.avg_receipt, name='avg_receipt'),
    path('monthly-dynamics/', views.monthly_dynamics, name='monthly_dynamics'),
    path('pie-products/', views.pie_products, name='pie_products'),
    path('pie-regions/', views.pie_regions, name='pie_regions'),
] 
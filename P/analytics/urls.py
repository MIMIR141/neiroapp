from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_dashboard, name='analytics_dashboard'),
    path('export/csv/', views.analytics_export_csv, name='analytics_export_csv'),
] 
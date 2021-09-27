from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('rcsb/', views.RCSB.as_view(), name='rcsb'),
    path('project/<str:pk>/', views.Detail.as_view(), name='project-detail'),
    path('project/<str:pk>/delete/', views.Delete.as_view(), name='project-delete'),
    path('project/<str:pk>/status/', views.project_status, name='project-status'),
    path('options/', views.update_options, name='update-options'),
    path('options/reset/', views.reset_options, name='reset-options'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
]

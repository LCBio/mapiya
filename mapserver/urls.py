from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('help/', views.HelpView.as_view(), name='help'),
    path('rcsb/', views.RCSB.as_view(), name='rcsb'),
    path('project/<str:pk>/', views.Detail.as_view(), name='project-detail'),
    path('project/<str:pk>/delete/', views.Delete.as_view(), name='project-delete'),
    path('project/<str:pk>/status/', views.project_status, name='project-status'),
    path('project/<str:pk>/molstar/', views.molstar, name='project-molstar'),
    path('options/', views.update_options, name='update-options'),
    path('options/reset/', views.reset_options, name='reset-options'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
]

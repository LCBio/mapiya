from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('help/', views.HelpView.as_view(), name='help'),
    path('rcsb/', views.RCSB.as_view(), name='rcsb'),
    path('project/<str:pk>/', views.Detail.as_view(), name='project-detail'),
    path('p/<str:pk>/', views.PlotlyProject.as_view(), name='plotly-project'),
    path('project/<str:pk>/delete/', views.Delete.as_view(), name='project-delete'),
    path('project/<str:pk>/resubmit/', views.resubmit, name='project-resubmit'),
    path('project/<str:pk>/status/', views.project_status, name='project-status'),
    path('project/<str:pk>/molstar/', views.molstar, name='project-molstar'),
    path('project/<str:pk>/molstar/<int:model_index>/', views.molstar_model, name='project-molstar-model'),
    path('project/<str:pk>/pqr/<int:model_index>/', views.get_pqr, name='get-pqr'),
    path('project/<str:pk>/data/', views.project_data, name='project-data'),
    path('project/<str:pk>/data/<int:model_index>', views.project_data_model, name='project-data-model'),
    path('options/', views.update_options, name='update-options'),
    path('options/reset/', views.reset_options, name='reset-options'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
]

from django.urls import path, include
from . import views
from . import plotly_apps


urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('rcsb/', views.RCSB.as_view(), name='rcsb'),
    path('map/<str:pk>/', views.Detail.as_view(), name='map-detail'),
    path('map/<str:pk>/delete/', views.Delete.as_view(), name='map-delete'),
    path('map/<str:pk>/status/', views.map_status, name='map-status'),
    path('options/', views.update_options, name='update-options'),
    path('options/reset/', views.reset_options, name='reset-options'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
]

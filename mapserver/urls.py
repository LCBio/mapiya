from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from . import views
from . import plotly_apps

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('signup/', views.Signup.as_view(), name='signup'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('reset/', views.PasswordReset.as_view(), name='password-reset'),
    path('rcsb/', views.RCSB.as_view(), name='rcsb'),
    path('map/<str:pk>/', views.Detail.as_view(), name='map-detail'),
    path('map/<str:pk>/data/', views.map_data, name='map-data'),
    path('map/<str:pk>/delete/', views.Delete.as_view(), name='map-delete'),
    path('ngl/<str:pk>/add/', views.NGLAddRep.as_view(), name='ngl-add'),
    path('ngl/<int:pk>/delete/', views.NGLDelRep.as_view(), name='ngl-delete'),
    path('ngl/<int:pk>/update/', views.NGLUpdateRep.as_view(), name='ngl-update'),
    path('ngl/<int:pk>/options/', views.NGLOptions.as_view(), name='ngl-options'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

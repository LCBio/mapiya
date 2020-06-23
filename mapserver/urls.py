from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('reset/', views.PasswordReset.as_view(), name='password-reset'),
    path('map/<str:pk>/', views.MapDetail.as_view(), name='map-detail'),
    path('map/<str:pk>/data/', views.map_data, name='map-data'),
    path('map/<str:pk>/delete/', views.MapDelete.as_view(), name='map-delete')
]

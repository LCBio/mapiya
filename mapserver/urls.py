from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^.*\.html', views.gentella_html, name='gentella'),
    path('', views.home_view, name='home'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('map/<str:pk>/', views.MapDetail.as_view(), name='map-detail')
]

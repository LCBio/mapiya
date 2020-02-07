from django.urls import path, re_path
from mapserver import views

urlpatterns = [

    # Matches any html file - to be used for gentella
    # Avoid using your .html in your resources.
    # Or create a separate django app.
    re_path(r'^.*\.html', views.gentella_html, name='gentella'),

    # The home page
    path('', views.Home.as_view(), name='home'),

    # /upload/1/
    path('upload/<int:pk>/', views.UploadDetail.as_view(), name='upload-detail'),

]

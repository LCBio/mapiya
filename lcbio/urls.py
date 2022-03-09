from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from mapserver import plotly2

urlpatterns = [
    path('', include('mapserver.urls')),
    path('rq/', include('django_rq.urls')),
    path('users/', include('users.urls')),
    path('admin/', admin.site.urls),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

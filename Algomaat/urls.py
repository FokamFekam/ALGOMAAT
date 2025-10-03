"""
URL configuration for meetasa project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from .views import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage),
    path('about/', views.about),
    path('bucket/', include('bucket.urls')),
    path('registration/', include('registration.urls')),
    path('spaces/', include('contents.urls.spaces')),
    path('publications/', include('contents.urls.publications')),
    path('relations/', include('contents.urls.relations')),
    path("d/", DashboardView.as_view(), name="dashboard"),
    path("", include("calendarapp.urls")),
    path('material/', include('material.urls')),
    path('lessonapp/', include('lessonapp.urls')),
    path('chat/', include('chat.urls')),
    path('accounts/', include('allauth.urls')),
    path('paiement/', include('paiement.urls')),
    path("calendarapp/", include("calendarapp.urls")),
    ]
    

from django.conf.urls.static import static
from django.conf import settings
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


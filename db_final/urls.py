from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

import app.views

urlpatterns = [
    path('admin/', include('admin.views')),
    path('__reload__/', include('django_browser_reload.urls')),
    path('', include('app.views')),
]

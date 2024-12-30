from django.urls import path, include
import admin.views

urlpatterns = [
    path('admin/', include('admin.views')),
    path('__reload__/', include('django_browser_reload.urls')),
    path('', include('app.views')),
]

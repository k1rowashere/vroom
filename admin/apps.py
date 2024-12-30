from django.apps import AppConfig


class AdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin'
   
    def ready(self):
        from django.contrib.auth.models import User
        if not User.objects.filter(username='kirowashere@gmail.com').exists():
            User.objects.create_superuser('kirowashere@gmail.com', "kirowashere@gmail.com", 'kirowashere')

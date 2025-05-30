from django.apps import AppConfig
from django.contrib.auth import get_user_model
import logging

class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'
    


logger = logging.getLogger(__name__)

def create_default_superuser():
    User = get_user_model()
    username = 'admin'
    email = 'admin@example.com'
    password = 'your-strong-password'

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        logger.info(f"Superuser '{username}' created.")
    else:
        logger.info(f"Superuser '{username}' already exists.")

class YourAppConfig(AppConfig):
    name = 'yourapp'

    def ready(self):
        create_default_superuser()

from django.apps import AppConfig
# import insta.signal


class InstaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'insta'

    def ready(self):
        import insta.signal

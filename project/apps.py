from django.apps import AppConfig
from django.conf import settings


class ProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project'

    def ready(self):
        import django
        from django.contrib.auth import get_user_model
        from rest_framework_simplejwt.tokens import RefreshToken

        if not django.apps.apps.ready:
            return

        User = get_user_model()
        try:
            user = User.objects.get(username='nandhatrainer')  # or any default user
            refresh = RefreshToken.for_user(user)
            print(f"\n✅ JWT Token for {user.username}:\n{str(refresh.access_token)}\n")
        except User.DoesNotExist:
            print("\n⚠️ User 'nandhatrainer' not found. Cannot generate JWT Token.\n")

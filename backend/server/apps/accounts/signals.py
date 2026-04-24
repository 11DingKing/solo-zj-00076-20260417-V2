from django.contrib.auth import get_user_model
from django.dispatch import receiver
from djoser.signals import user_registered
from .views import send_activation_email

User = get_user_model()


@receiver(user_registered)
def handle_user_registered(sender, user, request, **kwargs):
    """
    Signal handler that sends custom activation email when user registers.
    This is used because SEND_ACTIVATION_EMAIL is set to False in settings,
    but we still want to send activation emails using our custom token format.
    """
    if not user.is_active:
        context = {'user': user}
        send_activation_email(user, context)

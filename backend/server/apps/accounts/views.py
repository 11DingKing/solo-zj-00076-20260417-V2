from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone

from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication

from djoser import signals
from djoser.compat import get_user_email
from djoser.conf import settings as djoser_settings

from .utils import (
    generate_activation_token,
    validate_activation_token,
    mark_token_as_used,
    generate_uid,
    decode_uid,
    can_send_email,
    record_email_sent,
    EMAIL_THROTTLE_MINUTES
)

User = get_user_model()


def send_activation_email(user, context):
    """
    Send activation email with HTML template.
    """
    email = get_user_email(user)
    
    protocol = settings.PROTOCOL
    domain = settings.DOMAIN
    site_name = settings.SITE_NAME
    
    uid = generate_uid(user.id)
    token = generate_activation_token(user.id)
    
    activation_url = f"{protocol}://{domain}/activate/{uid}/{token}"
    
    html_content = render_to_string(
        'emails/activation.html',
        {
            'user': user,
            'site_name': site_name,
            'activation_url': activation_url,
            'protocol': protocol,
            'domain': domain,
        }
    )
    
    text_content = strip_tags(html_content)
    
    subject = f"Activate your {site_name} account"
    
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com')
    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[email]
    )
    email_message.attach_alternative(html_content, "text/html")
    email_message.send(fail_silently=True)
    
    record_email_sent(email)


class CustomActivationView(APIView):
    """
    Custom activation view that handles:
    - Token validation with HMAC-SHA256 signature
    - Token expiration (24 hours)
    - Preventing replay attacks (mark token as used)
    
    Error responses:
    - 400: Invalid token or token already used
    - 410: Token expired, please request a new one
    """
    permission_classes = [permissions.AllowAny]
    throttle_scope = None

    def post(self, request, *args, **kwargs):
        uid = request.data.get('uid')
        token = request.data.get('token')
        
        if not uid or not token:
            return Response(
                {'detail': 'UID and token are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_id = decode_uid(uid)
        if user_id is None:
            return Response(
                {'detail': 'Invalid UID.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validated_user_id, error = validate_activation_token(token)
        
        if error == 'expired':
            return Response(
                {
                    'detail': 'This activation link has expired. Please request a new one.',
                    'code': 'token_expired',
                    'resend_url': '/api/v1/users/resend_activation/'
                },
                status=status.HTTP_410_GONE
            )
        
        if error == 'already_used':
            return Response(
                {
                    'detail': 'This activation link has already been used. Please request a new one if needed.',
                    'code': 'token_already_used'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if error == 'invalid' or validated_user_id is None:
            return Response(
                {'detail': 'Invalid activation token.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if validated_user_id != user_id:
            return Response(
                {'detail': 'Token does not match the provided user.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user.is_active:
            return Response(
                {'detail': 'User is already active.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        mark_token_as_used(token, user_id)
        
        user.is_active = True
        user.save()
        
        signals.user_activated.send(
            sender=self.__class__, user=user, request=request
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomResendActivationView(APIView):
    """
    Custom resend activation view with rate limiting.
    - Same email can only be sent once per minute
    """
    permission_classes = [permissions.AllowAny]
    throttle_scope = None

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'email': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        can_send, remaining_seconds = can_send_email(email)
        
        if not can_send:
            return Response(
                {
                    'detail': f'Please wait {remaining_seconds} seconds before requesting another activation email.',
                    'code': 'rate_limited',
                    'retry_after': remaining_seconds
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'email': ['User with this email does not exist.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user.is_active:
            return Response(
                {'detail': 'User is already active.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        context = {'user': user}
        send_activation_email(user, context)
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class IsEmailVerified(permissions.BasePermission):
    """
    Permission class that checks if the user's email is verified.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_active

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

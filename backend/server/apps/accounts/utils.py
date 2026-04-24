import hashlib
import hmac
import json
import base64
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from django.conf import settings
from django.utils import timezone
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from .models import UsedToken, EmailThrottle


TOKEN_EXPIRY_HOURS = 24
EMAIL_THROTTLE_MINUTES = 1


def generate_activation_token(user_id: int) -> str:
    """
    Generate HMAC-SHA256 signed activation token containing:
    - user_id: the user's ID
    - exp: expiration timestamp (24 hours from now)
    - type: token type (for future extensibility)
    
    Format: base64(payload).hmac_signature
    """
    payload = {
        'user_id': user_id,
        'exp': int(time.time()) + (TOKEN_EXPIRY_HOURS * 3600),
        'type': 'activation'
    }
    
    payload_json = json.dumps(payload, separators=(',', ':'))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode('utf-8')).decode('utf-8').rstrip('=')
    
    signature = hmac.new(
        settings.SECRET_KEY.encode('utf-8'),
        payload_b64.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return f"{payload_b64}.{signature}"


def validate_activation_token(token: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Validate an activation token.
    
    Returns:
        Tuple of (user_id, error_message)
        - If valid: (user_id, None)
        - If invalid: (None, error_message)
        - If expired: (None, 'expired')
        - If already used: (None, 'already_used')
    """
    try:
        if '.' not in token:
            return None, 'invalid'
        
        payload_b64, signature = token.rsplit('.', 1)
        
        expected_signature = hmac.new(
            settings.SECRET_KEY.encode('utf-8'),
            payload_b64.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return None, 'invalid'
        
        padding = 4 - (len(payload_b64) % 4)
        if padding != 4:
            payload_b64 += '=' * padding
        
        payload_json = base64.urlsafe_b64decode(payload_b64.encode('utf-8')).decode('utf-8')
        payload = json.loads(payload_json)
        
        if payload.get('type') != 'activation':
            return None, 'invalid'
        
        if int(time.time()) > payload.get('exp', 0):
            return None, 'expired'
        
        user_id = payload.get('user_id')
        if user_id is None:
            return None, 'invalid'
        
        token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
        if UsedToken.objects.filter(token_hash=token_hash).exists():
            return None, 'already_used'
        
        return user_id, None
        
    except (json.JSONDecodeError, base64.binascii.Error, ValueError):
        return None, 'invalid'


def mark_token_as_used(token: str, user_id: int) -> None:
    """
    Mark a token as used to prevent replay attacks.
    """
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    UsedToken.objects.create(token_hash=token_hash, user_id=user_id)


def can_send_email(email: str) -> Tuple[bool, int]:
    """
    Check if an email can be sent (rate limiting).
    
    Returns:
        Tuple of (can_send, seconds_remaining)
        - If can send: (True, 0)
        - If rate limited: (False, seconds remaining until next allowed)
    """
    try:
        throttle = EmailThrottle.objects.get(email=email)
        elapsed = (timezone.now() - throttle.last_sent_at).total_seconds()
        remaining = int((EMAIL_THROTTLE_MINUTES * 60) - elapsed)
        
        if remaining <= 0:
            return True, 0
        return False, remaining
    except EmailThrottle.DoesNotExist:
        return True, 0


def record_email_sent(email: str) -> None:
    """
    Record that an email was sent for rate limiting purposes.
    """
    throttle, created = EmailThrottle.objects.get_or_create(
        email=email,
        defaults={'last_sent_at': timezone.now(), 'send_count': 1}
    )
    
    if not created:
        throttle.last_sent_at = timezone.now()
        throttle.send_count += 1
        throttle.save()


def generate_uid(user_id: int) -> str:
    """
    Generate a URL-safe base64 encoded user ID (compatible with Djoser format).
    """
    return base64.urlsafe_b64encode(str(user_id).encode('utf-8')).decode('utf-8').rstrip('=')


def decode_uid(uid: str) -> Optional[int]:
    """
    Decode a base64 encoded user ID.
    """
    try:
        padding = 4 - (len(uid) % 4)
        if padding != 4:
            uid += '=' * padding
        user_id_str = base64.urlsafe_b64decode(uid.encode('utf-8')).decode('utf-8')
        return int(user_id_str)
    except (base64.binascii.Error, ValueError, UnicodeDecodeError):
        return None

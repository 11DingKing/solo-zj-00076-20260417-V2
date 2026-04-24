from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from djoser import email
from djoser.conf import settings as djoser_settings

from .utils import generate_activation_token, generate_uid, record_email_sent

User = get_user_model()


class CustomActivationEmail(email.BaseDjoserEmail):
    template_name = "emails/activation.html"
    html_template_name = "emails/activation.html"

    def get_context_data(self):
        context = super().get_context_data()
        
        user = context.get("user")
        if user:
            protocol = settings.PROTOCOL
            domain = settings.DOMAIN
            site_name = settings.SITE_NAME
            
            uid = generate_uid(user.id)
            token = generate_activation_token(user.id)
            
            activation_url = f"{protocol}://{domain}/activate/{uid}/{token}"
            
            context.update({
                "site_name": site_name,
                "activation_url": activation_url,
                "protocol": protocol,
                "domain": domain,
            })
        
        return context

    def send(self, to, *args, **kwargs):
        self.context = self.get_context_data()
        
        subject = djoser_settings.EMAIL.subject
        rendered_subject = subject.format(**self.context).strip()
        
        html_content = render_to_string(
            self.html_template_name,
            self.context
        )
        text_content = strip_tags(html_content)
        
        from_email = djoser_settings.EMAIL.from_email or settings.DEFAULT_FROM_EMAIL
        
        email_message = EmailMultiAlternatives(
            subject=rendered_subject,
            body=text_content,
            from_email=from_email,
            to=to
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send(fail_silently=True)
        
        for email_address in to:
            record_email_sent(email_address)


class CustomPasswordResetEmail(email.PasswordResetEmail):
    pass

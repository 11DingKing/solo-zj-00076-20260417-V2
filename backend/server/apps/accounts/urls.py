from django.urls import re_path, include
from .views import CustomActivationView, CustomResendActivationView

accounts_urlpatterns = [
    re_path(r'^api/v1/users/activation/$', CustomActivationView.as_view(), name='custom-activation'),
    re_path(r'^api/v1/users/resend_activation/$', CustomResendActivationView.as_view(), name='custom-resend-activation'),
    re_path(r'^api/v1/', include('djoser.urls')),
    re_path(r'^api/v1/', include('djoser.urls.authtoken')),
]

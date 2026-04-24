
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from djoser.conf import settings
from djoser.serializers import TokenCreateSerializer, UserSerializer

User = get_user_model()


class CustomTokenCreateSerializer(TokenCreateSerializer):

    def validate(self, attrs):
        password = attrs.get("password")
        params = {settings.LOGIN_FIELD: attrs.get(settings.LOGIN_FIELD)}
        self.user = authenticate(
            request=self.context.get("request"), **params, password=password
        )
        if not self.user:
            self.user = User.objects.filter(**params).first()
            if self.user and not self.user.check_password(password):
                self.fail("invalid_credentials")
        if self.user:
            return attrs
        self.fail("invalid_credentials")


class CustomUserSerializer(UserSerializer):
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('is_active',)


class UserWithVerificationStatusSerializer(serializers.ModelSerializer):
    is_verified = serializers.BooleanField(source='is_active', read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_active', 'is_verified')
        read_only_fields = ('id', 'is_active', 'is_verified')

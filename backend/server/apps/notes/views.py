from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from apps.notes.models import Note 
from apps.notes.serializers import NoteSerializer
from apps.accounts.views import IsEmailVerified


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    queryset = Note.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsEmailVerified()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        if not request.user.is_active:
            return Response(
                {
                    'detail': 'You must verify your email address before creating notes.',
                    'code': 'email_not_verified',
                    'resend_url': '/api/v1/users/resend_activation/'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not request.user.is_active:
            return Response(
                {
                    'detail': 'You must verify your email address before updating notes.',
                    'code': 'email_not_verified'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_active:
            return Response(
                {
                    'detail': 'You must verify your email address before deleting notes.',
                    'code': 'email_not_verified'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(created_by=self.request.user).order_by('-created_at')

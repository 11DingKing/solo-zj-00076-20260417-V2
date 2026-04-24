from django.urls import re_path, include 
from rest_framework.routers import DefaultRouter
from apps.notes.views import NoteViewSet

router = DefaultRouter()
router.register("notes", NoteViewSet, basename="notes")
notes_urlpatterns = [re_path(r"api/v1/", include(router.urls))]

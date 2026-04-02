from rest_framework import viewsets

from apps.accounts.permissions import IsSystemAdmin
from apps.announcements.models import Announcement
from apps.announcements.serializers import AnnouncementSerializer


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.select_related("created_by").all().order_by("-id")
    serializer_class = AnnouncementSerializer
    permission_classes = [IsSystemAdmin]
    search_fields = ["title", "content"]
    ordering_fields = ["id", "created_at", "updated_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

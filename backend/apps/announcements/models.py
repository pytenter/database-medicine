from django.db import models

from apps.common.models import TimeStampedModel


class Announcement(TimeStampedModel):
    title = models.CharField(max_length=120, verbose_name="????")
    content = models.TextField(verbose_name="????")
    is_published = models.BooleanField(default=True, verbose_name="????")
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="announcements",
        verbose_name="???",
    )

    class Meta:
        db_table = "announcement"
        ordering = ["-id"]

    def __str__(self):
        return self.title

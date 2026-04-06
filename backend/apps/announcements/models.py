from django.db import models

from apps.common.models import TimeStampedModel


class Announcement(TimeStampedModel):
    title = models.CharField(max_length=120, verbose_name="公告标题")
    content = models.TextField(verbose_name="公告内容")
    is_published = models.BooleanField(default=True, verbose_name="发布状态")
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="announcements",
        verbose_name="发布人",
    )

    class Meta:
        db_table = "announcement"
        ordering = ["-id"]

    def __str__(self):
        return self.title
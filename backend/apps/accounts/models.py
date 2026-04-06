from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.models import TimeStampedModel


class RoleChoices(models.TextChoices):
    SYSTEM_ADMIN = "system_admin", "系统管理员"
    PHARMACY_ADMIN = "pharmacy_admin", "药店管理员"
    SALESPERSON = "salesperson", "销售人员"


class User(AbstractUser, TimeStampedModel):
    # This project does not use Django's built-in group/permission tables.
    groups = None
    user_permissions = None

    full_name = models.CharField(max_length=100, verbose_name="Full Name")
    role = models.CharField(max_length=30, choices=RoleChoices.choices, verbose_name="Role")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Phone")
    store = models.ForeignKey(
        "inventory.Store",
        on_delete=models.SET_NULL,
        related_name="users",
        null=True,
        blank=True,
        verbose_name="Assigned Store",
    )
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        db_table = "sys_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class ShiftPeriodChoices(models.TextChoices):
    MORNING = "morning", "早班"
    AFTERNOON = "afternoon", "中班"
    EVENING = "evening", "晚班"


class ShiftSchedule(TimeStampedModel):
    store = models.ForeignKey("inventory.Store", on_delete=models.CASCADE, related_name="shift_schedules")
    salesperson = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shift_schedules")
    shift_date = models.DateField(verbose_name="Shift Date")
    shift_period = models.CharField(max_length=20, choices=ShiftPeriodChoices.choices, verbose_name="Shift Period")
    start_time = models.TimeField(verbose_name="Start Time")
    end_time = models.TimeField(verbose_name="End Time")
    note = models.CharField(max_length=255, blank=True, verbose_name="Note")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_shift_schedules")

    class Meta:
        db_table = "shift_schedule"
        ordering = ["-shift_date", "start_time", "id"]

    def __str__(self):
        return f"{self.salesperson.full_name} - {self.shift_date}"

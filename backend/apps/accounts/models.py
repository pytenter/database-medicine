from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.models import TimeStampedModel


class RoleChoices(models.TextChoices):
    SYSTEM_ADMIN = "system_admin", "System Administrator"
    PHARMACY_ADMIN = "pharmacy_admin", "Pharmacy Administrator"
    SALESPERSON = "salesperson", "Salesperson"


class User(AbstractUser, TimeStampedModel):
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

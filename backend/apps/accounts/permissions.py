from rest_framework.permissions import BasePermission


class IsSystemAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "system_admin"


class IsPharmacyAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "pharmacy_admin"


class IsSalesperson(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "salesperson"


class IsSystemOrPharmacyAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {"system_admin", "pharmacy_admin"}

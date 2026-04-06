from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import RoleChoices, ShiftSchedule, User
from apps.accounts.permissions import IsPharmacyAdmin, IsSystemAdmin
from apps.accounts.serializers import (
    LoginSerializer,
    ShiftScheduleSerializer,
    UserCreateUpdateSerializer,
    UserSerializer,
)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("store").all().order_by("id")
    permission_classes = [IsSystemAdmin]
    search_fields = ["username", "full_name", "phone", "email"]
    ordering_fields = ["id", "username", "created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        role_value = self.request.query_params.get("role")
        if role_value in {RoleChoices.PHARMACY_ADMIN, RoleChoices.SALESPERSON}:
            queryset = queryset.filter(role=role_value)
        is_active_value = self.request.query_params.get("is_active")
        if is_active_value is not None:
            normalized = str(is_active_value).strip().lower()
            if normalized in {"true", "1", "yes"}:
                queryset = queryset.filter(is_active=True)
            elif normalized in {"false", "0", "no"}:
                queryset = queryset.filter(is_active=False)
        return queryset

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return UserCreateUpdateSerializer
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user.id == request.user.id:
            raise PermissionDenied("\u4e0d\u80fd\u505c\u7528\u5f53\u524d\u767b\u5f55\u4e2d\u7684\u7cfb\u7edf\u7ba1\u7406\u5458\u8d26\u53f7\u3002")
        if not user.is_active:
            return Response({"detail": "\u8be5\u8d26\u53f7\u5df2\u5904\u4e8e\u505c\u7528\u72b6\u6001\u3002"}, status=status.HTTP_200_OK)
        if user.role == RoleChoices.SYSTEM_ADMIN and User.objects.filter(role=RoleChoices.SYSTEM_ADMIN, is_active=True).exclude(id=user.id).count() == 0:
            raise PermissionDenied("\u81f3\u5c11\u9700\u8981\u4fdd\u7559\u4e00\u4e2a\u542f\u7528\u4e2d\u7684\u7cfb\u7edf\u7ba1\u7406\u5458\u8d26\u53f7\u3002")
        user.is_active = False
        user.save(update_fields=["is_active", "updated_at"])
        return Response({"detail": f"\u7528\u6237 {user.username} \u5df2\u505c\u7528\u3002"}, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=True)
    def reset_password(self, request, pk=None):
        user = self.get_object()
        user.set_password("Admin@123")
        user.save(update_fields=["password"])
        return Response({"message": "密码已重置为 Admin@123。"})


class ShiftScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ShiftScheduleSerializer
    permission_classes = [IsPharmacyAdmin]
    search_fields = ["salesperson__full_name", "salesperson__username", "note"]
    ordering_fields = ["shift_date", "start_time", "created_at"]

    def get_queryset(self):
        queryset = ShiftSchedule.objects.select_related("store", "salesperson", "created_by").all().order_by("-shift_date", "start_time", "id")
        user = self.request.user
        if user.store_id:
            queryset = queryset.filter(store_id=user.store_id, salesperson__role=RoleChoices.SALESPERSON)
        else:
            queryset = queryset.none()
        salesperson_id = self.request.query_params.get("salesperson")
        if salesperson_id:
            queryset = queryset.filter(salesperson_id=salesperson_id)
        shift_date = self.request.query_params.get("shift_date")
        if shift_date:
            queryset = queryset.filter(shift_date=shift_date)
        return queryset

    @action(methods=["get"], detail=False)
    def salespeople(self, request):
        queryset = User.objects.filter(role=RoleChoices.SALESPERSON, store_id=request.user.store_id, is_active=True).order_by("id")
        return Response(UserSerializer(queryset, many=True).data)

    def _validate_scope(self, serializer):
        user = self.request.user
        store = serializer.validated_data.get("store", getattr(serializer.instance, "store", None))
        salesperson = serializer.validated_data.get("salesperson", getattr(serializer.instance, "salesperson", None))
        if not user.store_id or not store or store.id != user.store_id:
            raise PermissionDenied("只能管理所属门店的班次排班。")
        if salesperson is None or salesperson.role != RoleChoices.SALESPERSON or salesperson.store_id != user.store_id:
            raise PermissionDenied("只能为当前门店销售人员排班。")

    def perform_create(self, serializer):
        self._validate_scope(serializer)
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        self._validate_scope(serializer)
        serializer.save(created_by=self.request.user)

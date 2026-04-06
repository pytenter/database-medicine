from django.db.models.deletion import ProtectedError
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
        return queryset

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return UserCreateUpdateSerializer
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user.id == request.user.id:
            raise PermissionDenied("不能删除当前登录中的系统管理员账号。")
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "该员工已关联业务数据，暂时不能直接删除。请先停用账号，或先清理其关联记录。"},
                status=status.HTTP_400_BAD_REQUEST,
            )


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

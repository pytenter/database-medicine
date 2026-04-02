from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import RoleChoices, ShiftSchedule, User


class UserSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source="store.name", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "full_name",
            "role",
            "role_display",
            "phone",
            "email",
            "is_active",
            "store",
            "store_name",
            "created_at",
            "updated_at",
        ]


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "password",
            "full_name",
            "role",
            "phone",
            "email",
            "is_active",
            "store",
        ]

    def validate(self, attrs):
        role = attrs.get("role") or getattr(self.instance, "role", None)
        store = attrs.get("store") if "store" in attrs else getattr(self.instance, "store", None)
        if role in {RoleChoices.PHARMACY_ADMIN, RoleChoices.SALESPERSON} and store is None:
            raise serializers.ValidationError("药店管理员和销售人员必须关联所属门店。")
        if role == RoleChoices.SYSTEM_ADMIN:
            attrs["store"] = None
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password", "Admin@123")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class ShiftScheduleSerializer(serializers.ModelSerializer):
    salesperson_name = serializers.CharField(source="salesperson.full_name", read_only=True)
    store_name = serializers.CharField(source="store.name", read_only=True)
    shift_period_display = serializers.CharField(source="get_shift_period_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)

    class Meta:
        model = ShiftSchedule
        fields = [
            "id",
            "store",
            "store_name",
            "salesperson",
            "salesperson_name",
            "shift_date",
            "shift_period",
            "shift_period_display",
            "start_time",
            "end_time",
            "note",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by"]

    def validate(self, attrs):
        salesperson = attrs.get("salesperson") or getattr(self.instance, "salesperson", None)
        store = attrs.get("store") or getattr(self.instance, "store", None)
        start_time = attrs.get("start_time") or getattr(self.instance, "start_time", None)
        end_time = attrs.get("end_time") or getattr(self.instance, "end_time", None)
        if salesperson and salesperson.role != RoleChoices.SALESPERSON:
            raise serializers.ValidationError("只能为销售人员安排班次。")
        if salesperson and store and salesperson.store_id != store.id:
            raise serializers.ValidationError("班次人员必须属于当前门店。")
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("班次开始时间必须早于结束时间。")
        return attrs


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("账号或密码错误。")
        if not user.is_active:
            raise serializers.ValidationError("该账号已停用。")

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
        }

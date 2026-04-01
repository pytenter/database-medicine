from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import RoleChoices, User


class UserSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source="store.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "full_name",
            "role",
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
            raise serializers.ValidationError("Pharmacy administrators and salespersons must be assigned to a store.")
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


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("This user has been disabled.")

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
        }

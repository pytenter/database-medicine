from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import RoleChoices, User
from apps.accounts.permissions import IsSystemAdmin
from apps.accounts.serializers import LoginSerializer, UserCreateUpdateSerializer, UserSerializer


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

    @action(methods=["post"], detail=True)
    def reset_password(self, request, pk=None):
        user = self.get_object()
        user.set_password("Admin@123")
        user.save(update_fields=["password"])
        return Response({"message": "?????? Admin@123?"})

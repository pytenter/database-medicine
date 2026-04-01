from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.sales.models import SaleOrder
from apps.sales.serializers import (
    LogisticsUpdateSerializer,
    OrderLogisticsSerializer,
    OrderReviewSerializer,
    ReviewSubmitSerializer,
    SaleCreateSerializer,
    SaleOrderSerializer,
)


class SalesPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return request.user.role in {"system_admin", "pharmacy_admin", "salesperson"}
        return request.user.role == "salesperson"


class SaleOrderViewSet(viewsets.ModelViewSet):
    queryset = SaleOrder.objects.select_related("store", "salesperson").prefetch_related(
        "items",
        "items__medicine",
        "items__medicine__manufacturer",
        "logistics",
        "review",
    )
    permission_classes = [SalesPermission]
    search_fields = ["order_no", "customer_name", "customer_phone", "salesperson__full_name", "store__name"]
    ordering_fields = ["id", "created_at", "total_amount"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role in {"pharmacy_admin", "salesperson"} and user.store_id:
            queryset = queryset.filter(store_id=user.store_id)

        search = self.request.query_params.get("search")
        status_value = self.request.query_params.get("status")
        if search:
            queryset = queryset.filter(
                Q(order_no__icontains=search)
                | Q(customer_name__icontains=search)
                | Q(customer_phone__icontains=search)
                | Q(store__name__icontains=search)
            )
        if status_value:
            queryset = queryset.filter(order_status=status_value)
        return queryset.distinct().order_by("-id")

    def get_serializer_class(self):
        if self.action == "create":
            return SaleCreateSerializer
        return SaleOrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(SaleOrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="logistics")
    def add_logistics(self, request, pk=None):
        order = self.get_object()
        serializer = LogisticsUpdateSerializer(data=request.data, context={"request": request, "order": order})
        serializer.is_valid(raise_exception=True)
        logistics = serializer.save()
        return Response(OrderLogisticsSerializer(logistics).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="review")
    def submit_review(self, request, pk=None):
        order = self.get_object()
        serializer = ReviewSubmitSerializer(data=request.data, context={"request": request, "order": order})
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        return Response(OrderReviewSerializer(review).data, status=status.HTTP_201_CREATED)

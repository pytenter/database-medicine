from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, DecimalField, Sum, Value
from django.db.models.functions import Coalesce, TruncDate
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import RoleChoices, User
from apps.announcements.models import Announcement
from apps.inventory.models import Inventory, Store
from apps.sales.models import OrderLogistics, OrderReview, SaleOrder


class DashboardOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        sales = SaleOrder.objects.select_related("store", "salesperson")
        inventories = Inventory.objects.select_related("medicine__category", "store")
        stores = Store.objects.all()
        employees = User.objects.filter(role__in=[RoleChoices.PHARMACY_ADMIN, RoleChoices.SALESPERSON])

        if user.role in {RoleChoices.PHARMACY_ADMIN, RoleChoices.SALESPERSON} and user.store_id:
            sales = sales.filter(store_id=user.store_id)
            inventories = inventories.filter(store_id=user.store_id)
            stores = stores.filter(id=user.store_id)
            employees = employees.filter(store_id=user.store_id)

        now = timezone.localtime()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

        total_stats = sales.aggregate(
            order_total=Count("id"),
            total_revenue=Coalesce(Sum("total_amount"), Value(Decimal("0.00")), output_field=DecimalField(max_digits=12, decimal_places=2)),
        )
        month_stats = sales.filter(created_at__gte=month_start).aggregate(
            order_count=Count("id"),
            revenue=Coalesce(Sum("total_amount"), Value(Decimal("0.00")), output_field=DecimalField(max_digits=12, decimal_places=2)),
        )
        year_stats = sales.filter(created_at__gte=year_start).aggregate(
            order_count=Count("id"),
            revenue=Coalesce(Sum("total_amount"), Value(Decimal("0.00")), output_field=DecimalField(max_digits=12, decimal_places=2)),
        )

        sales_daily = {
            row["day"]: row
            for row in sales.annotate(day=TruncDate("created_at")).values("day").annotate(
                revenue=Coalesce(Sum("total_amount"), Value(Decimal("0.00")), output_field=DecimalField(max_digits=12, decimal_places=2)),
                order_count=Count("id"),
            )
        }

        last_ten_days = []
        for offset in range(9, -1, -1):
            day = now.date() - timedelta(days=offset)
            row = sales_daily.get(day, {})
            last_ten_days.append({
                "date": day.isoformat(),
                "label": day.strftime("%m-%d"),
                "revenue": float(row.get("revenue", 0) or 0),
                "order_count": int(row.get("order_count", 0) or 0),
            })

        category_rows = list(inventories.values("medicine__category__name").annotate(total_quantity=Coalesce(Sum("quantity"), 0)).order_by("-total_quantity")[:6])
        total_quantity = sum(int(row["total_quantity"] or 0) for row in category_rows) or 1
        category_stats = [
            {
                "label": row["medicine__category__name"] or "\u672a\u5206\u7c7b",
                "value": int(row["total_quantity"] or 0),
                "percent": round((int(row["total_quantity"] or 0) / total_quantity) * 100, 1),
            }
            for row in category_rows
        ]

        notices = [
            {
                "id": item["id"],
                "title": item["title"],
                "content": item["content"],
                "time": item["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
            }
            for item in Announcement.objects.filter(is_published=True).order_by("-created_at", "-id").values("id", "title", "content", "created_at")[:3]
        ]

        logistics = OrderLogistics.objects.all()
        reviews = OrderReview.objects.all()
        if user.role in {RoleChoices.PHARMACY_ADMIN, RoleChoices.SALESPERSON} and user.store_id:
            logistics = logistics.filter(order__store_id=user.store_id)
            reviews = reviews.filter(order__store_id=user.store_id)

        logistics_daily = {row["day"]: int(row["count"]) for row in logistics.annotate(day=TruncDate("created_at")).values("day").annotate(count=Count("id"))}
        reviews_daily = {row["day"]: int(row["count"]) for row in reviews.annotate(day=TruncDate("created_at")).values("day").annotate(count=Count("id"))}

        activity_last_seven_days = []
        for offset in range(6, -1, -1):
            day = now.date() - timedelta(days=offset)
            sale_count = int(sales_daily.get(day, {}).get("order_count", 0) or 0)
            logistics_count = logistics_daily.get(day, 0)
            review_count = reviews_daily.get(day, 0)
            activity_last_seven_days.append({
                "date": day.isoformat(),
                "label": day.strftime("%m-%d"),
                "value": sale_count + logistics_count + review_count,
            })

        return Response({
            "top_stats": {
                "order_total": int(total_stats["order_total"] or 0),
                "total_revenue": float(total_stats["total_revenue"] or 0),
                "store_count": stores.count(),
                "employee_count": employees.count(),
            },
            "summary": {
                "month_order_count": int(month_stats["order_count"] or 0),
                "month_revenue": float(month_stats["revenue"] or 0),
                "year_order_count": int(year_stats["order_count"] or 0),
                "year_revenue": float(year_stats["revenue"] or 0),
            },
            "charts": {
                "income_last_10_days": [{"label": item["label"], "value": item["revenue"]} for item in last_ten_days],
                "orders_last_10_days": [{"label": item["label"], "value": item["order_count"]} for item in last_ten_days],
                "category_stats": category_stats,
                "activity_last_7_days": activity_last_seven_days,
            },
            "notices": notices,
        })

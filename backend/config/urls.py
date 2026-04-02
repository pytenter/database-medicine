from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def api_root(_request):
    return JsonResponse(
        {
            "project": "连锁药店管理系统",
            "status": "运行中",
            "message": "后端服务运行正常。请使用 http://127.0.0.1:5173/ 访问前端，或调用 /api/* 接口。",
            "routes": {
                "login": "/api/auth/login/",
                "current_user": "/api/auth/me/",
                "users": "/api/users/",
                "dashboard": "/api/dashboard/overview/",
                "announcements": "/api/announcements/",
                "medicines": "/api/medicines/",
                "inventory": "/api/inventory/",
                "sales": "/api/sales/",
            },
        }
    )


urlpatterns = [
    path("", api_root),
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/users/", include("apps.accounts.user_urls")),
    path("api/dashboard/", include("apps.common.urls")),
    path("api/announcements/", include("apps.announcements.urls")),
    path("api/medicines/", include("apps.medicine.urls")),
    path("api/inventory/", include("apps.inventory.urls")),
    path("api/sales/", include("apps.sales.urls")),
]


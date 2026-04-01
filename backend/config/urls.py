from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def api_root(_request):
    return JsonResponse(
        {
            "project": "Chain Pharmacy Management System",
            "status": "running",
            "message": "Backend service is available. Use the frontend at http://127.0.0.1:5173 or call /api/* endpoints.",
            "routes": {
                "login": "/api/auth/login/",
                "current_user": "/api/auth/me/",
                "users": "/api/users/",
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
    path("api/medicines/", include("apps.medicine.urls")),
    path("api/inventory/", include("apps.inventory.urls")),
    path("api/sales/", include("apps.sales.urls")),
]

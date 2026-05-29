from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.db import connection
from django.db.utils import OperationalError

def healthz(request):
    try:
        connection.ensure_connection()
        return JsonResponse({"status": "ok"})
    except OperationalError:
        return JsonResponse({"status": "error", "detail": "Database unreachable"}, status=503)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz', healthz),
]
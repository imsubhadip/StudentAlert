"""Main URL file. It sends every normal page to the students app."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("students.urls")),
]

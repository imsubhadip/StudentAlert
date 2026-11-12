"""Register the tables in the Django admin site (/admin/)."""
from django.contrib import admin

from .models import Student, ContactMessage


class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "roll_number", "email", "predicted_outcome", "created_at")
    search_fields = ("name", "roll_number", "email")
    list_filter = ("predicted_outcome",)


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email")


admin.site.register(Student, StudentAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)

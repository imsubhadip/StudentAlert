"""URLs of the students app."""
from django.urls import path

from . import views

urlpatterns = [
    # public pages
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),

    # student management and prediction pages (no login required)
    path("dashboard/", views.dashboard, name="dashboard"),
    path("bulk-analysis/", views.bulk_analysis, name="bulk_analysis"),
    path("bulk-analysis/report.pdf", views.bulk_pdf, name="bulk_pdf"),
    path("bulk-analysis/results.csv", views.bulk_csv, name="bulk_csv"),
    path("bulk-analysis/results.xlsx", views.bulk_xlsx, name="bulk_xlsx"),
    path("students/", views.student_list, name="student_list"),
    path("students/add/", views.add_student, name="add_student"),
    path("students/<int:student_id>/", views.student_detail, name="student_detail"),
    path("students/<int:student_id>/edit/", views.edit_student, name="edit_student"),
    path("students/<int:student_id>/delete/", views.delete_student, name="delete_student"),
    path("students/<int:student_id>/predict/", views.predict_student, name="predict_student"),
    path("students/<int:student_id>/result/", views.prediction_result, name="prediction_result"),
    path("students/<int:student_id>/report.pdf", views.individual_pdf, name="individual_pdf"),
]

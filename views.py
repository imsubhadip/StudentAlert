"""Views (the Python code behind each page) for StudentAlert."""
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.http import require_POST
import io, csv, json
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from . import ml_helper
from .forms import (StudentForm, PredictionForm,
                    FIELD_GROUPS, FEATURE_FIELDS)
from .models import Student

# Short advice shown on the result page (it is only a suggestion)
ADVICE = {
    "Dropout": "The model found a pattern similar to students who dropped out. "
               "It may help to talk to the student and offer academic or "
               "financial support.",
    "Enrolled": "The model found a pattern similar to students who had not yet "
                "finished their course at the end of its normal duration. "
                "Extra guidance may help the student finish on time.",
    "Graduate": "The model found a pattern similar to students who graduated. "
                "Normal monitoring is enough, but keep supporting the student.",
}


def build_recommendations(student):
    """Create transparent, rule-based support suggestions from entered fields.

    These are support prompts, not causal explanations or medical/financial
    determinations. Thresholds are operational flags and should be reviewed
    by a human adviser.
    """
    items = []
    enrolled = student.units_enrolled or 0
    approved = student.units_approved or 0
    grade = student.units_grade

    if enrolled > 0 and approved / enrolled < 0.5:
        items.append({
            "title": "Academic mentoring", "priority": "High",
            "reason": f"The student has approved {approved} of {enrolled} enrolled first-semester units.",
            "action": "Arrange an adviser meeting, review missed coursework and offer subject-level tutoring."
        })
    elif grade is not None and grade < 10:
        items.append({
            "title": "Academic check-in", "priority": "High",
            "reason": f"The recorded first-semester average is {grade:g} on the dataset's 0–20 scale.",
            "action": "Review difficult subjects with the student and agree on a short study-support plan."
        })

    if student.debtor == 1 or student.tuition_up_to_date == 0:
        items.append({
            "title": "Fees and financial support review", "priority": "High",
            "reason": "The entered record indicates a debtor flag or tuition fees are not up to date.",
            "action": "Privately refer the student to the institution's fee-support or scholarship office; check eligibility rather than assuming need."
        })

    if (student.units_without_evaluations or 0) > 0:
        items.append({
            "title": "Engagement follow-up", "priority": "Medium",
            "reason": f"{student.units_without_evaluations} first-semester units are recorded without evaluations.",
            "action": "Ask the student whether attendance, access, timetable or assessment barriers need attention."
        })

    if student.scholarship_holder == 0 and (student.debtor == 1 or student.tuition_up_to_date == 0):
        items.append({
            "title": "Check available aid options", "priority": "Medium",
            "reason": "The record shows no scholarship flag alongside a fee-related flag.",
            "action": "Explain available institutional aid and application deadlines; do not infer eligibility from the model."
        })

    if not items:
        items.append({
            "title": "Routine student check-in", "priority": "Normal",
            "reason": "No specific support flag was triggered by the available entered fields.",
            "action": "Discuss the student's goals, confirm access to learning resources and review progress at the next academic checkpoint."
        })

    # Put urgent flags first, but never use the predicted class alone to prescribe support.
    order = {"High": 0, "Medium": 1, "Normal": 2}
    return sorted(items, key=lambda item: order[item["priority"]])


# ---------- Public pages ----------

def home(request):
    return render(request, "students/home.html")


def about(request):
    return render(request, "students/about.html")


# ---------- Dashboard ----------

def dashboard(request):
    """Analytics dashboard built only from saved predictions and model metadata."""
    from django.db.models import Avg, Count
    from .models import COURSE_CHOICES

    total_students = Student.objects.count()
    predicted = Student.objects.exclude(predicted_outcome="")
    dropout_count = predicted.filter(predicted_outcome="Dropout").count()
    enrolled_count = predicted.filter(predicted_outcome="Enrolled").count()
    graduate_count = predicted.filter(predicted_outcome="Graduate").count()
    predicted_total = dropout_count + enrolled_count + graduate_count
    high_risk = predicted.filter(dropout_chance__gte=60).count()
    recent_students = predicted.order_by("-predicted_on")[:5]

    # Risk bands are calculated from actual saved model probabilities.
    risk_bands = [
        predicted.filter(dropout_chance__lt=30).count(),
        predicted.filter(dropout_chance__gte=30, dropout_chance__lt=60).count(),
        predicted.filter(dropout_chance__gte=60).count(),
    ]

    # The model's course codes are the available programme grouping; no
    # unsupported department names are invented.
    course_names = dict(COURSE_CHOICES)
    course_rows = list(predicted.values("course").annotate(
        total=Count("id"), risk=Avg("dropout_chance")
    ).order_by("-risk")[:6])
    course_labels = [course_names.get(row["course"], f"Course {row['course']}") for row in course_rows]
    course_risks = [round(row["risk"] or 0, 1) for row in course_rows]

    # Group first-semester grades into bands and show their actual average
    # dropout probability. This is descriptive, not a causal relationship.
    grade_rows = []
    for low, high, label in [(0, 8, "0–8"), (8, 10, "8–10"), (10, 12, "10–12"), (12, 14, "12–14"), (14, 21, "14–20")]:
        group = predicted.filter(units_grade__gte=low, units_grade__lt=high)
        agg = group.aggregate(score=Avg("units_grade"), risk=Avg("dropout_chance"))
        if group.exists():
            grade_rows.append({"label": label, "score": round(agg["score"] or 0, 1), "risk": round(agg["risk"] or 0, 1)})

    # Feature importance comes from the loaded classifier, when available.
    factor_labels, factor_values = [], []
    try:
        model, columns = ml_helper.load_model()
        estimator = getattr(model, "named_steps", {}).get("classifier", model)
        importances = getattr(estimator, "feature_importances_", None)
        if importances is not None and len(importances) == len(columns):
            pairs = sorted(zip(columns, importances), key=lambda item: item[1], reverse=True)[:5]
            friendly = {
                "Curricular units 1st sem (approved)": "1st-sem approved units",
                "Curricular units 1st sem (grade)": "1st-sem average grade",
                "Curricular units 1st sem (evaluations)": "1st-sem evaluations",
                "Curricular units 1st sem (enrolled)": "1st-sem enrolled units",
                "Curricular units 1st sem (credited)": "1st-sem credited units",
                "Curricular units 1st sem (without evaluations)": "1st-sem units w/o evaluation",
                "Previous qualification (grade)": "Previous qualification grade",
                "Tuition fees up to date": "Tuition fee status",
                "Scholarship holder": "Scholarship status",
                "Debtor": "Outstanding fees status",
            }
            factor_labels = [friendly.get(name, name) for name, _ in pairs]
            # Shown as a percentage share of the model's total importance.
            factor_values = [round(float(value) * 100, 1) for _, value in pairs]
    except Exception:
        factor_labels, factor_values = [], []

    context = {
        "total_students": total_students, "dropout_count": dropout_count,
        "enrolled_count": enrolled_count, "graduate_count": graduate_count,
        "predicted_total": predicted_total, "not_predicted": total_students-predicted_total,
        "high_risk": high_risk, "recent_students": recent_students,
        "outcome_labels": json.dumps(["Graduate", "Enrolled", "Dropout"]),
        "outcome_values": json.dumps([graduate_count, enrolled_count, dropout_count]),
        "risk_values": json.dumps(risk_bands),
        "risk_percent": round((high_risk / predicted_total) * 100) if predicted_total else 0,
        "course_labels": json.dumps(course_labels), "course_risks": json.dumps(course_risks),
        "grade_labels": json.dumps([r["label"] for r in grade_rows]),
        "grade_scores": json.dumps([r["score"] for r in grade_rows]),
        "grade_risks": json.dumps([r["risk"] for r in grade_rows]),
        "has_factors": bool(factor_labels),
        "factor_labels": json.dumps(factor_labels), "factor_values": json.dumps(factor_values),
    }
    return render(request, "students/dashboard.html", context)


# ---------- Student management ----------

def student_list(request):
    search_text = request.GET.get("q", "").strip()

    students = Student.objects.all().order_by("name")
    if search_text != "":
        # search in name, roll number and email
        students = students.filter(
            Q(name__icontains=search_text)
            | Q(roll_number__icontains=search_text)
            | Q(email__icontains=search_text)
        )

    paginator = Paginator(students, 10)  # 10 students on each page
    page = paginator.get_page(request.GET.get("page"))

    context = {"page": page, "search_text": search_text, "total_found": paginator.count}
    return render(request, "students/student_list.html", context)


def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, "Student profile saved. Now complete the 30 model inputs in the guided prediction form.")
            return redirect("predict_student", student_id=student.id)
    else:
        form = StudentForm()
    context = {"form": form, "page_title": "Add student"}
    return render(request, "students/student_form.html", context)


def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student details updated.")
            return redirect("student_detail", student_id=student.id)
    else:
        form = StudentForm(instance=student)
    context = {"form": form, "page_title": "Edit student"}
    return render(request, "students/student_form.html", context)


def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        student.delete()
        messages.success(request, "Student deleted.")
        return redirect("student_list")
    return render(request, "students/student_confirm_delete.html", {"student": student})


def make_detail_sections(student):
    """Make a list of sections with label/value rows for the details page."""
    sections = []
    filled_count = 0

    for title, field_names in FIELD_GROUPS:
        rows = []
        for name in field_names:
            field = Student._meta.get_field(name)  # gives us the label of the field
            value = getattr(student, name)

            if value is None:
                shown_value = "Not entered"
            else:
                filled_count = filled_count + 1
                if field.choices:
                    # show the text (for example "Single") instead of the code
                    shown_value = getattr(student, "get_" + name + "_display")()
                else:
                    shown_value = value
            rows.append({"label": field.verbose_name, "value": shown_value})
        sections.append({"title": title, "rows": rows})

    return sections, filled_count


def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    sections, filled_count = make_detail_sections(student)
    context = {
        "student": student,
        "sections": sections,
        "filled_count": filled_count,
        "total_fields": len(FEATURE_FIELDS),
    }
    return render(request, "students/student_detail.html", context)


# ---------- Prediction ----------

def make_form_sections(form):
    """Group the form fields into sections for the prediction page."""
    sections = []
    for title, field_names in FIELD_GROUPS:
        fields = []
        for name in field_names:
            fields.append(form[name])
        sections.append({"title": title, "fields": fields})
    return sections


def save_prediction(student, outcome, chances):
    """Store the prediction result in the student record."""
    student.predicted_outcome = outcome
    student.dropout_chance = chances["Dropout"]
    student.enrolled_chance = chances["Enrolled"]
    student.graduate_chance = chances["Graduate"]
    student.predicted_on = timezone.now()
    student.save()


def predict_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        form = PredictionForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save()  # save the 30 values entered in the form
            try:
                outcome, chances = ml_helper.predict_for_student(student)
                save_prediction(student, outcome, chances)
                return redirect("prediction_result", student_id=student.id)
            except Exception as error:
                # for example: model files missing or wrong scikit-learn version
                messages.error(request, "Could not make the prediction: " + str(error))
    else:
        form = PredictionForm(instance=student)

    context = {
        "student": student,
        "form": form,
        "sections": make_form_sections(form),
    }
    return render(request, "students/predict_form.html", context)


def prediction_result(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    # no prediction yet, so go to the form first
    if student.predicted_outcome == "":
        messages.warning(request, "There is no prediction for this student yet.")
        return redirect("predict_student", student_id=student.id)

    context = {
        "student": student,
        "advice": ADVICE[student.predicted_outcome],
        "recommendations": build_recommendations(student),
    }
    return render(request, "students/prediction_result.html", context)


# ---------- Bulk analysis and PDF reports ----------
def bulk_analysis(request):
    results = None
    error = None
    if request.method == "POST":
        uploaded = request.FILES.get("dataset")
        if not uploaded:
            error = "Choose a CSV or Excel file first."
        elif uploaded.size > 10 * 1024 * 1024:
            error = "File is too large. Maximum size is 10 MB."
        else:
            try:
                name = uploaded.name.lower()
                if name.endswith(".csv"):
                    frame = pd.read_csv(uploaded)
                elif name.endswith(".xlsx"):
                    frame = pd.read_excel(uploaded, engine="openpyxl")
                else:
                    raise ValueError("Only CSV and XLSX files are supported.")
                model, columns = ml_helper.load_model()
                missing = [c for c in columns if c not in frame.columns]
                if missing:
                    raise ValueError("Missing required model columns: " + ", ".join(missing))
                if len(frame) == 0:
                    raise ValueError("The uploaded file has no student rows.")
                if len(frame) > 5000:
                    raise ValueError("Maximum 5,000 student rows per upload.")
                data = frame.loc[:, columns].apply(pd.to_numeric, errors="coerce")
                bad_rows = data.isna().any(axis=1)
                valid = data.loc[~bad_rows]
                if valid.empty:
                    raise ValueError("No valid rows. Check missing or non-numeric feature values.")
                predictions = model.predict(valid)
                probabilities = model.predict_proba(valid)
                results = []
                from .ml_helper import COLUMN_TO_FIELD
                for idx, (source_index, row) in enumerate(valid.iterrows()):
                    probs = {str(c): round(float(probabilities[idx][j])*100, 1) for j,c in enumerate(model.classes_)}
                    dropout = probs.get("Dropout", 0)
                    risk = "High" if dropout >= 60 else ("Medium" if dropout >= 30 else "Low")
                    source = frame.loc[source_index]
                    student_id = str(source.get("Student ID", source.get("student_id", f"BULK-{source_index+1}"))).strip()
                    student_name = str(source.get("Student Name", source.get("name", f"Student {source_index+1}"))).strip()
                    if not student_id or student_id.lower() == "nan":
                        student_id = f"BULK-{source_index+1}"
                    if not student_name or student_name.lower() == "nan":
                        student_name = f"Student {source_index+1}"
                    # Save bulk predictions to the same Student table used by the dashboard.
                    feature_values = {COLUMN_TO_FIELD[col]: int(row[col]) if float(row[col]).is_integer() else float(row[col]) for col in columns}
                    student, _created = Student.objects.update_or_create(
                        roll_number=student_id[:30],
                        defaults={"name": student_name[:100], **feature_values},
                    )
                    save_prediction(student, str(predictions[idx]), probs)
                    results.append({"student_id": student_id, "name": student_name, "outcome": str(predictions[idx]), "dropout": dropout, "enrolled": probs.get("Enrolled",0), "graduate": probs.get("Graduate",0), "risk": risk})
                summary = {"total":len(results), "dropout":sum(r["outcome"]=="Dropout" for r in results), "enrolled":sum(r["outcome"]=="Enrolled" for r in results), "graduate":sum(r["outcome"]=="Graduate" for r in results), "high":sum(r["risk"]=="High" for r in results), "medium":sum(r["risk"]=="Medium" for r in results), "low":sum(r["risk"]=="Low" for r in results)}
                summary["dropout_pct"] = round(summary["dropout"]*100/summary["total"],1)
                request.session["bulk_results"] = results
                request.session["bulk_summary"] = summary
                return render(request, "students/bulk_results.html", {"results":results,"summary":summary,"skipped":int(bad_rows.sum())})
            except Exception as exc:
                error = str(exc)
    return render(request, "students/bulk_analysis.html", {"error":error})


def _pdf_response(title, lines, filename):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 55
    pdf.setFillColorRGB(0.12, 0.10, 0.28)
    pdf.setFont("Helvetica-Bold", 20); pdf.drawString(42, y, "StudentAlert")
    y -= 28; pdf.setFont("Helvetica-Bold", 14); pdf.drawString(42, y, title)
    y -= 28; pdf.setStrokeColorRGB(0.55,0.30,0.95); pdf.line(42,y,width-42,y)
    y -= 24; pdf.setFillColorRGB(0.12,0.12,0.18); pdf.setFont("Helvetica", 10)
    for line in lines:
        if y < 55:
            pdf.showPage(); y = height - 55; pdf.setFont("Helvetica",10)
        pdf.drawString(44, y, str(line)[:105]); y -= 17
    pdf.setFont("Helvetica-Oblique",8); pdf.drawString(42,30,"Educational estimate only. This model was trained on Portuguese institutional data and is not validated for Indian colleges.")
    pdf.save(); buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def individual_pdf(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if not student.predicted_outcome:
        messages.warning(request, "Run a prediction before downloading a report.")
        return redirect("predict_student", student_id=student.id)
    lines = [f"Student ID: {student.roll_number}", f"Name: {student.name}", f"Email: {student.email or 'Not provided'}", f"Predicted outcome: {student.predicted_outcome}", f"Dropout probability: {student.dropout_chance}%", f"Enrolled probability: {student.enrolled_chance}%", f"Graduate probability: {student.graduate_chance}%", f"Prediction date: {student.predicted_on}", "", "Suggested action:", ADVICE.get(student.predicted_outcome, "Provide appropriate student support.")]
    for item in build_recommendations(student):
        lines.extend([f"{item['priority']} - {item['title']}", item["reason"], item["action"]])
    return _pdf_response("Individual Student Prediction Report", lines, f"StudentAlert_{student.roll_number}.pdf")


def bulk_pdf(request):
    results = request.session.get("bulk_results")
    summary = request.session.get("bulk_summary")
    if not results or not summary:
        messages.warning(request, "Run a bulk analysis before downloading its report.")
        return redirect("bulk_analysis")
    lines = [f"Students analysed: {summary['total']}", f"Predicted Dropout: {summary['dropout']}", f"Predicted Enrolled: {summary['enrolled']}", f"Predicted Graduate: {summary['graduate']}", f"Predicted dropout share: {summary['dropout_pct']}%", f"High / Medium / Low risk: {summary['high']} / {summary['medium']} / {summary['low']}", "", "STUDENT-LEVEL RESULTS"]
    for r in results:
        lines.append(f"{r['student_id']} | {r['name']} | {r['outcome']} | Dropout {r['dropout']}% | {r['risk']} risk")
    return _pdf_response("Bulk Student Analysis Report", lines, "StudentAlert_Bulk_Report.pdf")


def bulk_csv(request):
    results = request.session.get("bulk_results")
    if not results:
        return redirect("bulk_analysis")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="StudentAlert_Bulk_Results.csv"'
    writer = csv.writer(response); writer.writerow(["Student ID","Name","Predicted Outcome","Dropout %","Enrolled %","Graduate %","Risk"])
    for r in results: writer.writerow([r["student_id"],r["name"],r["outcome"],r["dropout"],r["enrolled"],r["graduate"],r["risk"]])
    return response


def bulk_xlsx(request):
    results = request.session.get("bulk_results")
    if not results:
        return redirect("bulk_analysis")
    output = io.BytesIO()
    pd.DataFrame(results).rename(columns={"student_id":"Student ID","name":"Student Name","outcome":"Predicted Outcome","dropout":"Dropout %","enrolled":"Enrolled %","graduate":"Graduate %","risk":"Risk Level"}).to_excel(output, index=False, engine="openpyxl")
    response = HttpResponse(output.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="StudentAlert_Bulk_Results.xlsx"'
    return response

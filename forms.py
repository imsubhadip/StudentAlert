"""Forms for StudentAlert."""
from django import forms

from .models import Student, ContactMessage
from .ml_helper import COLUMN_TO_FIELD

# The 30 Student fields that the model needs
FEATURE_FIELDS = list(COLUMN_TO_FIELD.values())

# Used to show the 30 fields in small sections on the page
FIELD_GROUPS = [
    ("Personal and family details", [
        "marital_status", "nationality", "gender", "age_at_enrollment",
        "international", "displaced", "special_needs",
        "mother_qualification", "father_qualification",
        "mother_occupation", "father_occupation",
    ]),
    ("Admission details", [
        "application_mode", "application_order", "course", "attendance",
        "previous_qualification", "previous_grade", "admission_grade",
    ]),
    ("Fees and scholarship", [
        "debtor", "tuition_up_to_date", "scholarship_holder",
    ]),
    ("First semester results", [
        "units_credited", "units_enrolled", "units_evaluations",
        "units_approved", "units_grade", "units_without_evaluations",
    ]),
    ("Economic indicators", [
        "unemployment_rate", "inflation_rate", "gdp",
    ]),
]


def add_bootstrap_classes(form):
    """Give every input the Bootstrap style."""
    for field in form.fields.values():
        if isinstance(field.widget, forms.Select):
            field.widget.attrs["class"] = "form-select"
        else:
            field.widget.attrs["class"] = "form-control"


class StudentForm(forms.ModelForm):
    """Used to add and edit the basic details of a student."""

    class Meta:
        model = Student
        fields = ["name", "roll_number", "email", "phone"]
        labels = {"name": "Full name", "roll_number": "Roll number"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)


class PredictionForm(forms.ModelForm):
    """
    The 30 inputs of the model.
    Every field is required, so we never have to guess a missing value.
    """

    class Meta:
        model = Student
        fields = FEATURE_FIELDS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)
        for field in self.fields.values():
            field.required = True


class ContactForm(forms.ModelForm):
    """Contact page form."""

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

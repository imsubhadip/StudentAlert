"""
Database tables for StudentAlert.

Student        - basic details + the 30 inputs of the model + the last prediction
ContactMessage - messages sent from the Contact page

The numbers (codes) in the choices are the same codes used in the UCI dataset
"Predict Students' Dropout and Academic Success", because the model was trained on them.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# ---------- Choices (code, label) ----------

YES_NO_CHOICES = [(1, "Yes"), (0, "No")]

MARITAL_CHOICES = [
    (1, "Single"),
    (2, "Married"),
    (3, "Widower"),
    (4, "Divorced"),
    (5, "Facto union"),
    (6, "Legally separated"),
]

APPLICATION_MODE_CHOICES = [
    (1, "1st phase - general contingent"),
    (2, "Ordinance No. 612/93"),
    (5, "1st phase - special contingent (Azores Island)"),
    (7, "Holders of other higher courses"),
    (10, "Ordinance No. 854-B/99"),
    (15, "International student (bachelor)"),
    (16, "1st phase - special contingent (Madeira Island)"),
    (17, "2nd phase - general contingent"),
    (18, "3rd phase - general contingent"),
    (26, "Ordinance No. 533-A/99, item b2) (Different Plan)"),
    (27, "Ordinance No. 533-A/99, item b3 (Other Institution)"),
    (39, "Over 23 years old"),
    (42, "Transfer"),
    (43, "Change of course"),
    (44, "Technological specialization diploma holders"),
    (51, "Change of institution/course"),
    (53, "Short cycle diploma holders"),
    (57, "Change of institution/course (International)"),
]

# 0 = first choice ... 9 = last choice
APPLICATION_ORDER_CHOICES = []
for number in range(10):
    if number == 0:
        label = "0 (first choice)"
    elif number == 9:
        label = "9 (last choice)"
    else:
        label = str(number)
    APPLICATION_ORDER_CHOICES.append((number, label))

COURSE_CHOICES = [
    (33, "Biofuel Production Technologies"),
    (171, "Animation and Multimedia Design"),
    (8014, "Social Service (evening attendance)"),
    (9003, "Agronomy"),
    (9070, "Communication Design"),
    (9085, "Veterinary Nursing"),
    (9119, "Informatics Engineering"),
    (9130, "Equinculture"),
    (9147, "Management"),
    (9238, "Social Service"),
    (9254, "Tourism"),
    (9500, "Nursing"),
    (9556, "Oral Hygiene"),
    (9670, "Advertising and Marketing Management"),
    (9773, "Journalism and Communication"),
    (9853, "Basic Education"),
    (9991, "Management (evening attendance)"),
]

ATTENDANCE_CHOICES = [(1, "Daytime"), (0, "Evening")]

PREVIOUS_QUALIFICATION_CHOICES = [
    (1, "Secondary education"),
    (2, "Higher education - bachelor's degree"),
    (3, "Higher education - degree"),
    (4, "Higher education - master's"),
    (5, "Higher education - doctorate"),
    (6, "Frequency of higher education"),
    (9, "12th year of schooling - not completed"),
    (10, "11th year of schooling - not completed"),
    (12, "Other - 11th year of schooling"),
    (14, "10th year of schooling"),
    (15, "10th year of schooling - not completed"),
    (19, "Basic education 3rd cycle (9th/10th/11th year) or equiv."),
    (38, "Basic education 2nd cycle (6th/7th/8th year) or equiv."),
    (39, "Technological specialization course"),
    (40, "Higher education - degree (1st cycle)"),
    (42, "Professional higher technical course"),
    (43, "Higher education - master (2nd cycle)"),
]

NATIONALITY_CHOICES = [
    (1, "Portuguese"),
    (2, "German"),
    (6, "Spanish"),
    (11, "Italian"),
    (13, "Dutch"),
    (14, "English"),
    (17, "Lithuanian"),
    (21, "Angolan"),
    (22, "Cape Verdean"),
    (24, "Guinean"),
    (25, "Mozambican"),
    (26, "Santomean"),
    (32, "Turkish"),
    (41, "Brazilian"),
    (62, "Romanian"),
    (100, "Moldova (Republic of)"),
    (101, "Mexican"),
    (103, "Ukrainian"),
    (105, "Russian"),
    (108, "Cuban"),
    (109, "Colombian"),
]

MOTHER_QUALIFICATION_CHOICES = [
    (1, "Secondary Education - 12th Year of Schooling or Eq."),
    (2, "Higher Education - Bachelor's Degree"),
    (3, "Higher Education - Degree"),
    (4, "Higher Education - Master's"),
    (5, "Higher Education - Doctorate"),
    (6, "Frequency of Higher Education"),
    (9, "12th Year of Schooling - Not Completed"),
    (10, "11th Year of Schooling - Not Completed"),
    (11, "7th Year (Old)"),
    (12, "Other - 11th Year of Schooling"),
    (14, "10th Year of Schooling"),
    (18, "General commerce course"),
    (19, "Basic Education 3rd Cycle (9th/10th/11th Year) or Equiv."),
    (22, "Technical-professional course"),
    (26, "7th year of schooling"),
    (27, "2nd cycle of the general high school course"),
    (29, "9th Year of Schooling - Not Completed"),
    (30, "8th year of schooling"),
    (34, "Unknown"),
    (35, "Can't read or write"),
    (36, "Can read without having a 4th year of schooling"),
    (37, "Basic education 1st cycle (4th/5th year) or equiv."),
    (38, "Basic Education 2nd Cycle (6th/7th/8th Year) or Equiv."),
    (39, "Technological specialization course"),
    (40, "Higher education - degree (1st cycle)"),
    (41, "Specialized higher studies course"),
    (42, "Professional higher technical course"),
    (43, "Higher Education - Master (2nd cycle)"),
    (44, "Higher Education - Doctorate (3rd cycle)"),
]

# The father's list is the same as the mother's list plus 5 extra codes
FATHER_QUALIFICATION_CHOICES = MOTHER_QUALIFICATION_CHOICES + [
    (13, "2nd year complementary high school course"),
    (20, "Complementary High School Course"),
    (25, "Complementary High School Course - not concluded"),
    (31, "General Course of Administration and Commerce"),
    (33, "Supplementary Accounting and Administration"),
]
FATHER_QUALIFICATION_CHOICES.sort()

GENDER_CHOICES = [(1, "Male"), (0, "Female")]

OUTCOME_CHOICES = [
    ("Dropout", "Dropout"),
    ("Enrolled", "Enrolled"),
    ("Graduate", "Graduate"),
]

OCCUPATION_HELP = (
    "Enter the numeric occupation code used in the UCI dataset "
    "(for example 0 = Student, 90 = Other situation, 99 = blank)."
)


class Student(models.Model):
    # ----- Basic details -----
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=30, unique=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # ----- The 30 inputs of the model -----
    # They are empty (null) until they are entered in the prediction form.
    # Personal and family details
    marital_status = models.IntegerField(
        "Marital status", choices=MARITAL_CHOICES, null=True, blank=True)
    nationality = models.IntegerField(
        "Nationality", choices=NATIONALITY_CHOICES, null=True, blank=True)
    gender = models.IntegerField(
        "Gender", choices=GENDER_CHOICES, null=True, blank=True)
    age_at_enrollment = models.IntegerField(
        "Age at enrollment", null=True, blank=True,
        validators=[MinValueValidator(15), MaxValueValidator(100)],
        help_text="Age in years (15 to 100).")
    international = models.IntegerField(
        "International student", choices=YES_NO_CHOICES, null=True, blank=True)
    displaced = models.IntegerField(
        "Displaced", choices=YES_NO_CHOICES, null=True, blank=True)
    special_needs = models.IntegerField(
        "Educational special needs", choices=YES_NO_CHOICES, null=True, blank=True)
    mother_qualification = models.IntegerField(
        "Mother's qualification", choices=MOTHER_QUALIFICATION_CHOICES,
        null=True, blank=True)
    father_qualification = models.IntegerField(
        "Father's qualification", choices=FATHER_QUALIFICATION_CHOICES,
        null=True, blank=True)
    mother_occupation = models.IntegerField(
        "Mother's occupation (code)", null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(999)],
        help_text=OCCUPATION_HELP)
    father_occupation = models.IntegerField(
        "Father's occupation (code)", null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(999)],
        help_text=OCCUPATION_HELP)

    # Admission details
    application_mode = models.IntegerField(
        "Application mode", choices=APPLICATION_MODE_CHOICES, null=True, blank=True)
    application_order = models.IntegerField(
        "Application order", choices=APPLICATION_ORDER_CHOICES, null=True, blank=True)
    course = models.IntegerField(
        "Course", choices=COURSE_CHOICES, null=True, blank=True)
    attendance = models.IntegerField(
        "Daytime/evening attendance", choices=ATTENDANCE_CHOICES,
        null=True, blank=True)
    previous_qualification = models.IntegerField(
        "Previous qualification", choices=PREVIOUS_QUALIFICATION_CHOICES,
        null=True, blank=True)
    previous_grade = models.FloatField(
        "Previous qualification (grade)", null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(200)],
        help_text="Between 0 and 200.")
    admission_grade = models.FloatField(
        "Admission grade", null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(200)],
        help_text="Between 0 and 200.")

    # Money matters
    debtor = models.IntegerField(
        "Debtor", choices=YES_NO_CHOICES, null=True, blank=True)
    tuition_up_to_date = models.IntegerField(
        "Tuition fees up to date", choices=YES_NO_CHOICES, null=True, blank=True)
    scholarship_holder = models.IntegerField(
        "Scholarship holder", choices=YES_NO_CHOICES, null=True, blank=True)

    # First semester results (second semester is NOT used by the model)
    units_credited = models.IntegerField(
        "1st sem units credited", null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(60)])
    units_enrolled = models.IntegerField(
        "1st sem units enrolled", null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(60)])
    units_evaluations = models.IntegerField(
        "1st sem units evaluations", null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(60)])
    units_approved = models.IntegerField(
        "1st sem units approved", null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(60)])
    units_grade = models.FloatField(
        "1st sem grade (average)", null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        help_text="Average grade of the first semester (0 to 20).")
    units_without_evaluations = models.IntegerField(
        "1st sem units without evaluations", null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(60)])

    # Economic indicators (percentages) for the enrollment year
    unemployment_rate = models.FloatField(
        "Unemployment rate (%)", null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)])
    inflation_rate = models.FloatField(
        "Inflation rate (%)", null=True, blank=True,
        validators=[MinValueValidator(-50), MaxValueValidator(100)])
    gdp = models.FloatField(
        "GDP", null=True, blank=True,
        validators=[MinValueValidator(-100), MaxValueValidator(100)],
        help_text="GDP value for the enrollment year, as used in the dataset.")

    # ----- Last prediction (empty until a prediction is made) -----
    predicted_outcome = models.CharField(
        max_length=10, choices=OUTCOME_CHOICES, blank=True)
    dropout_chance = models.FloatField(null=True, blank=True)
    enrolled_chance = models.FloatField(null=True, blank=True)
    graduate_chance = models.FloatField(null=True, blank=True)
    predicted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name + " - " + self.email

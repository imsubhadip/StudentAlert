# Initial schema for StudentAlert.
from django.db import migrations, models
from django.core import validators
from students import models as student_models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Student",
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('roll_number', models.CharField(max_length=30, unique=True)),
                ('email', models.EmailField(blank=True)),
                ('phone', models.CharField(max_length=15, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('marital_status', models.IntegerField('Marital status', choices=student_models.MARITAL_CHOICES, null=True, blank=True)),
                ('nationality', models.IntegerField('Nationality', choices=student_models.NATIONALITY_CHOICES, null=True, blank=True)),
                ('gender', models.IntegerField('Gender', choices=student_models.GENDER_CHOICES, null=True, blank=True)),
                ('age_at_enrollment', models.IntegerField('Age at enrollment', null=True, blank=True, validators=[validators.MinValueValidator(15), validators.MaxValueValidator(100)], help_text='Age in years (15 to 100).')),
                ('international', models.IntegerField('International student', choices=student_models.YES_NO_CHOICES, null=True, blank=True)),
                ('displaced', models.IntegerField('Displaced', choices=student_models.YES_NO_CHOICES, null=True, blank=True)),
                ('special_needs', models.IntegerField('Educational special needs', choices=student_models.YES_NO_CHOICES, null=True, blank=True)),
                ('mother_qualification', models.IntegerField("Mother's qualification", choices=student_models.MOTHER_QUALIFICATION_CHOICES, null=True, blank=True)),
                ('father_qualification', models.IntegerField("Father's qualification", choices=student_models.FATHER_QUALIFICATION_CHOICES, null=True, blank=True)),
                ('mother_occupation', models.IntegerField("Mother's occupation (code)", null=True, blank=True, validators=[validators.MinValueValidator(0), validators.MaxValueValidator(999)], help_text=student_models.OCCUPATION_HELP)),
                ('father_occupation', models.IntegerField("Father's occupation (code)", null=True, blank=True, validators=[validators.MinValueValidator(0), validators.MaxValueValidator(999)], help_text=student_models.OCCUPATION_HELP)),
                ('application_mode', models.IntegerField('Application mode', choices=student_models.APPLICATION_MODE_CHOICES, null=True, blank=True)),
                ('application_order', models.IntegerField('Application order', choices=student_models.APPLICATION_ORDER_CHOICES, null=True, blank=True)),
                ('course', models.IntegerField('Course', choices=student_models.COURSE_CHOICES, null=True, blank=True)),
                ('attendance', models.IntegerField('Daytime/evening attendance', choices=student_models.ATTENDANCE_CHOICES, null=True, blank=True)),
                ('previous_qualification', models.IntegerField('Previous qualification', choices=student_models.PREVIOUS_QUALIFICATION_CHOICES, null=True, blank=True)),
                ('previous_grade', models.FloatField('Previous qualification (grade)', null=True, blank=True, validators=[validators.MinValueValidator(0), validators.MaxValueValidator(200)], help_text='Between 0 and 200.')),
                ('admission_grade', models.FloatField('Admission grade', null=True, blank=True, validators=[validators.MinValueValidator(0), validators.MaxValueValidator(200)], help_text='Between 0 and 200.')),
                ('debtor', models.IntegerField('Debtor', choices=student_models.YES_NO_CHOICES, null=True, blank=True)),
                ('tuition_up_to_date', models.IntegerField('Tuition fees up to date', choices=student_models.YES_NO_CHOICES, null=True, blank=True)),
                ('scholarship_holder', models.IntegerField('Scholarship holder', choices=student_models.YES_NO_CHOICES, null=True, blank=True)),
                ('units_credited', models.IntegerField('1st sem units credited', null=True, blank=True, validators=[validators.MinValueValidator(0), validators.MaxValueValidator(60)])),
                ('units_enrolled', models.IntegerField('1st sem units enrolled', null=True, blank=True, validators=[validators.MinValueValidator(0), validators.MaxValueValidator(60)])),
                ('units_evaluations', models.IntegerField('1st sem units evaluations', null=True, blank=True, validators=[validators.MinValueValidator(0), validators.MaxValueValidator(60)])),
                ('units_approved', models.IntegerField('1st sem units approved', null=True, blank=True, validators=[validators.MinValueValidator(0), validators.MaxValueValidator(60)])),
                ('units_grade', models.FloatField('1st sem grade (average)', null=True, blank=True, validators=[validators.MinValueValidator(0), validators.MaxValueValidator(20)], help_text='Average grade of the first semester (0 to 20).')),
                ('units_without_evaluations', models.IntegerField('1st sem units without evaluations', null=True, blank=True, validators=[validators.MinValueValidator(0), validators.MaxValueValidator(60)])),
                ('unemployment_rate', models.FloatField('Unemployment rate (%)', null=True, blank=True, validators=[validators.MinValueValidator(0), validators.MaxValueValidator(100)])),
                ('inflation_rate', models.FloatField('Inflation rate (%)', null=True, blank=True, validators=[validators.MinValueValidator(-50), validators.MaxValueValidator(100)])),
                ('gdp', models.FloatField('GDP', null=True, blank=True, validators=[validators.MinValueValidator(-100), validators.MaxValueValidator(100)], help_text='GDP value for the enrollment year, as used in the dataset.')),
                ('predicted_outcome', models.CharField(max_length=10, choices=student_models.OUTCOME_CHOICES, blank=True)),
                ('dropout_chance', models.FloatField(null=True, blank=True)),
                ('enrolled_chance', models.FloatField(null=True, blank=True)),
                ('graduate_chance', models.FloatField(null=True, blank=True)),
                ('predicted_on', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="ContactMessage",
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField()),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]

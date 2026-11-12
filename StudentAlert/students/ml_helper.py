"""
Machine learning helper for StudentAlert.

This file loads the trained Random Forest model (made in Google Colab)
and uses it to predict: Dropout, Enrolled or Graduate.
It does not use Django, so it is easy to test on its own.
"""
import os

import joblib
import pandas as pd

# The two model files are kept in the "ml_model" folder
PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_FILE = os.path.join(PROJECT_FOLDER, "ml_model", "dropout_model.joblib")
COLUMNS_FILE = os.path.join(PROJECT_FOLDER, "ml_model", "model_columns.joblib")

# The exact column name used in the notebook  ->  our Student model field name
# (some column names have spaces or an apostrophe, so we map them here)
COLUMN_TO_FIELD = {
    "Marital status": "marital_status",
    "Application mode": "application_mode",
    "Application order": "application_order",
    "Course": "course",
    "Daytime/evening attendance": "attendance",
    "Previous qualification": "previous_qualification",
    "Previous qualification (grade)": "previous_grade",
    "Nacionality": "nationality",  # spelled like this in the dataset
    "Mother's qualification": "mother_qualification",
    "Father's qualification": "father_qualification",
    "Mother's occupation": "mother_occupation",
    "Father's occupation": "father_occupation",
    "Admission grade": "admission_grade",
    "Displaced": "displaced",
    "Educational special needs": "special_needs",
    "Debtor": "debtor",
    "Tuition fees up to date": "tuition_up_to_date",
    "Gender": "gender",
    "Scholarship holder": "scholarship_holder",
    "Age at enrollment": "age_at_enrollment",
    "International": "international",
    "Curricular units 1st sem (credited)": "units_credited",
    "Curricular units 1st sem (enrolled)": "units_enrolled",
    "Curricular units 1st sem (evaluations)": "units_evaluations",
    "Curricular units 1st sem (approved)": "units_approved",
    "Curricular units 1st sem (grade)": "units_grade",
    "Curricular units 1st sem (without evaluations)": "units_without_evaluations",
    "Unemployment rate": "unemployment_rate",
    "Inflation rate": "inflation_rate",
    "GDP": "gdp",
}

# The model is loaded only once and then reused
model = None
columns = None


def load_model():
    """Load the model and the column names from the .joblib files."""
    global model, columns

    if model is None:
        if not os.path.exists(MODEL_FILE) or not os.path.exists(COLUMNS_FILE):
            raise FileNotFoundError(
                "Model files not found. Put dropout_model.joblib and "
                "model_columns.joblib inside the ml_model folder."
            )
        loaded_model = joblib.load(MODEL_FILE)
        loaded_columns = joblib.load(COLUMNS_FILE)

        # Safety check: the saved columns must match the columns the model learned
        if list(loaded_model.feature_names_in_) != list(loaded_columns):
            raise ValueError(
                "model_columns.joblib does not match dropout_model.joblib. "
                "Please save both files from the same notebook run."
            )
        model = loaded_model
        columns = loaded_columns

    return model, columns


def make_row(student, column_names):
    """Collect the student's values in exactly the same order as training."""
    row = {}
    missing = []

    for column in column_names:
        if column not in COLUMN_TO_FIELD:
            raise ValueError("Unknown model column: " + column)

        field_name = COLUMN_TO_FIELD[column]
        value = getattr(student, field_name)

        # 0 is a valid answer (for example "No"), so we only check for None
        if value is None:
            missing.append(column)
        row[column] = value

    # We never guess a missing value
    if len(missing) > 0:
        raise ValueError("These values are missing: " + ", ".join(missing))

    return row


def predict_for_student(student):
    """
    Predict the outcome for one student.
    Returns the predicted outcome and a dictionary of chances in percent.
    """
    loaded_model, column_names = load_model()

    row = make_row(student, column_names)
    data = pd.DataFrame([row], columns=column_names)

    outcome = loaded_model.predict(data)[0]
    probabilities = loaded_model.predict_proba(data)[0]

    # Match each probability with its class name (Dropout, Enrolled, Graduate)
    chances = {}
    for index in range(len(loaded_model.classes_)):
        class_name = loaded_model.classes_[index]
        chances[class_name] = round(float(probabilities[index]) * 100, 1)

    return str(outcome), chances

# StudentAlert - Student Dropout Early Warning System

**Project 18 | Django | Machine Learning**

StudentAlert is a Django web application that helps a college find students who may need extra
support. A Random Forest model (trained in Google Colab on the UCI *Predict Students' Dropout and
Academic Success* dataset) predicts one of three outcomes for a student:

- **Dropout**
- **Enrolled**
- **Graduate**

> Predictions are **estimates**, not certain outcomes. Use them only to offer extra help to students.

---

## 1. Features

| Page | What it does |
|------|--------------|
| Home | Short introduction to the project |
| Dashboard | Total students, Dropout / Graduate / Enrolled prediction counts, doughnut chart, recent students |
| Student list | All students, search (name, roll number, email), 10 students per page |
| Add / Edit student | Save the basic details of a student |
| Student details | Basic details, saved model inputs, latest prediction |
| Prediction form | The 30 inputs of the model (all required, nothing is guessed) |
| Prediction result | Predicted outcome, chance of each outcome, explanation that it is only an estimate |
| About | Project, model and limitations |
| Contact | Messages are saved in the database (read them in the admin site) |

Delete student is done from the student list or details page (with a confirmation page).

---

## 2. Folder structure

```
StudentAlert/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── ml_model/
│   ├── dropout_model.joblib        <- trained Random Forest model
│   └── model_columns.joblib        <- the 30 column names in training order
├── student_system/                 <- project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── students/                       <- our app
│   ├── models.py                   <- database tables
│   ├── forms.py                    <- forms
│   ├── views.py                    <- page logic
│   ├── urls.py                     <- page addresses
│   ├── admin.py                    <- admin site setup
│   ├── ml_helper.py                <- loads the model and makes predictions
│   ├── migrations/
│   └── templates/students/         <- HTML pages
└── static/
    ├── css/style.css
    └── js/main.js
```

`ml_helper.py` is a separate small file so that `views.py` stays short and the machine learning
code can be explained (and tested) on its own.

---

## 3. The two model files (important)

Both files must be inside the **`ml_model`** folder:

- `dropout_model.joblib`
- `model_columns.joblib`

**What is already included:** `dropout_model.joblib` is your uploaded model. The file
`model_columns.joblib` was **not** uploaded, so it was re-created from the feature names stored
inside the model itself (`model.feature_names_in_`). These are the same 30 names, in the same order,
that your notebook saves with `joblib.dump(list(X.columns), "model_columns.joblib")`.

If you want, replace it with the file you downloaded from Colab. The app checks at the first
prediction that the column file matches the model, and shows a clear error if it does not.

**scikit-learn version:** the model was saved with scikit-learn **1.6.1**, so `requirements.txt`
installs exactly that version. Using a different version may show a warning or break the model.

**The 30 inputs** (in training order): Marital status, Application mode, Application order, Course,
Daytime/evening attendance, Previous qualification, Previous qualification (grade), Nacionality,
Mother's qualification, Father's qualification, Mother's occupation, Father's occupation,
Admission grade, Displaced, Educational special needs, Debtor, Tuition fees up to date, Gender,
Scholarship holder, Age at enrollment, International, and the six first-semester curricular unit
values (credited, enrolled, evaluations, approved, grade, without evaluations), Unemployment rate,
Inflation rate and GDP.

Notes about the form:

- Dropdown options use the same numeric codes as the UCI dataset (the labels come from the dataset page).
- *Mother's occupation* and *Father's occupation* are typed as **numeric codes**, because the model was
  trained on those codes. See the dataset page: https://archive.ics.uci.edu/dataset/697
- All fields are required. If a value is not known, the prediction is not made. The program never
  fills in a missing value with a guess.

---

## 4. Installation on Windows

### Step 1: Install Python
1. Download Python **3.10, 3.11, 3.12 or 3.13** from https://www.python.org/downloads/
2. During installation, tick **"Add python.exe to PATH"**.
3. Check it in Command Prompt or PowerShell:
   ```
   python --version
   ```

### Step 2: Open the project folder
```
cd path\to\StudentAlert
```

### Step 3: Create and activate a virtual environment
```
python -m venv venv
venv\Scripts\activate
```
You should now see `(venv)` at the start of the line.

If PowerShell says *"running scripts is disabled"*, run this once and try again:
```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Step 4: Install the packages
```
pip install -r requirements.txt
```

### Step 5: Create the database
```
python manage.py makemigrations students
python manage.py migrate
```
`makemigrations` reads `models.py` and prepares the table definitions. `migrate` creates the SQLite
database file `db.sqlite3`.

### Step 6: Optional Django admin account
```
python manage.py createsuperuser
```
Enter a username and password. You will use them on the Login page.

### Step 7: Run the server
```
python manage.py runserver
```
Open http://127.0.0.1:8000/ in your browser.

- Website: http://127.0.0.1:8000/
- Admin site (view contact messages, edit data): http://127.0.0.1:8000/admin/

The pages need an internet connection for Bootstrap, Chart.js and the Google font (they are loaded
from a CDN).

---

## 5. How to use the app

1. Log in.
2. Click **Add student** and save the name and roll number.
3. Open the student and click **Enter details and predict**.
4. Fill all 30 fields and click **Predict outcome**.
5. Read the result page. The student's prediction is also counted on the **Dashboard**.

To test with real values, take a row from your dataset (for example, in Colab run
`X_test.iloc[0]`) and type its values into the form.

Each student keeps **one latest prediction**. Predicting again replaces the earlier result.

---

## 6. How the code works (for the viva)

1. **models.py** - `Student` has the basic details, the 30 model inputs (empty until entered) and
   the latest prediction. `ContactMessage` stores contact messages.
2. **forms.py** - `StudentForm` (basic details), `PredictionForm` (the 30 inputs, all required) and
   `ContactForm`.
3. **ml_helper.py**
   - `load_model()` loads both joblib files once and checks the columns match the model.
   - `make_row()` takes the student's values in the **same order as `model_columns.joblib`** and
     refuses to continue if any value is missing.
   - `predict_for_student()` builds a one-row Pandas table, calls `predict()` and `predict_proba()`,
     and returns the outcome and the chances in percent.
4. **views.py** - `predict_student` checks the form, saves the 30 values, calls the helper, saves the
   result in the student record and redirects to the result page.
5. **Dashboard** - counts students by `predicted_outcome` with the Django ORM; `main.js` draws the
   Chart.js doughnut from the numbers in the page.
6. **Access** - the main website pages (dashboard, students, and predictions) are available without
   logging in for a simple college demonstration. The separate Django admin site remains protected
   by its administrator login. Do not deploy this public, login-free version with real student data;
   anyone who can reach the site can view, add, edit, or delete student records. All forms use
   `{% csrf_token %}`.

**Why Random Forest?** It works with number codes and mixed columns, needs no scaling and was
compared with Logistic Regression and a Decision Tree in the notebook.

**Known limitations (also shown on the About page):** the model was trained on data from one
Portuguese institution; it can miss real dropouts and can give false alarms; "Enrolled" means the
student had not finished by the normal end of the course; some inputs are personal information.
The accuracy, precision, recall and F1-score are in your Colab notebook. This project does not
repeat them, so no number is invented here.

---

## 7. Upload to GitHub

1. Install Git: https://git-scm.com/download/win
2. Create an empty repository on https://github.com (for example `StudentAlert`). Do not add a README there.
3. In the project folder:
   ```
   git init
   git add .
   git commit -m "StudentAlert: Student Dropout Early Warning System"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/StudentAlert.git
   git push -u origin main
   ```
4. `.gitignore` already keeps `venv/`, `db.sqlite3` and `__pycache__/` out of GitHub.
   The model files (about 3.6 MB) are small enough to upload normally.
5. Tip: run `python manage.py makemigrations students` before your first commit, so the
   `students/migrations/0001_initial.py` file is uploaded too.

---

## 8. Deploy on PythonAnywhere

1. Create a free account at https://www.pythonanywhere.com
2. Open a **Bash console** and download your project:
   ```
   git clone https://github.com/YOUR-USERNAME/StudentAlert.git
   cd StudentAlert
   ```
3. Create a virtual environment with Python 3.10 or higher (use the newest one PythonAnywhere offers):
   ```
   mkvirtualenv studentalert --python=/usr/bin/python3.12
   pip install -r requirements.txt
   ```
   (Change `python3.12` if that version is not available.) The free plan has limited disk space,
   and scikit-learn + pandas are large, so this step can be tight.
4. Prepare the project:
   ```
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic
   ```
5. Go to the **Web** tab, click **Add a new web app**, choose **Manual configuration** and the same Python version.
6. On the Web tab set:
   - **Source code:** `/home/YOUR-USERNAME/StudentAlert`
   - **Working directory:** `/home/YOUR-USERNAME/StudentAlert`
   - **Virtualenv:** `/home/YOUR-USERNAME/.virtualenvs/studentalert`
   - **Static files:** URL `/static/` -> Directory `/home/YOUR-USERNAME/StudentAlert/staticfiles`
7. Click the **WSGI configuration file** link, delete its content and paste:
   ```python
   import os
   import sys

   path = "/home/YOUR-USERNAME/StudentAlert"
   if path not in sys.path:
       sys.path.append(path)

   os.environ["DJANGO_SETTINGS_MODULE"] = "student_system.settings"
   os.environ["DJANGO_SECRET_KEY"] = "put-a-long-random-text-here"
   os.environ["DJANGO_DEBUG"] = "False"

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
8. Click the green **Reload** button. Your site is at `https://YOUR-USERNAME.pythonanywhere.com`.

`ALLOWED_HOSTS` in `settings.py` already allows `.pythonanywhere.com`.

---

## 9. Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named django` | Activate the virtual environment: `venv\Scripts\activate`, then `pip install -r requirements.txt` |
| "Model files not found" on the prediction page | Put both `.joblib` files inside the `ml_model` folder |
| `InconsistentVersionWarning` from scikit-learn | Install the same version as training: `pip install scikit-learn==1.6.1` |
| "model_columns.joblib does not match dropout_model.joblib" | Save both files from the same notebook run |
| Page looks unstyled | Check your internet connection (Bootstrap is loaded from a CDN). On PythonAnywhere, check the static files mapping and run `collectstatic` |
| `no such table: students_student` | Run `python manage.py makemigrations students` and then `python manage.py migrate` |
| Port already in use | `python manage.py runserver 8080` |

## Bulk student analysis

Open **Bulk Analysis** from the sidebar and upload a CSV or XLSX file. The file must contain all 30 model input columns using the exact training-dataset column names. Optional metadata columns are `Student ID` and `Student Name`. Rows with missing or non-numeric model inputs are skipped and counted. A results page provides student-level outcomes and probabilities, plus PDF and CSV exports.

The bulk feature accepts up to 5,000 rows and a 10 MB file. Install dependencies with `pip install -r requirements.txt` (including `openpyxl` and `reportlab`).

## Responsible-use limitation

The bundled model was trained using data from a Portuguese higher-education institution. It has not been validated for Indian colleges. Its `predict_proba` outputs are model scores, not guaranteed or necessarily calibrated real-world probabilities. Use the tool only as an educational demonstration and to support human review; do not use it to deny admission, scholarships, progression, or other opportunities.
gunicorn==23.0.0

# Django PDF Upload to Google Drive

A simple Django project that provides a web form to generate a PDF file and automatically uploads it to a specific Google Drive folder using a Google Service Account.

---

## How It Works

1. HTML form in Django
2. PDF generation using ReportLab
3. Upload to Google Drive via Service Account
4. Files are saved into a shared Drive folder and instantly visible

---

## Requirements

- Python 3.11+
- A Google Cloud Platform (GCP) project with the Drive API enabled
- A Google Service Account with a downloaded JSON key file
- Editor access for the Service Account on the target Google Drive folder

---

## Setup

### 1. Create Django project

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install django
django-admin startproject googledrivepdfupload
cd googledrivepdfupload
python manage.py startapp googleuploader
```

### 2. Install dependencies

```bash
pip install reportlab google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib
```

---

## Configuration

### 1. Adjust `settings.py`

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Path to your Service Account key (do NOT commit this file)
GDRIVE_CREDENTIALS = os.path.join(BASE_DIR, 'googledrivepdfupload', 'service_account.json')

# Google Drive folder ID (create folder and share it with your Service Account)
GDRIVE_PARENT_ID = "XXXXXXXXXX" #https://drive.google.com/drive/folders/XXXXXXXXXX
```

### 2. Update `.gitignore`

```
*.json
*.pem
*.key
__pycache__/
.env
*.sqlite3
googledrivepdfupload/service_account.json
```

---

## Google Cloud Setup

1. Create a GCP project
2. Enable Google Drive API:
   https://console.developers.google.com/apis/library/drive.googleapis.com
3. Create a Service Account:
   https://console.cloud.google.com/iam-admin/serviceaccounts
4. Generate and download a JSON key file
5. Create a folder in Google Drive
6. Share the folder with the Service Account (Editor access)

---

## Usage

### 1. Start the development server

```bash
python manage.py migrate
python manage.py runserver
```

### 2. Open the form

Visit: http://127.0.0.1:8000/

### 3. Upload a PDF

- Enter a title
- Submit the form
- A folder will be created in Google Drive with the PDF inside

---

## Project Structure

```
googledrivepdfupload/
├── core/
│   ├── views.py
│   ├── gdrive.py        # Google Drive logic
│   └── templates/
│       └── googleuploader/
│           └── form.html
├── googledrivepdfupload/
│   ├── settings.py
│   └── urls.py
├── service_account.json  # DO NOT commit this!
└── manage.py
```

---

## Result

- Local PDF generation from a Django form
- Automatic upload to Google Drive
- Files are immediately accessible in your own Drive account

---

## Security Tips

- Never commit your JSON key to version control
- Only give folder access to trusted service accounts
- Use login protection for the upload form if necessary

---

## Optional Next Steps

- Display a link to the uploaded file in the UI
- Improve UI with Bootstrap
- Add form validation, CSRF protection, or login
- Use Celery for background uploads

---

## requirements.txt (pip freeze)

These packages were installed in the virtual environment:


```bash
pip freeze > requirements.txt
```

Then install dependencies with:

```bash
pip install -r requirements.txt
```

---

## License

This project currently has no license. Contact the author before reuse.

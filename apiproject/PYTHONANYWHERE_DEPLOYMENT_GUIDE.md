# 🚀 Complete PythonAnywhere Deployment Guide for Aura SIS

This step-by-step guide walks you through deploying the **Aura SIS** platform on **PythonAnywhere** from start to finish.

---

## 📋 Overview of Files Included for PythonAnywhere
- `requirements.txt` &mdash; Clean, pinned production dependencies.
- `wsgi_pythonanywhere.py` &mdash; Ready-to-copy WSGI configuration for the PythonAnywhere Web Tab.
- `deploy_pythonanywhere.sh` &mdash; One-command bash script for setting up the virtualenv, installing dependencies, applying migrations, and collecting static files.
- `apiproject/settings.py` &mdash; Pre-configured with `.pythonanywhere.com` allowed hosts, trusted CSRF origins, and WhiteNoise static asset compression.

---

## ⚡ Quick 5-Minute Deployment Steps

### Step 1: Open PythonAnywhere & Start a Bash Console
1. Log in to your [PythonAnywhere Dashboard](https://www.pythonanywhere.com/).
2. On your **Consoles** tab, click **Bash** under "Start a new console".

---

### Step 2: Clone or Upload Your Code
In your PythonAnywhere Bash console, clone your project repository:
```bash
cd ~
git clone <YOUR_GIT_REPO_URL> apiproject
cd ~/apiproject
```
*(If you are uploading files directly via ZIP or the PythonAnywhere Files tab, upload and extract them into `/home/<username>/apiproject`)*

---

### Step 3: Run the Automated Deployment Script
Run the included deployment script:
```bash
bash deploy_pythonanywhere.sh
```
This script automatically:
1. Creates a Python virtual environment in `~/.virtualenvs/apienv`
2. Installs all packages from `requirements.txt`
3. Applies database migrations (`python manage.py migrate`)
4. Generates static assets (`python manage.py collectstatic --noinput`)
5. Seeds initial course programs and student profiles (`python manage.py seed_data`)

> **Optional**: To create an admin account for the Django admin portal (`/admin/`):
> ```bash
> python manage.py createsuperuser
> ```

---

### Step 4: Configure the Web App in the PythonAnywhere Dashboard
1. Go to the **Web** tab in your PythonAnywhere dashboard: `https://www.pythonanywhere.com/user/<username>/webapps/`
2. Click **"Add a new web app"**.
3. Choose your domain name (e.g. `<username>.pythonanywhere.com`).
4. When asked for the framework, select **"Manual configuration"** (NOT Django, because you have an existing pre-configured Django project).
5. Select **Python 3.12** (or Python 3.11/3.10).
6. Click **Next** to finish creating the web app shell.

---

### Step 5: Configure Paths in the Web Tab

Scroll down the **Web** tab to set the following sections:

#### A. Code Section:
- **Source code**: `/home/<username>/apiproject`
- **Working directory**: `/home/<username>/apiproject`

#### B. Virtualenv Section:
- Click on the path link and enter:
  ```
  /home/<username>/.virtualenvs/apienv
  ```
  *(PythonAnywhere will confirm the virtualenv exists)*

#### C. WSGI Configuration File:
1. Click on the link next to **WSGI configuration file** (e.g. `/var/www/<username>_pythonanywhere_com_wsgi.py`).
2. Delete everything currently inside that file.
3. Open `wsgi_pythonanywhere.py` from this repository (or copy the block below):
```python
import os
import sys

# Replace with your actual PythonAnywhere username
USERNAME = '<username>'
PROJECT_PATH = f'/home/{USERNAME}/apiproject'

if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

os.environ['DJANGO_SETTINGS_MODULE'] = 'apiproject.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```
4. Replace `<username>` with your actual PythonAnywhere username.
5. Click the green **Save** button in the top right.

#### D. Static Files Mapping:
Scroll to the **Static files** section and add the following mapping:
- **URL**: `/static/`
- **Directory**: `/home/<username>/apiproject/staticfiles`

---

### Step 6: Reload Your Web App
1. Scroll to the top of the **Web** tab.
2. Click the large green button: **"Reload <username>.pythonanywhere.com"**.
3. Open your live website:
   ```
   https://<username>.pythonanywhere.com/
   ```

---

## 🔍 Verification Checklist

| Check | Expected Result |
|---|---|
| Dashboard | Executive dashboard loads with glowing cosmic aurora theme & animated counters |
| Student Directory | `/getall/` loads all students with filtering, search, and CSV export |
| Course Programs | `/getcourse/` lists curriculum programs and tuition statistics |
| REST Sandbox & SDK | `/api-docs/` allows testing endpoints live and generating cURL/JS/Python snippets |
| Admin Panel | `/admin/` loads Django administration login screen |
| Static Files | CSS styling, fonts, and Chart.js render crisp without missing file errors |

---

## 🛠️ Updating the Live Site in the Future
Whenever you push updates to GitHub, simply run this in your PythonAnywhere Bash console:
```bash
cd ~/apiproject
git pull
source ~/.virtualenvs/apienv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```
Then click **Reload** on the Web tab!


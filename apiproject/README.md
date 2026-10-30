# Aura SIS &mdash; Enterprise Student & Course Management Cloud Platform

[![PythonAnywhere Ready](https://img.shields.io/badge/PythonAnywhere-Deploy_Ready-blue?style=for-the-badge&logo=pythonanywhere&logoColor=white)](https://www.pythonanywhere.com/)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/Django_REST_Framework-3.18-red?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![WhiteNoise](https://img.shields.io/badge/WhiteNoise-6.12-blue?style=for-the-badge)](http://whitenoise.evans.io/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)

An enterprise-ready, production-hardened full-stack Student Information System (SIS) and REST Gateway. Built with **Django 6.0** and **Django REST Framework (DRF)** on the backend, styled with an executive **Cosmic Aurora** glassmorphic interface, smooth entrance & counter animations, real-time Chart.js telemetry, and an in-app multi-language developer SDK generator (cURL, Python, JavaScript).

---

## 🌟 Key Features

- **Executive Cloud Dashboard**: Real-time KPI telemetry with animated counter tickers (Active Students, Course Tracks, Tuition Pipeline in ₹, Median Student Demographics).
- **Modern "Cosmic Aurora & Cyber Slate" Theme**: Deep obsidian canvas with atmospheric animated glowing orbs, frosted glass panels (`backdrop-blur-2xl`), and radiant violet-cyan gradient accents.
- **Micro-Interactions & Fluid Animations**:
  - Cascading staggered entrance animations on all pages (`.animate-fade-in`, delays).
  - Smooth animated number counters on metric stat cards.
  - Interactive card lifts with luminous gradient glow borders on hover.
  - Non-blocking copy-to-clipboard feedback tooltips.
  - Shimmer sheen on primary call-to-action buttons.
  - Live radar pulse badges for system health and PythonAnywhere readiness.
- **Comprehensive Academic Operations**:
  - Full CRUD for student profiles (Enroll, View Dossier, Edit, Delete).
  - Full CRUD for academic curriculum programs (Add track, View syllabus details, Edit, Delete).
- **Search, Filtering & CSV Data Export**: Instant search across student names, emails, phones, and cities, plus one-click CSV report export.
- **Developer REST Console & SDK Generator**:
  - Test endpoints live against the Django REST engine with real-time latency measurement and status badge feedback.
  - Auto-generated copy-ready snippets in **cURL**, **Python (Requests)**, and **JavaScript (Fetch)**.
- **PythonAnywhere Turnkey Deployment**:
  - Complete with `requirements.txt`, `wsgi_pythonanywhere.py`, `deploy_pythonanywhere.sh`, and `PYTHONANYWHERE_DEPLOYMENT_GUIDE.md`.
  - Also compatible with Render, Railway, Vercel, and Gunicorn cloud hosts.
- **Automated Test Suite**: 11 comprehensive unit and integration test cases (**11/11 passing**).

---

## 🚀 PythonAnywhere 1-Click Deployment

For complete step-by-step instructions with dashboard settings, see **[PYTHONANYWHERE_DEPLOYMENT_GUIDE.md](PYTHONANYWHERE_DEPLOYMENT_GUIDE.md)**.

### Quick Setup in PythonAnywhere Bash Console:
```bash
# 1. Clone repository
cd ~
git clone <YOUR_GIT_REPO_URL> apiproject
cd ~/apiproject

# 2. Run the automated deployment script
bash deploy_pythonanywhere.sh
```

### Configure in PythonAnywhere Web Tab:
1. **Source & Working directory**: `/home/<username>/apiproject`
2. **Virtualenv**: `/home/<username>/.virtualenvs/apienv`
3. **WSGI configuration file**: Copy contents of `wsgi_pythonanywhere.py` (replace `<username>`)
4. **Static files**: URL `/static/` &rarr; Directory `/home/<username>/apiproject/staticfiles`
5. Click **Reload <username>.pythonanywhere.com**!

---

## 💻 Local Setup & Quickstart

### 1. Clone & Enter Directory
```bash
git clone <your-repo-url>
cd apiproject
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations, Collect Static & Seed Sample Data
```bash
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py seed_data
```

### 5. Launch Development Server
```bash
python manage.py runserver
```
Open **`http://127.0.0.1:8000/`** in your browser.

---

## 📡 REST API Specification

| Method | Endpoint | Description | Query / Request Payload |
|---|---|---|---|
| `GET` | `/` | Executive Management Web Dashboard | None |
| `GET` | `/getall/` | Retrieve all active students with course details | `?search=<term>&course=<id>` |
| `GET` | `/getid/<id>/` | Retrieve a single student by Primary Key | None |
| `POST` | `/addstudent/` | Enroll a new student record | `{ full_name, email, phone, age, gender, city, address, course }` |
| `PUT` | `/updateid/<id>/` | Update an existing student | `{ full_name, email, ... }` |
| `DELETE` | `/deleteid/<id>/` | Delete a student record permanently | None |
| `GET` | `/getcourse/` | Retrieve all course programs with enrollment stats | None |
| `GET` | `/getcourseid/<id>/` | Retrieve a single course program | None |
| `POST` | `/addcourse/` | Create a new course track | `{ course_name, course_fees, course_duration }` |
| `PUT` | `/updatecourse/<id>/` | Update course name, tuition fees, or duration | `{ course_name, course_fees, course_duration }` |
| `DELETE` | `/deletecourse/<id>/` | Delete a course curriculum | None |
| `GET` | `/api/stats/` | Live telemetry data for metrics & Chart.js charts | None |
| `GET` | `/api-docs/` | Interactive REST Console & SDK Generator | None |

---

## 🧪 Running Automated Tests

Run the full Django test suite:
```bash
python manage.py test
```

Expected output:
```
Ran 11 tests in 0.32s
OK
System check identified no issues (0 silenced).
```

---

## 👤 Author & License
- **Author**: Paras Patadiya
- **Role**: Full-Stack Python & Django Developer
- **License**: MIT

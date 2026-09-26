# Aura SIS &mdash; Enterprise Student & Course Management Cloud Platform

[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/Django_REST_Framework-3.17-red?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Gunicorn](https://img.shields.io/badge/Gunicorn-26.2-499848?style=for-the-badge&logo=gunicorn&logoColor=white)](https://gunicorn.org/)
[![WhiteNoise](https://img.shields.io/badge/WhiteNoise-6.12-blue?style=for-the-badge)](http://whitenoise.evans.io/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)

An enterprise-ready, production-hardened full-stack Student Information System (SIS) and REST Gateway. Built with **Django 6.0** and **Django REST Framework (DRF)** on the backend, styled with an executive glassmorphism SaaS interface, real-time Chart.js analytics, and a multi-language developer SDK generator (cURL, Python, JavaScript).

---

## Key Features

- **Executive Cloud Dashboard**: Real-time KPI telemetry (Active Students, Course Tracks, Tuition Pipeline in ₹, Median Student Demographics).
- **Dual-View Student Directory**: Toggle seamlessly between an **Interactive Data Table** and a modern **Card Grid View**.
- **Multi-Attribute Search & Course Filter**: Instant debounce query across student names, emails, phone numbers, and cities.
- **In-App Developer Sandbox & SDK Generator**: Test live REST endpoints in real-time and generate copyable snippets in **cURL**, **Python (requests)**, and **JavaScript (Fetch)**.
- **Production Hardened**:
  - Pre-configured with **WhiteNoise** for standalone static file serving without external Nginx.
  - Environment variable support (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`).
  - **Gunicorn** WSGI production runner with `Procfile` and `build.sh` for 1-click cloud hosting.
  - Hardened CSRF trusted origins for Render, Railway, Vercel, and PythonAnywhere.
- **CSV Data Export**: One-click download of the complete student registry to CSV.
- **Automated Test Suite**: 11 unit and integration test cases covering models, serializers, validation rules, and REST endpoints (**11/11 passing**).

---

## Architecture Overview

```
                                  +-----------------------------+
                                  |     Modern Frontend UI      |
                                  | (Tailwind CSS, FontAwesome, |
                                  |   Chart.js, Vanilla ES6)    |
                                  +--------------+--------------+
                                                 |
                                        Fetch / REST JSON
                                                 |
                                                 v
+--------------------------------------------------------------------------------------------+
|                              Production Django & DRF Backend                               |
|                                                                                            |
|  +--------------------+   +-----------------------+   +-------------------+   +---------+  |
|  |    WhiteNoise      |-->|      URL Routing      |-->|     API Views     |-->| Models  |  |
|  |  (Static Serving)  |   |   (apiapp/urls.py)    |   | (apiapp/views.py) |   |  (ORM)  |  |
|  +--------------------+   +-----------------------+   +-------------------+   +----+----+  |
|                                                                                    |       |
+------------------------------------------------------------------------------------|-------+
                                                                                     v
                                                                          +--------------------+
                                                                          |   SQLite Database  |
                                                                          +--------------------+
```

---

## REST API Specification

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

---

## Local Setup & Quickstart

### 1. Clone & Enter Project Directory
```bash
git clone <your-repo-url>
cd apiproject
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Production Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations & Collect Static Files
```bash
python manage.py migrate
python manage.py collectstatic --no-input
```

### 5. Launch Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 1-Click Live Cloud Deployment Guide

### Deploying to Render.com (Recommended)
1. Push your project to GitHub.
2. Sign in to [Render](https://render.com/) and click **New +** &rarr; **Web Service**.
3. Select your GitHub repository.
4. Configure the service settings:
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn apiproject.wsgi --log-file -`
5. Under **Environment Variables**, add:
   - `SECRET_KEY`: `<generate-a-strong-random-key>`
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `.onrender.com,localhost,127.0.0.1`
6. Click **Deploy Web Service**. Render will build and launch your live application automatically!

---

## Running Automated Tests

Run the full Django REST test suite:
```bash
python manage.py test apiapp
```

Expected output:
```
Ran 11 tests in 0.33s
OK
```

---

## Author & Credits
- **Developer**: Paras Patadiya
- **Role**: Full-Stack Python & Django Developer
- **License**: MIT

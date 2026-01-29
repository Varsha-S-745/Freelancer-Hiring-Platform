# SkillConnect – Freelancer Hiring Platform

SkillConnect is a freelancer job searching and hiring platform built using **Django**, **Django REST Framework**, **HTML**, **CSS**, and **JavaScript**.  
It supports **separate authentication and dashboards** for **Freelancers** and **Recruiters**, with **JWT-based authentication**, job posting, job applications, application tracking, and **email notifications**.

---

## Project Overview

SkillConnect allows:
- Freelancers to create profiles, browse jobs, apply for jobs, and track application status.
- Recruiters to post jobs, view applications, and accept or reject freelancer applications.
- Automatic email notifications to freelancers when their application status changes.

---

## Tech Stack

- Backend: Django, Django REST Framework
- Authentication: JWT (SimpleJWT)
- Frontend: HTML, CSS, JavaScript
- Database: SQLite (default)
- API Testing: Postman
- Email Service: Gmail SMTP

---

## Home Page

The home page (`SkillConnect`) contains four options:
- Freelancer Register
- Freelancer Sign In
- Recruiter Register
- Recruiter Sign In

Users must choose their role before authentication.

---

## Authentication

- Signup and Signin APIs
- JWT-based authentication
- Backend authentication only (frontend handled separately)
- Users sign up/sign in using:
  - Username
  - Email
  - Password

---

## User Model

Custom user model includes:
- Username
- Email
- Password
- Role (Freelancer / Recruiter)
- Resume (file upload)
- Additional role-based fields

---

## Role-Based Flow

When the application opens:
- Registration page is shown
- User selects role (Freelancer or Recruiter)
- User is redirected to the respective signup/signin page
- After successful login, user is redirected to the respective dashboard

---

## Freelancer Dashboard

The freelancer dashboard contains the following features:

### 1. View / Create / Edit Profile
Freelancers can create and manage their profile with:
- Name
- Date of Birth
- Skills
- Experience
- Tech Stack

### 2. View Job Postings
- Freelancers can view all available job postings
- Freelancers can apply using the **"I'm Interested"** button
- If already applied, system shows **Already Applied**
- Otherwise, application is submitted successfully

### 3. Track Application Status
Freelancers can track application status for all applied jobs:
- Pending
- Accepted
- Rejected

---

## Recruiter Dashboard

The recruiter dashboard contains the following features:

### 1. Post New Jobs
Recruiters can post jobs with:
- Job Title
- Pay Per Hour
- Tech Stack
- Experience Level

### 2. View Applications
Recruiters can:
- View all applications for jobs they posted
- See freelancer details
- Accept or Reject applications

---

## Job Application Workflow

1. Freelancer applies to a job using **I'm Interested**
2. Application status is set to **Pending**
3. Recruiter reviews the application
4. Recruiter accepts or rejects the application
5. Freelancer receives an email notification

---

## Email Notification System

- Gmail SMTP is used
- Email is sent to freelancers when application status changes
- Triggered on:
  - Application Accepted
  - Application Rejected

---

## API Endpoints

### Authentication
- POST `/api/signup/`
- POST `/api/signin/`
- POST `/api/token/refresh/`

### Freelancer APIs
- GET `/api/freelancer/profile/`
- POST `/api/freelancer/profile/`
- PUT `/api/freelancer/profile/`
- GET `/api/jobs/`
- POST `/api/jobs/apply/<job_id>/`
- GET `/api/applications/status/`

### Recruiter APIs
- POST `/api/jobs/create/`
- GET `/api/jobs/my-jobs/`
- GET `/api/jobs/<job_id>/applications/`
- POST `/api/applications/<id>/accept/`
- POST `/api/applications/<id>/reject/`

---

## Setup Instructions

### Clone the Repository
```bash
git clone https://github.com/your-username/skillconnect.git
cd skillconnect

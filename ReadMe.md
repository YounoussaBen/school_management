# School Management System

This Django application is designed for managing a school's administrative tasks. It supports functionalities for handling student profiles, teacher assignments, course management, attendance tracking, and grade reporting. The system includes separate login mechanisms for students and teachers, and an admin panel for creating and managing courses, staff, teachers, and students.

## Features

- **User Management**: Supports roles for Students, Teachers, and Staff.
- **Course Management**: Assign courses to teachers and enroll students in courses.
- **Attendance Tracking**: Record and view student attendance for each subject.
- **Grade Management**: Input and manage student grades, with automated GPA calculation.
- **Report Generation**: Downloadable PDF reports for students including grades, attendance, and teacher remarks.

## Installation and Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/YounoussaBen/school_management.git
   cd school_management
   ```

2. **Set Up Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**

   ```bash
   python manage.py migrate
   ```

5. **Create a Superuser**

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the Development Server**

   ```bash
   python manage.py runserver
   ```

7. **Access the Application**

   - **Admin Panel**: Navigate to `http://127.0.0.1:8000/admin/` to create and manage courses, staff, teachers, and students.
   - **Main Page**: Navigate to `http://127.0.0.1:8000/` to sign in as a student or teacher.

## Usage

- **Student Login**: Enter your email and password to access student functionalities such as viewing your grades, attendance, and profile.
- **Teacher Login**: Enter your email and password to access teacher functionalities such as marking attendance, managing grades, and viewing student profiles.

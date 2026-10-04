# Job Application Tracker

Python Flask + MySQL web application for tracking job applications.

## Features
- Register/Login
- Add job applications
- Edit/Delete applications
- Application status tracking
- Search and filter
- Interview date
- Dashboard statistics
- MySQL database

## Windows Setup

### 1. Open the project in VS Code

Open this folder:
`JobApplicationTracker`

### 2. Create and activate virtual environment

Open VS Code Terminal:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install packages

```bash
pip install -r requirements.txt
```

### 4. Create database

Open MySQL Workbench and open `database.sql`.
Run the complete SQL script.

It creates:
- `job_tracker` database
- `users` table
- `jobs` table

### 5. Set MySQL password

Open `app.py`.

Find:

```python
"password": "YOUR_MYSQL_PASSWORD",
```

Replace it with your MySQL root password.

Do not share your password publicly.

### 6. Run the application

In the VS Code terminal:

```bash
python app.py
```

You should see:

`Running on http://127.0.0.1:5000`

Open Chrome:

`http://127.0.0.1:5000`

### 7. First use

1. Click Register.
2. Create an account.
3. Login.
4. Click Add Job.
5. Add a company and role.
6. Check Dashboard.
7. Use Applications to search, filter, edit and delete.

## Important

Keep the terminal running while using the website.
To stop the server, press `Ctrl + C`.

## Resume Project Title

Job Application Tracker | Python, Flask, MySQL, HTML, CSS, JavaScript

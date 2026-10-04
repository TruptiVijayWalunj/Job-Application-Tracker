from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "trupti08",
    "database": "job_tracker"
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if not name or not email or not password:
            flash("All fields are required.")
            return redirect(url_for("register"))

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            cur.close()
            db.close()
            flash("Email already registered.")
            return redirect(url_for("register"))

        hashed = generate_password_hash(password)
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",
            (name, email, hashed)
        )
        db.commit()
        cur.close()
        db.close()

        flash("Registration successful. Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()
        db.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(status='Applied') AS applied,
            SUM(status='Shortlisted') AS shortlisted,
            SUM(status='Interview') AS interview,
            SUM(status='Selected') AS selected,
            SUM(status='Rejected') AS rejected
        FROM jobs WHERE user_id=%s
    """, (session["user_id"],))
    stats = cur.fetchone()

    cur.execute("""
        SELECT * FROM jobs
        WHERE user_id=%s
        ORDER BY id DESC LIMIT 5
    """, (session["user_id"],))
    recent_jobs = cur.fetchall()

    cur.close()
    db.close()
    return render_template("dashboard.html", stats=stats, jobs=recent_jobs)

@app.route("/jobs")
@login_required
def jobs():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    db = get_db()
    cur = db.cursor(dictionary=True)

    query = "SELECT * FROM jobs WHERE user_id=%s"
    params = [session["user_id"]]

    if search:
        query += " AND (company_name LIKE %s OR job_role LIKE %s OR location LIKE %s)"
        like = f"%{search}%"
        params.extend([like, like, like])

    if status:
        query += " AND status=%s"
        params.append(status)

    query += " ORDER BY id DESC"
    cur.execute(query, tuple(params))
    job_list = cur.fetchall()

    cur.close()
    db.close()
    return render_template("jobs.html", jobs=job_list, search=search, status=status)

@app.route("/jobs/add", methods=["GET", "POST"])
@login_required
def add_job():
    if request.method == "POST":
        company = request.form["company_name"].strip()
        role = request.form["job_role"].strip()
        location = request.form["location"].strip()
        applied_date = request.form["applied_date"] or None
        status = request.form["status"]
        interview_date = request.form["interview_date"] or None
        notes = request.form["notes"].strip()

        db = get_db()
        cur = db.cursor()
        cur.execute("""
            INSERT INTO jobs
            (user_id, company_name, job_role, location, applied_date,
             status, interview_date, notes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            session["user_id"], company, role, location, applied_date,
            status, interview_date, notes
        ))
        db.commit()
        cur.close()
        db.close()

        flash("Job application added successfully.")
        return redirect(url_for("jobs"))

    return render_template("add_job.html")

@app.route("/jobs/edit/<int:job_id>", methods=["GET", "POST"])
@login_required
def edit_job(job_id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM jobs WHERE id=%s AND user_id=%s",
        (job_id, session["user_id"])
    )
    job = cur.fetchone()
    cur.close()

    if not job:
        db.close()
        flash("Job not found.")
        return redirect(url_for("jobs"))

    if request.method == "POST":
        company = request.form["company_name"].strip()
        role = request.form["job_role"].strip()
        location = request.form["location"].strip()
        applied_date = request.form["applied_date"] or None
        status = request.form["status"]
        interview_date = request.form["interview_date"] or None
        notes = request.form["notes"].strip()

        cur = db.cursor()
        cur.execute("""
            UPDATE jobs SET company_name=%s, job_role=%s, location=%s,
            applied_date=%s, status=%s, interview_date=%s, notes=%s
            WHERE id=%s AND user_id=%s
        """, (
            company, role, location, applied_date, status,
            interview_date, notes, job_id, session["user_id"]
        ))
        db.commit()
        cur.close()
        db.close()

        flash("Job application updated.")
        return redirect(url_for("jobs"))

    db.close()
    return render_template("edit_job.html", job=job)

@app.route("/jobs/delete/<int:job_id>", methods=["POST"])
@login_required
def delete_job(job_id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "DELETE FROM jobs WHERE id=%s AND user_id=%s",
        (job_id, session["user_id"])
    )
    db.commit()
    cur.close()
    db.close()

    flash("Job application deleted.")
    return redirect(url_for("jobs"))

if __name__ == "__main__":
    app.run(debug=True)

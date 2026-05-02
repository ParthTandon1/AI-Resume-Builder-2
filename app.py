from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from PyPDF2 import PdfReader
import os
from weasyprint import HTML

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "fallback_key")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume_builder.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------- MODELS ----------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)

    full_name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))

    profile = db.Column(db.String(500))
    education = db.Column(db.String(500))
    internships = db.Column(db.String(500))
    projects = db.Column(db.String(500))
    certifications = db.Column(db.String(500))
    skills = db.Column(db.String(500))
    achievements = db.Column(db.String(500))
    seminars = db.Column(db.String(500))
    publications = db.Column(db.String(500))

    template = db.Column(db.String(50))


with app.app_context():
    db.create_all()

# ---------- ROUTES ----------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = User(
            name=request.form.get("name"),
            email=request.form.get("email"),
            password=request.form.get("password")
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            email=request.form.get("email").strip(),
            password=request.form.get("password").strip()
        ).first()

        if user:
            session["user_id"] = user.id
            return redirect("/dashboard")
        return "Invalid credentials"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" in session:
        return render_template("dashboard.html")
    return redirect("/login")


# ---------- ATS UPLOAD ----------
@app.route("/upload_resume", methods=["GET", "POST"])
def upload_resume():
    if request.method == "POST":
        file = request.files.get("resume")
        job_desc = request.form.get("job_desc") or ""

        if not file or not file.filename.endswith(".pdf"):
            return "Upload PDF only"

        reader = PdfReader(file)
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        job_words = set(job_desc.lower().split())
        resume_words = set(text.lower().split())

        match = job_words.intersection(resume_words)
        score = int((len(match) / len(job_words)) * 100) if job_words else 0
        missing = list(job_words - resume_words)

        return render_template("ats_result.html", score=score, missing=missing[:20])

    return render_template("upload_resume.html")


# ---------- CREATE RESUME ----------
@app.route("/resume", methods=["GET", "POST"])
def resume():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        new_resume = Resume(
            user_id=session["user_id"],
            full_name=request.form.get("full_name") or "",
            address=request.form.get("address") or "",
            phone=request.form.get("phone") or "",
            email=request.form.get("email") or "",
            profile=request.form.get("profile") or "",
            education=request.form.get("education") or "",
            internships=request.form.get("internships") or "",
            projects=request.form.get("projects") or "",
            certifications=request.form.get("certifications") or "",
            skills=request.form.get("skills") or "",
            achievements=request.form.get("achievements") or "",
            seminars=request.form.get("seminars") or "",
            publications=request.form.get("publications") or "",
            template=request.form.get("template") or "classic"
        )

        db.session.add(new_resume)
        db.session.commit()
        return redirect("/preview")

    return render_template("resume.html")


# ---------- PREVIEW ----------
@app.route("/preview")
def preview():
    if "user_id" not in session:
        return redirect("/login")

    resume = Resume.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Resume.id.desc()).first()

    if not resume:
        return "No resume found"

    if resume.template == "modern":
        return render_template("modern.html", resume=resume)
    return render_template("classic.html", resume=resume)


# ---------- DOWNLOAD (DISABLED SAFE VERSION) ----------
@app.route("/download")
def download():

    if "user_id" not in session:
        return redirect("/login")

    resume = Resume.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Resume.id.desc()).first()

    if not resume:
        return "No resume found"

    # Render HTML template
    rendered = render_template("classic.html", resume=resume)

    # Convert to PDF
    pdf = HTML(string=rendered).write_pdf()

    return (pdf, 200, {
        'Content-Type': 'application/pdf',
        'Content-Disposition': f'attachment; filename={resume.full_name}.pdf'
    })

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run()
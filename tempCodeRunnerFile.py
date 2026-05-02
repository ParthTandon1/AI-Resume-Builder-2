from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

# Create Flask App
app = Flask(__name__)
app.secret_key = "secretkey"

# SQLite Configuration (no MySQL required)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resume_builder.db'       
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db = SQLAlchemy(app)

# Database Model
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    education = db.Column(db.String(200))
    skills = db.Column(db.String(300))
    experience = db.Column(db.String(300))
    certifications = db.Column(db.String(300))
    internships = db.Column(db.String(300))
    projects = db.Column(db.String(300))

# Create Tables
with app.app_context():
    db.create_all()

# Routes
@app.route("/")
#Home
def home():
    return render_template("index.html")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")

@app.route("/resume", methods=["GET", "POST"])
def resume():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        full_name = request.form["full_name"]
        phone = request.form["phone"]
        email = request.form["email"]
        education = request.form["education"]
        skills = request.form["skills"]
        experience = request.form["experience"]
        certifications = request.form["certifications"]
        internships = request.form["internships"]
        projects = request.form["projects"]
        new_resume = Resume(
    user_id=session["user_id"],
    full_name=full_name,
    phone=phone,
    email=email,
    education=education,
    skills=skills,
    experience=experience,
    certifications=certifications,
    internships=internships,
    projects=projects
)
        db.session.add(new_resume)
        db.session.commit()
        return redirect("/preview")
    return render_template("resume.html")

@app.route("/preview")
def preview():

    if "user_id" not in session:
        return redirect("/login")

    resume = Resume.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Resume.id.desc()).first()

    return render_template("preview.html", resume=resume)

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            session["user_id"] = user.id
            return redirect("/dashboard")
        else:
            return "Invalid Email or Password"

    return render_template("login.html")

# Dashboard
@app.route("/dashboard")
def dashboard():
    if "user_id" in session:
        return render_template("dashboard.html")
    else:
        return redirect("/login")

# Logout
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/login")

# Run Server
if __name__ == "__main__":
    app.run(debug=True)

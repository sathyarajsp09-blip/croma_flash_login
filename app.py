from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
import re
import string
import os

# =====================
# APP SETUP
# =====================
app = Flask(__name__)
app.secret_key = "secret123"

# =====================
# DATABASE CONFIG
# =====================
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Render / Production (PostgreSQL)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    # Local development (SQLite)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/database.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# =====================
# MODELS
# =====================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(80), nullable=False)

# =====================
# HELPERS
# =====================
def has_sequential_chars(password, seq_len=3):
    password = password.lower()
    sequences = (string.ascii_lowercase, string.digits)

    for seq in sequences:
        for i in range(len(seq) - seq_len + 1):
            if seq[i:i+seq_len] in password:
                return True
    return False

# =====================
# ROUTES
# =====================
@app.route("/")
def home():
    return render_template("Home.html")

@app.route("/homepage")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["pwd"]

        user_data = User.query.filter_by(
            username=uname,
            password=passw
        ).first()

        if user_data:
            session["user"] = uname
            return redirect(url_for("dashboard"))

        return render_template("login.html", login_error="Invalid username or password")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form["uname"]
        mail = request.form["email"]
        pwd = request.form["pwd"]
        cpwd = request.form["cpwd"]

        if pwd != cpwd:
            return render_template("register.html", error="Passwords do not match")

        if not (8 <= len(pwd) <= 16):
            return render_template("register.html", error="Password must be 8–16 characters long")

        if not re.search(r"[A-Z]", pwd):
            return render_template("register.html", error="Password must contain an uppercase letter")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd):
            return render_template("register.html", error="Password must contain a special character")

        if has_sequential_chars(pwd):
            return render_template("register.html", error="Password must not contain sequences")

        new_user = User(username=uname, email=mail, password=pwd)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/secondpage")
def secondpage():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("secondpage.html")

@app.route("/playstation")
def playstation():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("playstation_corousel.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# =====================
# APP START (SAFE)
# =====================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()

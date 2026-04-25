from flask import Flask, render_template, request, redirect, session
from utils.db import init_db
from models.analyzer import analyze_answer
import sqlite3, random
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

init_db()

question_bank = {
    "HR": [
        "Tell me about yourself",
        "What are your strengths?",
        "Why should we hire you?",
        "Tell me about a challenge you faced",
        "Where do you see yourself in 5 years?"
    ],
    "DSA": [
        "Explain binary search",
        "What is time complexity?",
        "Difference between stack and queue",
        "What is recursion?",
        "What is dynamic programming?"
    ],
    "TECH": [
        "What is OOP?",
        "Explain REST API",
        "What is SQL?",
        "What is normalization?",
        "What is cloud computing?"
    ]
}

@app.route("/", methods=["GET","POST"])
def index():
    if "user_id" not in session:
        return redirect("/login")

    question = session.get("question", "")
    score = ""
    feedback = ""
    missing = []

    if request.method == "POST":

        if "category" in request.form:
            category = request.form["category"]
            question = random.choice(question_bank[category])
            session["question"] = question

        elif "answer" in request.form:
            answer = request.form["answer"]
            question = session.get("question")

            score, missing, feedback = analyze_answer(question, answer)

            conn = sqlite3.connect("database.db")
            cur = conn.cursor()
            cur.execute("INSERT INTO results VALUES (NULL,?,?,?)",
                        (session["user_id"], "Mixed", score))
            conn.commit()
            conn.close()

    return render_template("index.html",
                           question=question,
                           score=score,
                           feedback=feedback,
                           missing=missing)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("SELECT id,password FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            return redirect("/")
        return "Invalid login"

    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO users VALUES (NULL,?,?)",(username,password))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT score FROM results WHERE user_id=?", (session["user_id"],))
    data = cur.fetchall()
    conn.close()

    scores = [x[0] for x in data]
    avg = sum(scores)/len(scores) if scores else 0

    return render_template("dashboard.html",
                           scores=scores,
                           avg=avg)
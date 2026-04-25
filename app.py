from flask import Flask, render_template, request, redirect, session
import sqlite3, random
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        category TEXT,
        score INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- QUESTIONS ----------------
question_bank = {
    "HR": [
        "Tell me about yourself",
        "What are your strengths?",
        "Why should we hire you?"
    ],
    "DSA": [
        "Explain binary search",
        "What is time complexity?",
        "Difference between stack and queue"
    ],
    "TECH": [
        "What is OOP?",
        "Explain REST API",
        "What is SQL?"
    ]
}

# ---------------- IDEAL DATA ----------------
ideal_data = {
    "Tell me about yourself": {
        "ideal": "I am a computer science student with strong programming and problem solving skills and experience in projects.",
        "keywords": ["programming", "skills", "projects", "problem solving"]
    },
    "What are your strengths?": {
        "ideal": "My strengths include problem solving, teamwork, communication and technical skills.",
        "keywords": ["problem solving", "teamwork", "communication", "skills"]
    },
    "Why should we hire you?": {
        "ideal": "You should hire me because I have strong technical skills, problem solving ability and I am eager to learn.",
        "keywords": ["skills", "problem solving", "learning"]
    },
    "Explain binary search": {
        "ideal": "Binary search works on sorted arrays and has time complexity of O log n.",
        "keywords": ["sorted", "algorithm", "log"]
    },
    "What is time complexity?": {
        "ideal": "Time complexity measures how runtime grows with input size.",
        "keywords": ["algorithm", "input", "time"]
    },
    "Difference between stack and queue": {
        "ideal": "Stack uses LIFO and queue uses FIFO.",
        "keywords": ["lifo", "fifo"]
    },
    "What is OOP?": {
        "ideal": "Object oriented programming includes classes objects inheritance polymorphism encapsulation.",
        "keywords": ["class", "object", "inheritance", "polymorphism"]
    },
    "Explain REST API": {
        "ideal": "REST API uses HTTP methods like GET POST PUT DELETE.",
        "keywords": ["http", "api", "get", "post"]
    },
    "What is SQL?": {
        "ideal": "SQL is used to manage and query relational databases.",
        "keywords": ["database", "query", "data"]
    }
}

# ---------------- ANALYSIS ----------------
def analyze_answer(question, answer):
    data = ideal_data.get(question)
    if not data:
        return 50, [], "Basic answer"

    ideal = data["ideal"]
    keywords = data["keywords"]

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([ideal, answer])

    similarity = cosine_similarity(vectors[0:1], vectors[1:2])
    sim_score = similarity[0][0] * 70

    missing = [k for k in keywords if k not in answer.lower()]
    keyword_score = ((len(keywords) - len(missing)) / len(keywords)) * 30

    final_score = int(sim_score + keyword_score)

    # Feedback
    if final_score > 80:
        feedback = "Excellent answer with strong clarity."
    elif final_score > 60:
        feedback = "Good answer, improve depth."
    else:
        feedback = "Needs improvement. Add more key concepts."

    return final_score, missing, feedback

# ---------------- AUTH ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users VALUES (NULL, ?, ?)", (username, password))
            conn.commit()
        except:
            return "User already exists"

        conn.close()
        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, password FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- MAIN ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        return redirect("/login")

    question = ""
    score = ""
    missing = []
    feedback = ""
    category = ""

    if request.method == "POST":
        category = request.form["category"]
        answer = request.form.get("answer", "")

        question = random.choice(question_bank[category])

        if answer:
            score, missing, feedback = analyze_answer(question, answer)

            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO results VALUES (NULL, ?, ?, ?)",
                           (session["user_id"], category, score))
            conn.commit()
            conn.close()

    return render_template("index.html",
                           question=question,
                           score=score,
                           missing=missing,
                           feedback=feedback,
                           category=category)

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT category, score FROM results WHERE user_id=?", 
                   (session["user_id"],))
    data = cursor.fetchall()
    conn.close()

    categories = [row[0] for row in data]
    scores = [row[1] for row in data]

    return render_template("dashboard.html",
                           categories=categories,
                           scores=scores)

if __name__ == "__main__":
    app.run()
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

ideal_data = {

# ---------------- HR ----------------
"Tell me about yourself": {
    "ideal": "I am a computer science student with strong programming skills and experience in building projects.",
    "keywords": ["programming", "skills", "projects"]
},
"What are your strengths?": {
    "ideal": "My strengths include problem solving, teamwork and communication skills.",
    "keywords": ["problem solving", "teamwork", "skills"]
},
"Why should we hire you?": {
    "ideal": "I have strong technical skills and a learning mindset to contribute effectively.",
    "keywords": ["skills", "learning"]
},
"Tell me about a challenge you faced": {
    "ideal": "I faced a challenge in a project and solved it through research and persistence.",
    "keywords": ["challenge", "solution"]
},
"Where do you see yourself in 5 years?": {
    "ideal": "I see myself growing as a skilled software engineer contributing to impactful projects.",
    "keywords": ["growth", "career"]
},

# ---------------- DSA ----------------
"Explain binary search": {
    "ideal": "Binary search works on sorted arrays and has O log n complexity.",
    "keywords": ["sorted", "log"]
},
"What is time complexity?": {
    "ideal": "Time complexity measures how runtime grows with input size.",
    "keywords": ["runtime", "input"]
},
"Difference between stack and queue": {
    "ideal": "Stack uses LIFO and queue uses FIFO.",
    "keywords": ["lifo", "fifo"]
},
"What is recursion?": {
    "ideal": "Recursion is when a function calls itself until a base condition.",
    "keywords": ["function", "base"]
},
"What is dynamic programming?": {
    "ideal": "Dynamic programming solves problems by storing subproblem results.",
    "keywords": ["subproblem", "dp"]
},

# ---------------- TECH ----------------
"What is OOP?": {
    "ideal": "OOP is based on classes objects inheritance polymorphism encapsulation.",
    "keywords": ["class", "object"]
},
"Explain REST API": {
    "ideal": "REST API uses HTTP methods like GET POST PUT DELETE.",
    "keywords": ["http", "api"]
},
"What is SQL?": {
    "ideal": "SQL is used to manage and query databases.",
    "keywords": ["database", "query"]
},
"What is normalization?": {
    "ideal": "Normalization reduces redundancy in databases.",
    "keywords": ["database", "redundancy"]
},
"What is cloud computing?": {
    "ideal": "Cloud computing provides services over the internet.",
    "keywords": ["internet", "services"]
}
}

def analyze_answer(question, answer):
    data = ideal_data.get(question)

    if not data:
        return 50, [], "Basic answer"

    ideal = data["ideal"]
    keywords = data["keywords"]

    emb1 = model.encode(ideal, convert_to_tensor=True)
    emb2 = model.encode(answer, convert_to_tensor=True)

    similarity = util.cos_sim(emb1, emb2).item()
    sim_score = similarity * 70

    missing = [k for k in keywords if k not in answer.lower()]
    keyword_score = ((len(keywords) - len(missing)) / len(keywords)) * 30

    final_score = int(sim_score + keyword_score)

    if final_score > 80:
        feedback = "Excellent answer."
    elif final_score > 60:
        feedback = "Good answer, improve depth."
    else:
        feedback = "Needs improvement."

    return final_score, missing, feedback
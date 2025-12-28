import os
import re
import requests
import pdfminer.high_level
from tkinter import Tk, filedialog, messagebox, ttk
import tkinter as tk


# ----------------- Resume Parsing ----------------- #
def extract_text_from_pdf(pdf_path):
    return pdfminer.high_level.extract_text(pdf_path)

def extract_name(text):
    # Split text into lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Common unwanted headings to ignore
    ignore_words = ['resume', 'curriculum', 'vitae', 'bio-data', 'profile']
    
    for line in lines[:10]:
        # Skip lines that contain digits or unwanted words
        if any(ch.isdigit() for ch in line):
            continue
        if any(word.lower() in line.lower() for word in ignore_words):
            continue
        
        words = line.split()
        # Check if the line looks like a name (2–4 words, alphabetic)
        if 1 < len(words) <= 4 and all(w.isalpha() for w in words):
            # Check for uppercase or title case
            if line.isupper() or all(w[0].isupper() for w in words):
                return line.title()
    
    # Fallback: look for name-like pattern (First Last)
    match = re.search(r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,2})\b", text)
    if match:
        return match.group(0).title()

    return "Name Not Found"


def extract_phone(text):
    # Matches +91 9876543210, (987)6543210, 98765-43210, 9876543210
    match = re.search(r"(\+?\d{1,3}[\s\-]?\(?\d{3,5}\)?[\s\-]?\d{3,5}[\s\-]?\d{3,5})", text)
    if match:
        phone = match.group()
        # Clean spaces and extra symbols
        phone = re.sub(r"[^\d+]", "", phone)
        return phone
    return "Phone Not Found"


def extract_email(text):
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group() if match else "Not Found"


def extract_skills(text):
    keywords = [
        "python", "java", "c++", "sql", "html", "css", "javascript", "django",
        "flask", "pandas", "numpy", "machine learning", "deep learning",
        "data science", "excel", "power bi", "matplotlib", "tensorflow", "keras"
    ]
    found = set()
    lower_text = text.lower()
    for skill in keywords:
        if skill in lower_text:
            found.add(skill.title())
    return list(found)

def parse_resume(file_path):
    text = extract_text_from_pdf(file_path)
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text)
    }

# ----------------- Recommendation System ----------------- #
def get_coursera_courses(skill):
    url = f"https://api.coursera.org/api/courses.v1?q=search&query={skill}&limit=3"
    try:
        res = requests.get(url)
        data = res.json()
        courses = data.get("elements", [])
        return [{
            "platform": "Coursera",
            "title": course.get("name", "Course"),
            "url": f"https://www.coursera.org/learn/{course.get('slug', '')}"
        } for course in courses]
    except:
        return []

def get_linkedin_learning_courses(skill):
    return [{
        "platform": "LinkedIn Learning",
        "title": f"{skill.title()} for Beginners",
        "url": f"https://www.linkedin.com/learning/search?keywords={skill}"
    }]

def get_linkedin_jobs(skill):
    return [{
        "platform": "LinkedIn",
        "title": f"{skill.title()} Jobs",
        "url": f"https://www.linkedin.com/jobs/search/?keywords={skill}"
    }]

def get_indeed_jobs(skill):
    return [{
        "platform": "Indeed",
        "title": f"{skill.title()} Jobs",
        "url": f"https://www.indeed.com/jobs?q={skill}"
    }]

def get_naukri_jobs(skill):
    return [{
        "platform": "Naukri",
        "title": f"{skill.title()} Jobs",
        "url": f"https://www.naukri.com/{skill}-jobs"
    }]

def recommend_courses(skills):
    result = []
    for skill in skills:
        result += get_coursera_courses(skill)
        result += get_linkedin_learning_courses(skill)
    return result

def recommend_jobs(skills):
    result = []
    for skill in skills:
        result += get_linkedin_jobs(skill)
        result += get_indeed_jobs(skill)
        result += get_naukri_jobs(skill)
    return result

# ----------------- GUI ----------------- #
class ResumeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Resume Parser & Recommender")
        self.geometry("950x600")
        self.configure(bg="#f8f9fa")
        self.skills = []
        self.sidebar()
        self.main_frame = tk.Frame(self, bg="white")
        self.main_frame.pack(side="right", fill="both", expand=True)
        self.show_home()
        
    def sidebar(self):
        sidebar = tk.Frame(self, bg="#2c3e50", width=200)
        sidebar.pack(side="left", fill="y")
        tk.Label(sidebar, text="DYNA", bg="#2c3e50", fg="white", font=("Arial", 16)).pack(pady=20)
        opts = [("Home", self.show_home), ("Resume Parser", self.show_resume_parser),
                ("Course Suggestions", self.show_courses), ("Job Suggestions", self.show_jobs)]
        for text, cmd in opts:
            tk.Button(sidebar, text=text, bg="#34495e", fg="white", font=("Arial", 12),
                      command=cmd).pack(fill="x", pady=5, padx=10)

    def clear_main(self):
        for w in self.main_frame.winfo_children():
            w.destroy()

    def show_home(self):
        self.clear_main()
        tk.Label(self.main_frame, text="Welcome to DYNA", font=("Arial", 24), bg="white").pack(pady=100)

    def show_resume_parser(self):
        self.clear_main()
        result_box = tk.Text(self.main_frame, font=("Arial", 12), width=100, height=20)
        result_box.pack(pady=20)

        def upload():
            file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
            if file_path:
                data = parse_resume(file_path)
                self.skills = data["skills"]
                output = f"Name: {data['name']}\nEmail: {data['email']}\nPhone: {data['phone']}\nSkills: {', '.join(self.skills)}"
                result_box.delete("1.0", tk.END)
                result_box.insert(tk.END, output)

        tk.Button(self.main_frame, text="Upload Resume (PDF)", command=upload,
                  bg="#27ae60", fg="white", font=("Arial", 13)).pack(pady=10)

    def show_courses(self):
        self.clear_main()
        tk.Label(self.main_frame, text="📚 Course Suggestions", font=("Arial", 18), bg="white").pack(pady=10)
        if not self.skills:
            tk.Label(self.main_frame, text="Please parse a resume first.", fg="red", bg="white").pack(pady=20)
            return
        self.display_recommendations(recommend_courses(self.skills))

    def show_jobs(self):
        self.clear_main()
        tk.Label(self.main_frame, text="💼 Job Suggestions", font=("Arial", 18), bg="white").pack(pady=10)
        if not self.skills:
            tk.Label(self.main_frame, text="Please parse a resume first.", fg="red", bg="white").pack(pady=20)
            return
        self.display_recommendations(recommend_jobs(self.skills))

    def display_recommendations(self, items):
        container = tk.Frame(self.main_frame, bg="white")
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg="white")

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for item in items:
            block = tk.Frame(scrollable, bg="#ecf0f1", pady=5, padx=10, bd=1, relief="solid")
            block.pack(padx=10, pady=5, fill="x")
            tk.Label(block, text=item["title"], font=("Arial", 13, "bold"), bg="#ecf0f1").pack(anchor="w")
            tk.Label(block, text=f"Platform: {item['platform']}", bg="#ecf0f1").pack(anchor="w")
            tk.Label(block, text=item["url"], fg="blue", cursor="hand2", bg="#ecf0f1").pack(anchor="w")


if __name__ == "__main__":
    app = ResumeApp()
    app.mainloop()
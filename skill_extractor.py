import re
# Canonical skill name -> list of ways people write it.
SKILLS = {
    # Languages
    "Python": ["python"],
    "Java": ["java"],
    "C": ["c language", "c programming"],
    "C++": ["c++", "cpp"],
    "C#": ["c#"],
    "JavaScript": ["javascript", "js", "ecmascript"],
    "TypeScript": ["typescript"],
    "SQL": ["sql", "mysql", "postgresql", "postgres", "sqlite", "oracle sql"],
    "R": ["r programming", "r language"],
    # Core CS
    "Data Structures": ["data structures", "dsa", "data structures and algorithms"],
    "Algorithms": ["algorithms", "algorithm design"],
    "OOP": ["oop", "oops", "object oriented", "object-oriented"],
    "Operating Systems": ["operating systems", "operating system"],
    "DBMS": ["dbms", "database management"],
    "Computer Networks": ["computer networks", "networking"],
    # Data / ML
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning"],
    "NLP": ["nlp", "natural language processing"],
    "Computer Vision": ["computer vision", "opencv"],
    "Data Analysis": ["data analysis", "data analytics"],
    "Data Visualization": ["data visualization", "data visualisation"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "Matplotlib": ["matplotlib"],
    "Seaborn": ["seaborn"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Excel": ["excel", "ms excel", "microsoft excel"],
    "Statistics": ["statistics", "statistical analysis"],
    # Web / backend
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "React": ["react", "reactjs", "react.js"],
    "Node.js": ["node.js", "nodejs", "node js"],
    "Django": ["django"],
    "Flask": ["flask"],
    "FastAPI": ["fastapi"],
    "Streamlit": ["streamlit"],
    "REST API": ["rest api", "restful api", "rest apis", "restful apis"],
    "MongoDB": ["mongodb", "mongo db"],
    # Tools / cloud
    "Git": ["git"],
    "GitHub": ["github"],
    "Docker": ["docker"],
    "Linux": ["linux"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure"],
    "GCP": ["gcp", "google cloud"],
    "CI/CD": ["ci/cd", "cicd"],
    # Soft / process
    "Problem Solving": ["problem solving", "problem-solving"],
    "Communication": ["communication skills", "communication"],
    "Teamwork": ["teamwork", "team player", "collaboration"],
    "Agile": ["agile", "scrum"],
}


def _alias_pattern(alias: str) -> re.Pattern:
    # Not preceded/followed by letters, digits, + or # so "java" != "javascript"
    # and "c" != "css".
    return re.compile(
        r"(?<![A-Za-z0-9+#])" + re.escape(alias) + r"(?![A-Za-z0-9+#])",
        re.IGNORECASE,
    )


_PATTERNS = {
    skill: [_alias_pattern(a) for a in aliases]
    for skill, aliases in SKILLS.items()
}


def find_skills(text: str) -> list:
    """Return the skills found in text, without duplicates,
    in the order they first appear."""
    if not text:
        return []
    found = []  # (position, skill)
    for skill, patterns in _PATTERNS.items():
        positions = []
        for p in patterns:
            m = p.search(text)
            if m:
                positions.append(m.start())
        if positions:
            found.append((min(positions), skill))
    found.sort()
    return [skill for _, skill in found]


def extract_skills(text: str) -> set:
    """Skills found in a resume, as a set for fast lookup."""
    return set(find_skills(text))

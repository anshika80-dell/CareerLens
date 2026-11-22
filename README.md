
# 🎯 CareerLens
### Resume Intelligence & Job Matching Platform

CareerLens is a Python-based resume analyzer that helps users understand how well their resume matches a given job description.

It extracts information from PDF resumes, identifies technical skills, compares them with job requirements, calculates text similarity, and generates a downloadable PDF report.

## ✨ Features

- 📄 PDF Resume Parsing
- 🧠 Automatic Skill Extraction
- ✅ Matched Skills Identification
- ❌ Missing Skills Identification
- 📊 Skill Match Percentage
- 🔍 NLP-Based Text Similarity
- 📈 Visual Analysis Dashboard
- 📥 Downloadable PDF Report

## 🛠️ Technologies Used

- Python
- Streamlit
- PyMuPDF
- pypdf
- Scikit-learn
- Pandas
- ReportLab
- Regular Expressions

## ⚙️ How It Works

1. Upload your resume in PDF format.
2. Paste the job description.
3. CareerLens extracts text from your resume.
4. It identifies skills in both texts.
5. It displays matched and missing skills.
6. It calculates TF-IDF cosine similarity.
7. Download your analysis report.

## 🚀 Installation & Setup

Clone the repository:

```bash
git clone https://github.com/anshika80-dell/CareerLens
```

Move into the project directory:

```bash
cd "career lense"
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

## 📊 Similarity Calculation

CareerLens uses TF-IDF and Cosine Similarity to measure text similarity between a resume and a job description.

**Note:** The similarity score is a text-based comparison, not an official ATS score or hiring probability.

## 👩‍💻 Developed With

Python and Streamlit

---

⭐ If you find this project useful, feel free to explore the repository!


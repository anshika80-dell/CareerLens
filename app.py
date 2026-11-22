import streamlit as st
import pandas as pd
from io import BytesIO
from html import escape

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from resume_parser import extract_text_from_pdf
from skill_extractor import extract_skills, find_skills
from nlp_matcher import calculate_similarity


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="CareerLens | Resume Analyzer",
    page_icon="🎯",
    layout="wide"
)


# ==================================================
# HELPERS
# ==================================================

def html(markup: str):
    """Render HTML safely in Streamlit.
    Removes indentation/blank lines so Markdown never treats it as a code block."""
    flat = "".join(line.strip() for line in markup.strip().splitlines())
    st.markdown(flat, unsafe_allow_html=True)


def section_title(icon: str, title: str, subtitle: str = ""):
    sub = f'<div class="sec-sub">{escape(subtitle)}</div>' if subtitle else ""
    html(f"""
    <div class="sec-head">
        <div class="sec-icon">{icon}</div>
        <div>
            <div class="sec-title">{escape(title)}</div>
            {sub}
        </div>
    </div>
    """)


def banner(kind: str, message: str):
    icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
    html(f"""
    <div class="banner banner-{kind}">
        <span class="banner-icon">{icons.get(kind, "ℹ️")}</span>
        <span>{escape(message)}</span>
    </div>
    """)


# ==================================================
# CSS - LIGHT PROFESSIONAL THEME
# ==================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, .stApp, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
}

/* ---------- Base ---------- */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #F4F7FD !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1150px;
}

.stMarkdown p, .stMarkdown li, label, .stCaption {
    color: #334155 !important;
}

hr { border-color: #DCE4F0 !important; }

/* ---------- Hero ---------- */
.hero {
    background: linear-gradient(120deg, #1E3A8A 0%, #2563EB 55%, #0EA5E9 100%);
    border-radius: 22px;
    padding: 38px 40px;
    color: #FFFFFF;
    box-shadow: 0 14px 34px rgba(37, 99, 235, 0.25);
    margin-bottom: 22px;
}
.hero-title {
    font-size: 44px;
    font-weight: 800;
    letter-spacing: -1px;
    color: #FFFFFF !important;
    line-height: 1.1;
}
.hero-sub {
    font-size: 18px;
    font-weight: 600;
    color: #DBEAFE !important;
    margin-top: 8px;
}
.hero-desc {
    font-size: 14.5px;
    color: #BFDBFE !important;
    margin-top: 6px;
}
.hero-chips { margin-top: 18px; }
.hero-chip {
    display: inline-block;
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.28);
    color: #FFFFFF !important;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    margin: 0 8px 8px 0;
}

/* ---------- Steps ---------- */
.steps { display: flex; gap: 14px; margin-bottom: 8px; flex-wrap: wrap; }
.step {
    flex: 1; min-width: 200px;
    background: #FFFFFF;
    border: 1px solid #DCE4F0;
    border-radius: 14px;
    padding: 14px 18px;
    display: flex; align-items: center; gap: 12px;
}
.step-num {
    width: 32px; height: 32px; border-radius: 50%;
    background: #2563EB; color: #FFFFFF !important;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 14px; flex-shrink: 0;
}
.step-text { color: #172554 !important; font-weight: 600; font-size: 14px; }

/* ---------- Section headings ---------- */
.sec-head {
    display: flex; align-items: center; gap: 14px;
    margin: 34px 0 14px 0;
}
.sec-icon {
    width: 44px; height: 44px; border-radius: 12px;
    background: #DBEAFE;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
}
.sec-title { font-size: 24px; font-weight: 800; color: #172554 !important; line-height: 1.2; }
.sec-sub { font-size: 13.5px; color: #64748B !important; margin-top: 2px; }

/* ---------- Tip card ---------- */
.tip-card {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-left: 6px solid #F59E0B;
    border-radius: 14px;
    padding: 16px 20px;
    margin: 6px 0 14px 0;
}
.tip-title { font-weight: 800; color: #92400E !important; font-size: 15px; margin-bottom: 4px; }
.tip-text { color: #78350F !important; font-size: 14px; line-height: 1.6; }

/* ---------- File uploader (fix dark chip) ---------- */
[data-testid="stFileUploader"] {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 14px !important;
    padding: 16px !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: #F8FAFF !important;
    border: 2px dashed #93C5FD !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploaderDropzone"] * { color: #1E3A8A !important; }
[data-testid="stFileUploaderDropzone"] button {
    background: #FFFFFF !important;
    border: 1px solid #93C5FD !important;
    color: #1E3A8A !important;
}

/* uploaded file chip */
[data-testid="stFileUploaderFile"],
[data-testid="stFileUploaderFile"] > div,
[data-testid="stFileUploaderFile"] div {
    background: #EFF6FF !important;
    color: #172554 !important;
    -webkit-text-fill-color: #172554 !important;
}
[data-testid="stFileUploaderFile"] {
    border: 1px solid #BFDBFE !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploaderFile"] small,
[data-testid="stFileUploaderFile"] span,
[data-testid="stFileUploaderFileName"] {
    color: #172554 !important;
    -webkit-text-fill-color: #172554 !important;
    opacity: 1 !important;
}
[data-testid="stFileUploaderFile"] svg,
[data-testid="stFileUploaderDeleteBtn"] svg { fill: #1E3A8A !important; color: #1E3A8A !important; }
[data-testid="stFileUploaderFile"] button { background: transparent !important; }

/* ---------- Text area ---------- */
.stTextArea textarea {
    background: #FFFFFF !important;
    color: #172554 !important;
    -webkit-text-fill-color: #172554 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 12px !important;
    font-size: 14.5px !important;
}
.stTextArea textarea::placeholder {
    color: #94A3B8 !important;
    -webkit-text-fill-color: #94A3B8 !important;
    opacity: 1 !important;
}
.stTextArea textarea:focus { border-color: #2563EB !important; box-shadow: 0 0 0 1px #2563EB !important; }

/* ---------- Buttons ---------- */
.stButton > button,
.stDownloadButton > button {
    background: linear-gradient(90deg, #2563EB, #1D4ED8) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    min-height: 50px;
    box-shadow: 0 8px 18px rgba(37, 99, 235, 0.25);
}
.stButton > button *, .stDownloadButton > button * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: linear-gradient(90deg, #1D4ED8, #1E3A8A) !important;
}

/* ---------- Banners ---------- */
.banner {
    display: flex; align-items: center; gap: 10px;
    padding: 14px 18px; border-radius: 12px;
    font-weight: 600; font-size: 14.5px; margin: 10px 0;
}
.banner-success { background: #E8F7EF; border: 1px solid #A7E0BD; color: #14532D !important; }
.banner-error   { background: #FEF2F2; border: 1px solid #FECACA; color: #991B1B !important; }
.banner-warning { background: #FFFBEB; border: 1px solid #FDE68A; color: #92400E !important; }
.banner span { color: inherit !important; }
.banner-icon { font-size: 18px; }

/* ---------- Score cards ---------- */
.score-grid { display: flex; gap: 16px; flex-wrap: wrap; }
.score-card {
    flex: 1; min-width: 220px;
    background: #FFFFFF;
    border: 1px solid #DCE4F0;
    border-radius: 16px;
    padding: 20px 22px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
}
.score-label { font-size: 13.5px; font-weight: 700; color: #64748B !important; }
.score-value { font-size: 38px; font-weight: 800; color: #172554 !important; margin-top: 4px; }
.score-note { font-size: 12.5px; color: #94A3B8 !important; margin-top: 2px; }
.c-blue  { border-top: 5px solid #2563EB; }
.c-teal  { border-top: 5px solid #0EA5E9; }
.c-green { border-top: 5px solid #16A34A; }
.c-red   { border-top: 5px solid #DC2626; }

/* ---------- Custom progress bar ---------- */
.prog-wrap {
    background: #FFFFFF; border: 1px solid #DCE4F0;
    border-radius: 16px; padding: 20px 22px;
}
.prog-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.prog-text { font-weight: 700; color: #172554 !important; font-size: 15px; }
.prog-badge { padding: 5px 14px; border-radius: 999px; font-weight: 700; font-size: 13px; }
.badge-good { background: #DCFCE7; color: #166534 !important; }
.badge-mid  { background: #FEF3C7; color: #92400E !important; }
.badge-low  { background: #FEE2E2; color: #991B1B !important; }
.prog-track { width: 100%; height: 16px; background: #E2E8F0; border-radius: 999px; overflow: hidden; }
.prog-fill  { height: 100%; border-radius: 999px; }
.fill-good { background: linear-gradient(90deg, #22C55E, #16A34A); }
.fill-mid  { background: linear-gradient(90deg, #FBBF24, #F59E0B); }
.fill-low  { background: linear-gradient(90deg, #F87171, #DC2626); }
.prog-cap  { font-size: 12.5px; color: #64748B !important; margin-top: 12px; }

/* ---------- Matched / Missing cards ---------- */
.skill-card {
    border-radius: 18px; padding: 22px; min-height: 200px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
}
.matched-card { background: #ECFDF3; border: 1px solid #A7E0BD; }
.missing-card { background: #FFF5F5; border: 1px solid #FECACA; }
.card-head { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
.card-badge {
    width: 40px; height: 40px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; font-weight: 800; color: #FFFFFF !important;
}
.badge-green { background: #16A34A; }
.badge-red   { background: #DC2626; }
.card-title-g { font-size: 20px; font-weight: 800; color: #166534 !important; }
.card-title-r { font-size: 20px; font-weight: 800; color: #991B1B !important; }
.card-count { font-size: 12.5px; font-weight: 600; margin-top: 1px; }
.cnt-g { color: #15803D !important; }
.cnt-r { color: #B91C1C !important; }

.chip {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 7px 14px; border-radius: 999px;
    font-size: 14px; font-weight: 600; margin: 0 8px 10px 0;
}
.chip-g { background: #FFFFFF; border: 1px solid #86EFAC; color: #14532D !important; }
.chip-r { background: #FFFFFF; border: 1px solid #FCA5A5; color: #7F1D1D !important; }
.empty-note { font-size: 14px; font-style: italic; }
.empty-g { color: #166534 !important; }
.empty-r { color: #991B1B !important; }

/* ---------- Expander (fix invisible text) ---------- */
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 14px !important;
}
[data-testid="stExpander"] details,
[data-testid="stExpander"] summary {
    background: #FFFFFF !important;
    border-radius: 14px !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary *,
[data-testid="stExpander"] summary p {
    color: #172554 !important;
    -webkit-text-fill-color: #172554 !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}
[data-testid="stExpander"] summary svg { fill: #172554 !important; color: #172554 !important; }

.resume-box {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 18px;
    max-height: 340px;
    overflow-y: auto;
    white-space: pre-wrap;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13.5px;
    line-height: 1.7;
    color: #1E293B !important;
}

/* ---------- Suggestion cards ---------- */
.sug-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
.sug-card {
    background: #FFFFFF;
    border: 1px solid #DCE4F0;
    border-left: 6px solid #F59E0B;
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
}
.sug-top { display: flex; align-items: center; gap: 10px; }
.sug-icon { font-size: 20px; }
.sug-skill { font-size: 17px; font-weight: 800; color: #172554 !important; }
.sug-text { font-size: 13.5px; color: #475569 !important; margin-top: 8px; line-height: 1.55; }
.sug-tag {
    display: inline-block; margin-top: 10px;
    background: #FEF3C7; color: #92400E !important;
    padding: 4px 12px; border-radius: 999px;
    font-size: 12px; font-weight: 700;
}
.all-good {
    background: #ECFDF3; border: 1px solid #A7E0BD; border-radius: 16px;
    padding: 22px; color: #14532D !important; font-weight: 600; font-size: 15px;
}

/* ---------- Instruction card ---------- */
.info-card {
    background: linear-gradient(135deg, #EFF6FF, #E0F2FE);
    border: 1px solid #BFDBFE;
    border-radius: 18px;
    padding: 24px 26px;
}
.info-title { font-size: 19px; font-weight: 800; color: #1E3A8A !important; margin-bottom: 12px; }
.info-list { margin: 0; padding-left: 0; list-style: none; }
.info-list li {
    color: #1E3A8A !important;
    font-size: 14.5px; line-height: 1.65;
    padding: 8px 0 8px 34px; position: relative;
}
.info-list li::before {
    content: "✔"; position: absolute; left: 0; top: 8px;
    width: 22px; height: 22px; border-radius: 50%;
    background: #2563EB; color: #FFFFFF;
    font-size: 12px; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
}

/* ---------- Footer ---------- */
.footer { text-align: center; color: #64748B !important; font-size: 13px; padding-top: 25px; }

</style>
""", unsafe_allow_html=True)


# ==================================================
# HERO HEADER
# ==================================================

html("""
<div class="hero">
    <div class="hero-title">🎯 CareerLens</div>
    <div class="hero-sub">Resume Intelligence &amp; Job Matching Platform</div>
    <div class="hero-desc">Understand your strengths. Discover skill gaps. Make your next career move with confidence.</div>
    <div class="hero-chips">
        <span class="hero-chip">📄 Resume Parsing</span>
        <span class="hero-chip">🧠 Skill Matching</span>
        <span class="hero-chip">📊 Similarity Score</span>
        <span class="hero-chip">📥 PDF Report</span>
    </div>
</div>
""")

html("""
<div class="steps">
    <div class="step"><div class="step-num">1</div><div class="step-text">Upload your resume PDF</div></div>
    <div class="step"><div class="step-num">2</div><div class="step-text">Paste the job description</div></div>
    <div class="step"><div class="step-num">3</div><div class="step-text">Get your analysis report</div></div>
</div>
""")


# ==================================================
# RESUME UPLOAD
# ==================================================

section_title("📄", "Upload Your Resume", "Use a text-based PDF (not a scanned image).")

html("""
<div class="tip-card">
    <div class="tip-title">💡 Before you upload</div>
    <div class="tip-text">
        If you know a skill but it is not written in your resume, add it first
        (only if you really have it). The analyzer can only match skills that are
        written in your resume.
    </div>
</div>
""")

uploaded_file = st.file_uploader(
    "Choose your resume PDF",
    type=["pdf"],
    help="Upload a text-based PDF resume."
)

if uploaded_file is not None:
    banner("success", f"Resume uploaded successfully: {uploaded_file.name}")


# ==================================================
# JOB DESCRIPTION
# ==================================================

section_title("💼", "Job Description", "Paste the complete job posting for the best results.")

job_description = st.text_area(
    "Paste the job description here",
    height=200,
    placeholder="Paste the complete job description here...",
    label_visibility="collapsed"
)

analyze = st.button(
    "🔍 Analyze My Resume",
    use_container_width=True
)


# ==================================================
# PDF REPORT FUNCTION
# ==================================================

def create_pdf_report(
    matched_skills,
    missing_skills,
    skill_score,
    similarity_score
):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        textColor=colors.HexColor("#1E3A8A"),
        fontSize=22
    )

    normal_style = ParagraphStyle(
        "ReportNormal",
        parent=styles["Normal"],
        textColor=colors.HexColor("#172554"),
        fontSize=11,
        leading=17
    )

    elements = []

    elements.append(
        Paragraph("CareerLens - Resume Analysis Report", title_style)
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"<b>Skill Match:</b> {skill_score}%",
            normal_style
        )
    )

    elements.append(
        Paragraph(
            f"<b>Text Similarity:</b> {similarity_score}%",
            normal_style
        )
    )

    elements.append(Spacer(1, 15))

    elements.append(
        Paragraph("<b>Matched Skills</b>", normal_style)
    )

    elements.append(
        Paragraph(
            escape(", ".join(matched_skills) if matched_skills else "None"),
            normal_style
        )
    )

    elements.append(Spacer(1, 15))

    elements.append(
        Paragraph("<b>Missing Skills</b>", normal_style)
    )

    elements.append(
        Paragraph(
            escape(", ".join(missing_skills) if missing_skills else "None"),
            normal_style
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "Skill matching is based on predefined keywords. "
            "Text similarity uses TF-IDF and cosine similarity. "
            "These are not official ATS scores or hiring predictions.",
            normal_style
        )
    )

    doc.build(elements)

    buffer.seek(0)

    return buffer


# ==================================================
# ANALYSIS
# ==================================================

if analyze:

    if uploaded_file is None:

        banner("error", "Please upload your resume PDF first.")

    elif not job_description.strip():

        banner("error", "Please paste a job description to compare against.")

    else:

        try:

            with st.spinner("Analyzing your resume..."):

                resume_text = extract_text_from_pdf(uploaded_file)

                if not resume_text.strip():
                    banner(
                        "error",
                        "No readable text found in this PDF. "
                        "Please upload a text-based resume."
                    )
                    st.stop()

                resume_skills = extract_skills(resume_text)

                job_skills = find_skills(job_description)

                matched_skills = [
                    skill for skill in job_skills
                    if skill in resume_skills
                ]

                missing_skills = [
                    skill for skill in job_skills
                    if skill not in resume_skills
                ]

                if job_skills:
                    skill_score = round(
                        len(matched_skills) / len(job_skills) * 100,
                        2
                    )
                else:
                    skill_score = 0

                similarity_score = calculate_similarity(
                    resume_text,
                    job_description
                )

            # ======================================
            # SUCCESS MESSAGE
            # ======================================

            banner("success", "Resume analysis completed successfully!")

            # ======================================
            # DASHBOARD
            # ======================================

            section_title("📊", "Your Analysis Dashboard", "A quick snapshot of how your resume fits this job.")

            html(f"""
            <div class="score-grid">
                <div class="score-card c-blue">
                    <div class="score-label">🎯 Skill Match</div>
                    <div class="score-value">{skill_score}%</div>
                    <div class="score-note">Job skills found in your resume</div>
                </div>
                <div class="score-card c-teal">
                    <div class="score-label">📝 Text Similarity</div>
                    <div class="score-value">{similarity_score}%</div>
                    <div class="score-note">TF-IDF + cosine similarity</div>
                </div>
                <div class="score-card c-green">
                    <div class="score-label">✅ Matched Skills</div>
                    <div class="score-value">{len(matched_skills)}</div>
                    <div class="score-note">Skills you already have</div>
                </div>
                <div class="score-card c-red">
                    <div class="score-label">⚠️ Missing Skills</div>
                    <div class="score-value">{len(missing_skills)}</div>
                    <div class="score-note">Skills to work on</div>
                </div>
            </div>
            """)

            # ======================================
            # SKILL MATCH PROGRESS
            # ======================================

            section_title("🎯", "Overall Skill Match")

            if skill_score >= 70:
                level, verdict = "good", "Strong match"
            elif skill_score >= 40:
                level, verdict = "mid", "Moderate match"
            else:
                level, verdict = "low", "Needs improvement"

            bar_width = max(0, min(100, float(skill_score)))

            html(f"""
            <div class="prog-wrap">
                <div class="prog-top">
                    <div class="prog-text">Your skill match is {skill_score}%</div>
                    <div class="prog-badge badge-{level}">{verdict}</div>
                </div>
                <div class="prog-track">
                    <div class="prog-fill fill-{level}" style="width:{bar_width}%;"></div>
                </div>
                <div class="prog-cap">
                    This percentage shows the share of recognized job-description skills
                    also found in your resume's recognized skills section.
                </div>
            </div>
            """)

            # ======================================
            # MATCHED AND MISSING SKILLS
            # ======================================

            section_title("🧠", "Skills Breakdown", "What you already have vs. what the job asks for.")

            left, right = st.columns(2)

            if matched_skills:
                matched_html = "".join(
                    f'<span class="chip chip-g">✅ {escape(skill)}</span>'
                    for skill in matched_skills
                )
            else:
                matched_html = '<div class="empty-note empty-g">No matched skills found.</div>'

            if missing_skills:
                missing_html = "".join(
                    f'<span class="chip chip-r">⚠️ {escape(skill)}</span>'
                    for skill in missing_skills
                )
            else:
                missing_html = '<div class="empty-note empty-r">Great! No missing skills found.</div>'

            with left:
                html(f"""
                <div class="skill-card matched-card">
                    <div class="card-head">
                        <div class="card-badge badge-green">✓</div>
                        <div>
                            <div class="card-title-g">Matched Skills</div>
                            <div class="card-count cnt-g">{len(matched_skills)} found in your resume</div>
                        </div>
                    </div>
                    <div>{matched_html}</div>
                </div>
                """)

            with right:
                html(f"""
                <div class="skill-card missing-card">
                    <div class="card-head">
                        <div class="card-badge badge-red">!</div>
                        <div>
                            <div class="card-title-r">Missing Skills</div>
                            <div class="card-count cnt-r">{len(missing_skills)} not found in your resume</div>
                        </div>
                    </div>
                    <div>{missing_html}</div>
                </div>
                """)

            # ======================================
            # BAR GRAPH
            # ======================================

            section_title("📈", "Matched vs Missing Skills")

            chart_data = pd.DataFrame({
                "Skill Category": [
                    "Matched Skills",
                    "Missing Skills"
                ],
                "Number of Skills": [
                    len(matched_skills),
                    len(missing_skills)
                ]
            })

            st.bar_chart(
                chart_data,
                x="Skill Category",
                y="Number of Skills",
                color="#3B82F6"
            )

            st.caption(
                "How to read this graph: The taller bar represents the category "
                "with more skills. The numbers show how many skills matched "
                "or were missing from your resume."
            )

            # ======================================
            # RESUME TEXT PREVIEW
            # ======================================

            section_title("📃", "Extracted Resume Text", "Check that your PDF was read correctly.")

            with st.expander("View the text extracted from your uploaded resume"):
                st.markdown(
                    f'<div class="resume-box">{escape(resume_text)}</div>',
                    unsafe_allow_html=True
                )

            # ======================================
            # SUGGESTIONS
            # ======================================

            section_title("💡", "Improvement Suggestions", "Skills worth adding or learning for this role.")

            if missing_skills:

                cards = "".join(
                    f"""
                    <div class="sug-card">
                        <div class="sug-top">
                            <div class="sug-icon">⚠️</div>
                            <div class="sug-skill">{escape(skill)}</div>
                        </div>
                        <div class="sug-text">
                            Required by the job but not found in your resume.
                            Add it if you already know it, or add it to your learning plan.
                        </div>
                        <span class="sug-tag">Priority skill</span>
                    </div>
                    """
                    for skill in missing_skills
                )

                html(f'<div class="sug-grid">{cards}</div>')

            else:

                html("""
                <div class="all-good">
                    🎉 All recognized skills from this job description were found
                    in your resume's recognized skills section. Nice work!
                </div>
                """)

            # ======================================
            # PDF DOWNLOAD
            # ======================================

            section_title("📥", "Download Your Report")

            pdf_file = create_pdf_report(
                matched_skills,
                missing_skills,
                skill_score,
                similarity_score
            )

            st.download_button(
                label="⬇️ Download Analysis Report",
                data=pdf_file,
                file_name="CareerLens_Analysis_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

            st.caption(
                "Note: Skill Match is keyword-based. Text Similarity uses "
                "TF-IDF and cosine similarity. Neither is an official ATS score."
            )

            # ======================================
            # GENERAL INSTRUCTIONS (LAST)
            # ======================================

            section_title("📌", "General Instructions", "Read this to get more accurate results.")

            html("""
            <div class="info-card">
                <div class="info-title">Before you upload your resume</div>
                <ul class="info-list">
                    <li>If you know a skill but it is not written in your resume, add it first
                        (only if you truly have it), then upload again.</li>
                    <li>Use the exact skill names, for example "Machine Learning", "SQL", "Python",
                        so the matcher can recognize them.</li>
                    <li>Keep a clear <b>Skills</b> section in your resume and list projects with the tools you used.</li>
                    <li>Upload a text-based PDF. Scanned or image-only PDFs cannot be read.</li>
                    <li>Paste the complete job description for a more accurate comparison.</li>
                </ul>
            </div>
            """)

        except Exception as error:

            banner("error", f"Analysis error: {error}")
            st.exception(error)  # shows the full traceback while debugging


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.markdown(
    '<div class="footer">CareerLens | Resume Intelligence &amp; Job Matching Platform</div>',
    unsafe_allow_html=True
)

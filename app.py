from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
import PyPDF2
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# =========================
# Helper Functions
# =========================
def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    # pdf_content is plain text now
    response = model.generate_content([input, pdf_content, prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    """Extract text from uploaded PDF using PyPDF2"""
    if uploaded_file is not None:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        if not text.strip():
            text = "⚠️ Could not extract text from this PDF. It might be scanned or image-based."
        return text
    else:
        raise FileNotFoundError("No file uploaded")

def format_response(response):
    """Format AI response into clean markdown"""
    return f"""
    <div class="response-box">
        <p>{response}</p>
    </div>
    """

def create_pdf(report_title, content):
    """Generate a PDF and return as BytesIO"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, report_title)

    c.setFont("Helvetica", 11)

    y = height - 80
    for line in content.split("\n"):
        if y < 50:  # New page if space ends
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - 50
        c.drawString(50, y, line)
        y -= 15

    c.save()
    buffer.seek(0)
    return buffer

# =========================
# Streamlit App UI
# =========================
st.set_page_config(page_title="ATS Resume Expert", layout="centered")

# Inject CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f0f8ff, #e6f2ff);
    }
    h1 {
        color: #003366 !important;
        text-align: center;
        font-family: 'Trebuchet MS', sans-serif;
    }
    textarea {
        border: 2px solid #003366 !important;
        border-radius: 10px !important;
        padding: 10px !important;
        font-size: 15px !important;
    }
    div.stButton > button {
        background-color: #003366;
        color: white;
        border-radius: 10px;
        padding: 8px 16px;
        border: none;
        font-size: 16px;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #0059b3;
        transform: scale(1.05);
    }
    .response-box {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        border-left: 6px solid #003366;
        font-size: 16px;
        line-height: 1.6;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 ATS Resume Expert")
st.write("Upload your resume and job description to get a professional ATS-style analysis.")

# Inputs
input_text = st.text_area("📝 Job Description", placeholder="Paste the job description here...")
uploaded_file = st.file_uploader("📂 Upload your resume (PDF only)", type=["pdf"])

if uploaded_file is not None:
    st.success("✅ PDF Uploaded Successfully!")

# Buttons in row
col1, col2, col3 = st.columns(3)
with col1:
    submit1 = st.button("📄 Resume Review")
with col2:
    submit2 = st.button("🎯 Skill Improvement")
with col3:
    submit3 = st.button("📊 Match Percentage")

# Prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager. Review the provided resume against the job description. 
Share a professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt2 = """
You are a career coach with expertise in ATS and resume optimization.
Based on the resume and job description, suggest specific skills,
certifications, or tools the candidate should learn or improve
to increase their chances of getting shortlisted.
Provide practical, actionable advice in bullet points.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of ATS functionality. 
Evaluate the resume against the provided job description. 
First, give the **percentage match**, then list **missing keywords**, and finally provide **final thoughts**.
"""

# =========================
# Actions
# =========================
if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        with st.spinner("🔍 Analyzing resume... Please wait ⏳"):
            response = get_gemini_response(input_prompt1, pdf_content, input_text)
        st.subheader("📄 HR Review")
        st.markdown(format_response(response), unsafe_allow_html=True)

        pdf_buffer = create_pdf("Resume Review Report", response)
        st.download_button("⬇️ Download Report as PDF", pdf_buffer, file_name="resume_review.pdf", mime="application/pdf")

    else:
        st.warning("⚠️ Please upload a resume.")

elif submit2:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        with st.spinner("🎯 Finding skill gaps... Please wait ⏳"):
            response = get_gemini_response(input_prompt2, pdf_content, input_text)
        st.subheader("🎯 Skill Improvement Suggestions")
        st.markdown(format_response(response), unsafe_allow_html=True)

        pdf_buffer = create_pdf("Skill Improvement Report", response)
        st.download_button("⬇️ Download Report as PDF", pdf_buffer, file_name="skill_improvement.pdf", mime="application/pdf")

    else:
        st.warning("⚠️ Please upload a resume.")

elif submit3:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        with st.spinner("📊 Calculating ATS Match... Please wait ⏳"):
            response = get_gemini_response(input_prompt3, pdf_content, input_text)
        st.subheader("📊 Match Percentage & Analysis")
        st.markdown(format_response(response), unsafe_allow_html=True)

        pdf_buffer = create_pdf("ATS Match Report", response)
        st.download_button("⬇️ Download Report as PDF", pdf_buffer, file_name="ats_match.pdf", mime="application/pdf")

    else:
        st.warning("⚠️ Please upload a resume.")

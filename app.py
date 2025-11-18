import streamlit as st
import io
from PyPDF2 import PdfReader
import streamlit as st
import io
from PyPDF2 import PdfReader
from knowledge_base import KNOWLEDGE_BASE_DATA
import uuid
import firebase_admin
from firebase_admin import credentials, firestore


# Initialize Firebase (only initialize once)
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase_service_account"]))
    firebase_admin.initialize_app(cred)
db = firestore.client()


# --- TOP 10 job roles' skills pooled together
TOP_SKILLS = {
    "Product Management", "AI Technologies", "UX Design", "Agile", "Communication", "Data Strategy",
    "Data Analysis", "Business Strategy", "Python", "SQL", "Visualization",
    "TensorFlow", "PyTorch", "Algorithms", "Model Deployment", "Cloud Platforms",
    "Power BI", "Tableau", "Data Warehousing", "Reporting", "Strategic Thinking",
    "Strategic Planning", "Emerging Tech", "AI Trends", "Leadership", "Risk Management",
    "AI Policy", "Ethics", "Compliance", "Risk Analysis", "Legal Awareness",
    "Marketing Analytics", "CRM Tools", "A/B Testing", "Data Interpretation", "Strategy",
    "Change Management", "Tech Integration", "AI Adoption", "Business Modeling",
    "Data Governance", "Data Architecture", "Market Analysis", "AI Solutions", "Sales Strategy", "Negotiation", "Tech Fluency"
}

BEST_PLATFORMS = {
    "Coursera": "https://www.coursera.org",
    "edX": "https://www.edx.org",
    "Udemy": "https://www.udemy.com",
    "LinkedIn Learning": "https://www.linkedin.com/learning/",
    "FutureLearn": "https://www.futurelearn.com",
    "Khan Academy": "https://www.khanacademy.org",
    "Pluralsight": "https://www.pluralsight.com",
    "DataCamp": "https://www.datacamp.com",
    "Codecademy": "https://www.codecademy.com",
    "BCG": "https://www.bcg.com/capabilities/digital-transformation",
    "Trailhead": "https://trailhead.salesforce.com",
    "Udacity": "https://www.udacity.com",
}

def signup(email, password):
    st.error("Demo: Signup disabled for Firebase Auth via Admin SDK. Use client-side or REST API for real email/password registration!")
    return None, "Signup not implemented"

def signin(email, password):
    st.error("Demo: Signin disabled for Firebase Auth via Admin SDK. Use client-side or REST API for real email/password authentication!")
    return None, "Signin not implemented"

def signout():
    st.session_state["user"] = None
    return True, None

def send_password_reset_email(email):
    st.error("Demo: Password reset disabled for Firebase Auth via Admin SDK. Use client-side or REST API for real password reset!")
    return False, "Reset not implemented"

def show_signup():
    st.header("Create Account")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_pw")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_pw")
    if st.button("Sign Up"):
        st.error("Signup is for demonstration only. Use Firebase Auth SDK or REST for actual user registration.")
    if st.button("Go to Sign In", key="to_login_from_signup"):
        st.session_state.page = "login"
        st.rerun()

def show_login():
    st.header("Sign In")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_pw")
    if st.button("Sign In"):
        st.error("Sign In is for demonstration only. Use Firebase Auth SDK or REST for actual authentication.")
        st.session_state["user"] = {"email": email}
        st.session_state.page = "main"
        st.rerun()
    if st.button("Create Account", key="to_signup_from_login"):
        st.session_state.page = "signup"
        st.rerun()
    if st.button("Forgot Password?", key="to_reset_from_login"):
        st.session_state.page = "reset"
        st.rerun()

def show_reset_password():
    st.header("Reset Password")
    email = st.text_input("Enter your email to reset password", key="reset_email")
    if st.button("Send Reset Link"):
        st.error("Password reset is for demonstration only. Use Firebase Auth SDK or REST for actual password reset.")
    if st.button("Back to Sign In", key="to_login_from_reset"):
        st.session_state.page = "login"
        st.rerun()

def show_main_app():
    st.title("🌟 Career Roadmap Generator")
    st.sidebar.success(f"Logged in as: {st.session_state['user']['email']}")
    if st.sidebar.button("Logout"):
        signout()
        st.session_state.page = "login"
        st.sidebar.info("Logged out.")
        st.rerun()

    st.write("---")
    st.subheader("🎯 Upload and Analyze Your Resume")
    st.caption("Upload your PDF and generate a personalized career roadmap!")

    uploaded_file = st.file_uploader("Upload your resume", type=["pdf"])
    st.caption("Limit 5MB per file • PDF only")

    user_skills = []
    if uploaded_file:
        if uploaded_file.size > 5 * 1024 * 1024:
            st.error("File too large! Please upload a PDF smaller than 5 MB.")
        else:
            with st.expander("Extracted Resume Skills", expanded=True):
                text = extract_text_from_pdf_uploaded_file(uploaded_file)
                user_skills = top10_skill_extractor(text)
                # Save resume text and skills to Firestore
                db.collection("resumes").add({
                    "email": st.session_state['user']['email'],
                    "resume_text": text,
                    "extracted_skills": user_skills,
                    "doc_id": str(uuid.uuid4())
                })
                if user_skills:
                    st.success(f"Skills found: {', '.join(user_skills)}")
                else:
                    st.warning("No skills found.")

    target_job = st.selectbox("👔 Target Job Role", [role['job_title'] for role in KNOWLEDGE_BASE_DATA])
    if st.button("Generate Roadmap 🗺️"):
        missing_skills, recommendations = gap_analysis(user_skills, target_job)
        st.write("---")
        st.subheader("🔑 Roadmap: Skills to Learn")
        best_platforms_lines = [
            f"[{platform}]({url})" for platform, url in BEST_PLATFORMS.items()
        ]
        if missing_skills:
            for skill in missing_skills:
                rec = recommendations.get(skill, {})
                if rec and rec.get('title') and rec.get('link'):
                    st.markdown(
                        f"**{skill}:** [{rec['title']} ({rec['platform']})]({rec['link']})",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"**{skill}:** No direct course. Explore these platforms:<br>{' | '.join(best_platforms_lines)}",
                        unsafe_allow_html=True
                    )
        else:
            st.success("You're ready for this role! No missing skills.")

    st.write("---")
    st.info("Thanks for using the Career Roadmap Generator! 🌈")

def extract_text_from_pdf_uploaded_file(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text
    except Exception:
        st.error("Sorry, couldn't read your PDF file. Please try a different file.")
        return ""

def top10_skill_extractor(text):
    extracted = set()
    text = text.lower()
    for skill in TOP_SKILLS:
        if skill.lower() in text:
            extracted.add(skill)
    return list(extracted)

def gap_analysis(user_skills, target_job):
    for role in KNOWLEDGE_BASE_DATA:
        if role["job_title"].lower() == target_job.lower():
            required_skills = set(role["required_skills"])
            user_skills_set = set(user_skills)
            missing_skills = required_skills - user_skills_set
            recommendations = {skill: role['course_recommendations'].get(skill, {}) for skill in missing_skills}
            return list(missing_skills), recommendations
    return [], {}

# Session State Navigation
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user" in st.session_state and st.session_state["user"]:
    st.session_state.page = "main"

# Navigation logic
if st.session_state.page == "login":
    show_login()
elif st.session_state.page == "signup":
    show_signup()
elif st.session_state.page == "reset":
    show_reset_password()
elif st.session_state.page == "main":
    show_main_app()
else:
    show_login()

import streamlit as st
import requests
import PyPDF2 # pip install PyPDF2 to extract text from PDF

st.set_page_config(page_title="AI Resume Tailor", layout="wide")

st.title("📄 Multi-Agent Resume & CV Generator")
st.markdown("Upload your current resume and provide a job URL to generate tailored documents.")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("Upload Details")
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])
    job_url = st.text_input("Job Description URL", placeholder="https://careers.company.com/job/123")
    
    generate_btn = st.button("Generate Documents", type="primary")

# --- Main Logic ---
if generate_btn:
    if not uploaded_file or not job_url:
        st.error("Please provide both a resume PDF and a Job URL.")
    else:
        with st.spinner("Agents are working... (Parsing JD -> Converting YAML -> Tailoring Resume -> Writing CV)"):
            try:
                # 1. Extract text from PDF (Optional: You can send raw text to your agent)
                # pdf_reader = PyPDF2.PdfReader(uploaded_file)
                # resume_text = ""
                # for page in pdf_reader.pages:
                #     resume_text += page.extract_text()
                files = {
                        "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
                    }
                data={"job_url":job_url}
                # 2. Call your FastAPI Backend
                # Ensure your FastAPI server is running on port 8000
                api_url = "http://localhost:8000/invoke"
                # payload = 
                
                response = requests.post(api_url,files=files,data=data)
                response.raise_for_status()
                received_data_from_server = response.json()
                
                # 3. Display Results in Tabs
                output = received_data_from_server.get("output", {})
                
                tab1, tab2, tab3 = st.tabs(["📊 Job Description", "📝 Tailored Resume", "✉️ Cover Letter"])
                
                with tab1:
                    st.subheader("Extracted Job Requirements")
                    st.write(output.get("jd", "No JD extracted."))
                
                with tab2:
                    st.subheader("Tailored Resume (LaTeX/Markdown)")
                    st.code(output.get("tailored_resume", "No resume generated."), language="latex")
                    st.download_button("Download Resume", output.get("tailored_resume"), file_name="tailored_resume.tex")
                
                with tab3:
                    st.subheader("Tailored Cover Letter")
                    st.write(output.get("CV", "No CV generated."))
                    st.download_button("Download CV", output.get("CV"), file_name="cover_letter.txt")

            except Exception as e:
                st.error(f"An error occurred: {e}")

# Footer
st.divider()
st.caption("Powered by LangGraph Multi-Agent Orchestration")

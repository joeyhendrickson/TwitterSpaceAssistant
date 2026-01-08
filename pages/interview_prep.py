import os
import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
from uuid import uuid4
import json

# Load environment variables
load_dotenv()

# Initialize API clients
openai_api_key = os.getenv("OPENAI_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")

if not openai_api_key or not pinecone_api_key:
    st.error("🚨 **Configuration Error**")
    st.markdown("""
    This app requires API keys to function. Please set up the following environment variables:
    
    **Required Environment Variables:**
    - `OPENAI_API_KEY` - Your OpenAI API key
    - `PINECONE_API_KEY` - Your Pinecone API key
    """)
    st.stop()

try:
    client = OpenAI(api_key=openai_api_key)
    pc = Pinecone(api_key=pinecone_api_key)
    
    # Interview Prep specific index - use shared index with namespace
    index_name = "conversation-assistant-shared"
    
    # Check if index exists, if not create it
    try:
        index = pc.Index(index_name)
    except Exception:
        from pinecone import ServerlessSpec
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        index = pc.Index(index_name)
        
except Exception as e:
    st.error(f"🚨 **Connection Error**: {str(e)}")
    st.stop()

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        pdf = PdfReader(pdf_file)
        text = "\n".join([page.extract_text() for page in pdf.pages])
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

def analyze_resume(resume_text, resume_name="Resume"):
    """Analyze resume and extract structured information"""
    try:
        prompt = f"""
        Analyze this resume and extract key information in JSON format:
        
        Resume Text:
        {resume_text}
        
        Return a JSON object with the following structure:
        {{
            "name": "Full name",
            "email": "Email address",
            "phone": "Phone number",
            "summary": "Professional summary",
            "skills": ["skill1", "skill2", ...],
            "experience": [
                {{
                    "title": "Job title",
                    "company": "Company name",
                    "duration": "Time period",
                    "description": "Job description"
                }}
            ],
            "education": [
                {{
                    "degree": "Degree name",
                    "school": "School name",
                    "year": "Graduation year"
                }}
            ],
            "certifications": ["cert1", "cert2", ...],
            "achievements": ["achievement1", "achievement2", ...]
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        # Try to parse JSON response
        try:
            resume_data = json.loads(response.choices[0].message.content)
            resume_data['resume_name'] = resume_name
            return resume_data
        except json.JSONDecodeError:
            # Fallback: return structured data from text
            return {
                "resume_name": resume_name,
                "name": "Extracted from resume",
                "summary": response.choices[0].message.content[:500],
                "skills": [],
                "experience": [],
                "education": [],
                "certifications": [],
                "achievements": []
            }
            
    except Exception as e:
        st.error(f"Error analyzing resume: {e}")
        return None

def compare_resumes_against_job(resumes_data, job_description):
    """Compare multiple resumes against job description and analyze strengths/weaknesses"""
    try:
        # Combine all resumes into a comparison format
        resumes_summary = ""
        for i, resume in enumerate(resumes_data, 1):
            resume_name = resume.get('resume_name', f'Resume {i}')
            resumes_summary += f"""
            === {resume_name} ===
            Name: {resume.get('name', 'N/A')}
            Summary: {resume.get('summary', 'N/A')}
            Skills: {', '.join(resume.get('skills', []))}
            Experience: {len(resume.get('experience', []))} positions
            Education: {len(resume.get('education', []))} entries
            Certifications: {', '.join(resume.get('certifications', []))}
            
            """
        
        prompt = f"""
        You are an expert resume analyst and career advisor. Compare these resumes against the job description and provide a comprehensive analysis.
        
        RESUMES TO COMPARE:
        {resumes_summary}
        
        JOB DESCRIPTION:
        {job_description}
        
        Provide a detailed analysis in the following format:
        
        ## COMPARATIVE ANALYSIS
        
        ### OVERALL ASSESSMENT
        [Provide an overall assessment of how well the resumes match the job description]
        
        ### STRENGTHS (What works well across the resumes)
        [List 5-7 key strengths that align with the job requirements]
        
        ### WEAKNESSES & GAPS (What's missing or needs improvement)
        [List 5-7 weaknesses, gaps, or areas that don't align with the job requirements]
        
        ### IMPROVEMENT RECOMMENDATIONS
        [Provide specific, actionable advice on how to improve the resumes, including:
        - What to emphasize more
        - What to add
        - What to remove or de-emphasize
        - How to better align with job requirements
        - Specific keywords to include
        - Formatting suggestions]
        
        ### KEY ALIGNMENT SCORE
        [Rate how well the resumes align with the job (1-10) and explain why]
        
        Be specific, actionable, and focus on helping create a resume that will get the candidate noticed.
        """
        
        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        st.error(f"Error comparing resumes: {e}")
        return None

def generate_improved_resume(resumes_data, job_description, custom_prompt=""):
    """Generate a consolidated, improved resume based on multiple resumes and job description"""
    try:
        # Combine all resumes into a comprehensive data structure
        all_skills = set()
        all_experience = []
        all_education = []
        all_certifications = set()
        all_achievements = set()
        personal_info = {}
        
        for resume in resumes_data:
            all_skills.update(resume.get('skills', []))
            all_experience.extend(resume.get('experience', []))
            all_education.extend(resume.get('education', []))
            all_certifications.update(resume.get('certifications', []))
            all_achievements.update(resume.get('achievements', []))
            
            # Use the most complete personal info
            if not personal_info.get('name') and resume.get('name'):
                personal_info['name'] = resume.get('name')
            if not personal_info.get('email') and resume.get('email'):
                personal_info['email'] = resume.get('email')
            if not personal_info.get('phone') and resume.get('phone'):
                personal_info['phone'] = resume.get('phone')
        
        # Create comprehensive resume data
        consolidated_data = {
            "personal_info": personal_info,
            "skills": list(all_skills),
            "experience": all_experience,
            "education": all_education,
            "certifications": list(all_certifications),
            "achievements": list(all_achievements)
        }
        
        # Build the prompt
        prompt = f"""
        You are an expert resume writer. Create a consolidated, improved resume that:
        1. Combines the best elements from multiple resume versions
        2. Is optimized for the specific job description
        3. Highlights the most relevant experience and skills
        4. Uses industry-standard formatting
        5. Includes keywords from the job description
        6. Is ATS-friendly (Applicant Tracking System)
        
        CONSOLIDATED RESUME DATA:
        Name: {personal_info.get('name', 'Candidate')}
        Email: {personal_info.get('email', 'email@example.com')}
        Phone: {personal_info.get('phone', 'N/A')}
        
        Skills: {', '.join(list(all_skills)[:30])}
        
        Experience ({len(all_experience)} positions):
        {json.dumps(all_experience, indent=2)}
        
        Education ({len(all_education)} entries):
        {json.dumps(all_education, indent=2)}
        
        Certifications: {', '.join(list(all_certifications))}
        Achievements: {', '.join(list(all_achievements))}
        
        TARGET JOB DESCRIPTION:
        {job_description}
        
        {"CUSTOM INSTRUCTIONS: " + custom_prompt if custom_prompt else ""}
        
        Create a professional, well-formatted resume in the following structure:
        
        [Full Name]
        [Email] | [Phone] | [LinkedIn URL if available]
        
        PROFESSIONAL SUMMARY
        [Write a compelling 3-4 sentence summary that highlights the most relevant experience and skills for this specific job]
        
        SKILLS
        [List the most relevant skills for this job, organized by category if helpful]
        
        PROFESSIONAL EXPERIENCE
        [List the most relevant positions in reverse chronological order. For each position:
        - Job Title | Company Name | Duration
        - 3-5 bullet points highlighting achievements, responsibilities, and impact
        - Use metrics and quantifiable results where possible
        - Focus on accomplishments that align with the job requirements]
        
        EDUCATION
        [List education in reverse chronological order]
        
        CERTIFICATIONS
        [List relevant certifications]
        
        ACHIEVEMENTS / AWARDS (if applicable)
        [List notable achievements]
        
        Make sure to:
        - Use action verbs
        - Include quantifiable metrics
        - Match keywords from the job description
        - Keep it concise (1-2 pages)
        - Use professional formatting
        - Highlight the most relevant experience first
        """
        
        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        st.error(f"Error generating improved resume: {e}")
        return None

def main():
    st.title("🎯 Interview Preparation & Resume Optimizer")
    st.markdown("**Upload multiple resumes, compare against job descriptions, and generate an improved resume**")
    
    # Get or create user ID
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid4())
    
    # Initialize session state
    if 'resumes' not in st.session_state:
        st.session_state.resumes = []
    if 'resumes_data' not in st.session_state:
        st.session_state.resumes_data = []
    
    # Step 1: Upload Multiple Resumes
    st.header("📄 Step 1: Upload Your Resumes")
    st.info("💡 Upload multiple resume versions to compare and consolidate them")
    
    uploaded_files = st.file_uploader(
        "Upload your resumes (PDF format)",
        type="pdf",
        accept_multiple_files=True,
        help="You can upload multiple resume versions to compare them"
    )
    
    if uploaded_files:
        # Process uploaded files
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in [r['filename'] for r in st.session_state.resumes]:
                resume_text = extract_text_from_pdf(uploaded_file)
                if resume_text and resume_text.strip():
                    with st.spinner(f"Analyzing {uploaded_file.name}..."):
                        resume_data = analyze_resume(resume_text, uploaded_file.name)
                        if resume_data:
                            st.session_state.resumes.append({
                                'filename': uploaded_file.name,
                                'text': resume_text,
                                'data': resume_data
                            })
                            st.session_state.resumes_data.append(resume_data)
                            st.success(f"✅ {uploaded_file.name} analyzed successfully!")
    
    # Display uploaded resumes
    if st.session_state.resumes:
        st.subheader("📋 Uploaded Resumes")
        for i, resume in enumerate(st.session_state.resumes, 1):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{i}. {resume['filename']}**")
                if resume['data'].get('name'):
                    st.caption(f"Name: {resume['data'].get('name')}")
            with col2:
                st.metric("Skills", len(resume['data'].get('skills', [])))
            with col3:
                st.metric("Experience", len(resume['data'].get('experience', [])))
        
        # Remove resume button
        if st.button("🗑️ Clear All Resumes"):
            st.session_state.resumes = []
            st.session_state.resumes_data = []
            st.rerun()
    
    # Step 2: Job Description
    st.header("💼 Step 2: Enter Job Description")
    st.info("💡 Paste the job description to compare your resumes against it")
    
    job_description = st.text_area(
        "Job Description",
        height=300,
        placeholder="Paste the complete job description here, including:\n- Job title and company\n- Responsibilities\n- Requirements\n- Qualifications\n- Preferred skills\n- Any other relevant details...",
        key="job_description"
    )
    
    # Step 3: Analysis
    if st.session_state.resumes_data and job_description:
        st.header("📊 Step 3: Resume Analysis")
        
        if st.button("🔍 Analyze Resumes Against Job Description", type="primary"):
            with st.spinner("Analyzing resumes and comparing against job description..."):
                analysis = compare_resumes_against_job(st.session_state.resumes_data, job_description)
                if analysis:
                    st.session_state.analysis = analysis
                    st.markdown(analysis)
        
        # Display analysis if available
        if 'analysis' in st.session_state:
            st.markdown("---")
            st.markdown("### 📊 Analysis Results")
            st.markdown(st.session_state.analysis)
    
    # Step 4: Generate Improved Resume
    if st.session_state.resumes_data and job_description:
        st.header("✨ Step 4: Generate Improved Resume")
        
        # Custom prompt option
        with st.expander("🎨 Custom Instructions (Optional)", expanded=False):
            custom_prompt = st.text_area(
                "Add custom instructions for resume generation",
                height=150,
                placeholder="Example: 'Emphasize leadership experience', 'Focus on technical skills', 'Make it more concise', 'Highlight remote work experience', etc.",
                key="custom_prompt"
            )
        
        if st.button("🚀 Generate Consolidated Improved Resume", type="primary"):
            custom_instructions = st.session_state.get('custom_prompt', '')
            with st.spinner("Generating your optimized resume..."):
                improved_resume = generate_improved_resume(
                    st.session_state.resumes_data,
                    job_description,
                    custom_instructions
                )
                if improved_resume:
                    st.session_state.improved_resume = improved_resume
                    st.session_state.improved_resume_version = 1
                    st.success("✅ Improved resume generated!")
        
        # Display improved resume
        if 'improved_resume' in st.session_state:
            st.markdown("---")
            st.markdown("### 📄 Your Improved Resume")
            
            # Download button
            st.download_button(
                label="📥 Download Resume",
                data=st.session_state.improved_resume,
                file_name="improved_resume.txt",
                mime="text/plain"
            )
            
            # Display resume
            st.text_area(
                "Resume Content",
                value=st.session_state.improved_resume,
                height=600,
                key="resume_display"
            )
            
            # Generate new version
            st.markdown("---")
            st.subheader("🔄 Generate Different Version")
            
            new_version_prompt = st.text_area(
                "Customize this version",
                height=100,
                placeholder="Example: 'Make it more technical', 'Focus on management experience', 'Emphasize achievements', 'Make it shorter', etc.",
                key="new_version_prompt"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✨ Generate New Version", type="primary"):
                    with st.spinner("Generating new version..."):
                        new_version = generate_improved_resume(
                            st.session_state.resumes_data,
                            job_description,
                            new_version_prompt
                        )
                        if new_version:
                            st.session_state.improved_resume = new_version
                            st.session_state.improved_resume_version += 1
                            st.success(f"✅ Version {st.session_state.improved_resume_version} generated!")
                            st.rerun()
            
            with col2:
                if st.button("🗑️ Clear Generated Resume"):
                    if 'improved_resume' in st.session_state:
                        del st.session_state.improved_resume
                    if 'improved_resume_version' in st.session_state:
                        del st.session_state.improved_resume_version
                    st.rerun()
    
    # Instructions
    if not st.session_state.resumes_data:
        st.markdown("---")
        st.info("""
        ### 📝 How to Use:
        
        1. **Upload Resumes**: Upload one or more resume versions (PDF format)
        2. **Enter Job Description**: Paste the complete job description you're applying for
        3. **Analyze**: Click "Analyze Resumes" to see strengths, weaknesses, and improvement recommendations
        4. **Generate**: Click "Generate Improved Resume" to create a consolidated, optimized resume
        5. **Customize**: Use custom prompts to generate different versions tailored to your needs
        """)

if __name__ == "__main__":
    main()

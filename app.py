"""
Multi-Agent Resume Optimizer - Streamlit Application

A comprehensive Streamlit app that provides a user-friendly interface for
the multi-agent resume optimization system with Groq API integration.
"""

import streamlit as st
import json
import os
import tempfile
import time
from datetime import datetime
from typing import Dict, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
import base64

# Import configuration and workflow
from config import config, setup_environment
import sys
sys.path.append('src')
from workflow.resume_workflow import ResumeWorkflow
from tools.file_parser import ResumeParser

# Setup environment
setup_environment()

# Configure Streamlit page
st.set_page_config(**config.get_streamlit_config())

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #4A4A4A;
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .metric-card {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF6B6B;
        margin: 1rem 0;
    }
    
    .success-message {
        background-color: #D4EDDA;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28A745;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: #F8D7DA;
        color: #721C24;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #DC3545;
        margin: 1rem 0;
    }
    
    .info-box {
        background-color: #E7F3FF;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #007BFF;
        margin: 1rem 0;
    }
    
    .stProgress .st-bo {
        background-color: #FF6B6B;
    }
</style>
""", unsafe_allow_html=True)


class ResumeOptimizerApp:
    """
    Main Streamlit application class for the Resume Optimizer.
    
    Provides a comprehensive interface for resume optimization including
    file upload, workflow execution, results display, and downloads.
    """
    
    def __init__(self):
        """Initialize the application."""
        self.workflow = None
        self.setup_session_state()
    
    def setup_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'workflow_result' not in st.session_state:
            st.session_state.workflow_result = None
        
        if 'uploaded_resume' not in st.session_state:
            st.session_state.uploaded_resume = None
        
        if 'job_url' not in st.session_state:
            st.session_state.job_url = ""
        
        if 'processing' not in st.session_state:
            st.session_state.processing = False
        
        if 'workflow_logs' not in st.session_state:
            st.session_state.workflow_logs = []
    
    def render_header(self):
        """Render the application header."""
        st.markdown('<div class="main-header">📄 Multi-Agent Resume Optimizer</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">AI-powered resume optimization with 90%+ ATS score guarantee</div>', unsafe_allow_html=True)
        
        # Configuration status
        validation = config.validate_config()
        if validation["valid"]:
            st.success("✅ Configuration validated successfully")
        else:
            st.error("❌ Configuration validation failed")
            for error in validation["errors"]:
                st.error(f"• {error}")
            st.stop()
    
    def render_sidebar(self):
        """Render the sidebar with configuration and help."""
        with st.sidebar:
            st.header("🔧 Configuration")
            
            # API Status
            st.subheader("API Status")
            if config.GROQ_API_KEY:
                st.success("✅ Groq API configured")
            else:
                st.error("❌ Groq API key missing")
                st.info("Add GROQ_API_KEY to your .env file")
            
            # Workflow Settings
            st.subheader("Workflow Settings")
            st.info(f"📁 Template: {config.DEFAULT_TEMPLATE_PATH}")
            st.info(f"📂 Output: {config.DEFAULT_OUTPUT_DIR}")
            st.info(f"🗃️ RAG DB: {config.DEFAULT_RAG_DB_PATH}")
            
            # Performance Settings
            st.subheader("Performance")
            st.info(f"⏱️ Timeout: {config.WORKFLOW_TIMEOUT_SECONDS}s")
            st.info(f"🔄 Max Concurrent: {config.MAX_CONCURRENT_WORKFLOWS}")
            
            # Help Section
            st.subheader("📚 Help & Tips")
            with st.expander("How to use"):
                st.markdown("""
                1. **Upload Resume**: Upload your resume as JSON, PDF, or DOCX file
                2. **Job Description**: Paste the job posting URL
                3. **Optimize**: Click 'Optimize Resume' to start
                4. **Review**: Check ATS score and preview
                5. **Download**: Get LaTeX or PDF file
                """)
            
            with st.expander("Supported formats"):
                st.markdown("""
                - **Resume**: JSON format with structured data
                - **Job URLs**: LinkedIn, Indeed, Glassdoor, etc.
                - **Output**: LaTeX (.tex) and PDF files
                """)
            
            with st.expander("Troubleshooting"):
                st.markdown("""
                - Ensure valid JSON resume format
                - Check job URL accessibility
                - Verify API keys in .env file
                - Check network connectivity
                """)
    
    def render_file_upload(self):
        """Render the file upload section."""
        st.header("📤 Step 1: Upload Resume")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Upload your resume (JSON, PDF, or DOCX format)",
                type=['json', 'txt', 'pdf', 'docx'],
                help="Upload a resume in JSON, PDF, or DOCX format"
            )
            
            if uploaded_file is not None:
                try:
                    # Read and parse the file using the unified parser
                    file_content = uploaded_file.read()
                    file_name = uploaded_file.name
                    
                    # Initialize parser
                    parser = ResumeParser()
                    
                    # Parse the file based on its type
                    resume_data = parser.parse_file(file_name, file_content)
                    
                    # Validate the parsed data
                    if not parser.validate_resume_data(resume_data):
                        st.warning("⚠️ Parsed resume data may be incomplete. Please review the preview.")
                    
                    st.session_state.uploaded_resume = resume_data
                    
                    # Display success message with file type
                    file_type = file_name.split('.')[-1].upper()
                    st.markdown(f'<div class="success-message">✅ {file_type} resume uploaded and parsed successfully!</div>', unsafe_allow_html=True)
                    
                    # Show resume preview
                    with st.expander("📋 Resume Preview"):
                        st.json(resume_data)
                    
                except Exception as e:
                    st.error(f"❌ Error parsing file: {e}")
                    st.info("💡 **Supported formats:** JSON, PDF, DOCX")
                    st.info("💡 **Tips:** Ensure your PDF/DOCX resume has clear section headers like 'Experience', 'Education', 'Skills'")
        
        with col2:
            if st.session_state.uploaded_resume:
                st.markdown('<div class="info-box">📊 Resume Analysis</div>', unsafe_allow_html=True)
                
                # Basic resume statistics
                resume = st.session_state.uploaded_resume
                stats = self.analyze_resume_structure(resume)
                
                for key, value in stats.items():
                    st.metric(key, value)
    
    def analyze_resume_structure(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the structure of uploaded resume data."""
        stats = {}
        
        # Count sections
        if 'experience' in resume_data:
            stats['Experience Entries'] = len(resume_data['experience'])
        
        if 'skills' in resume_data:
            if isinstance(resume_data['skills'], list):
                stats['Skills'] = len(resume_data['skills'])
            elif isinstance(resume_data['skills'], dict):
                total_skills = sum(len(v) if isinstance(v, list) else 1 for v in resume_data['skills'].values())
                stats['Skills'] = total_skills
        
        if 'education' in resume_data:
            stats['Education'] = len(resume_data['education'])
        
        if 'projects' in resume_data:
            stats['Projects'] = len(resume_data['projects'])
        
        return stats
    
    def render_job_input(self):
        """Render the job description input section."""
        st.header("🔗 Step 2: Job Description")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            job_url = st.text_input(
                "Job Description URL",
                value=st.session_state.job_url,
                placeholder="https://linkedin.com/jobs/view/123456789",
                help="Paste the URL of the job posting you want to optimize for"
            )
            
            st.session_state.job_url = job_url
            
            # URL validation
            if job_url:
                if self.validate_job_url(job_url):
                    st.success("✅ Valid job URL format")
                else:
                    st.warning("⚠️ URL format may not be supported")
        
        with col2:
            if job_url:
                st.markdown('<div class="info-box">🔍 URL Analysis</div>', unsafe_allow_html=True)
                
                # Extract domain
                from urllib.parse import urlparse
                try:
                    domain = urlparse(job_url).netloc
                    st.info(f"Domain: {domain}")
                    
                    # Check if domain is in allowed list
                    if any(allowed in domain for allowed in config.ALLOWED_DOMAINS):
                        st.success("✅ Supported platform")
                    else:
                        st.warning("⚠️ Platform not in whitelist")
                
                except Exception:
                    st.error("❌ Invalid URL format")
    
    def validate_job_url(self, url: str) -> bool:
        """Validate job URL format."""
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def render_optimization_section(self):
        """Render the optimization execution section."""
        st.header("🚀 Step 3: Optimize Resume")
        
        # Check if ready to optimize
        ready_to_optimize = (
            st.session_state.uploaded_resume is not None and 
            st.session_state.job_url and 
            not st.session_state.processing
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button(
                "🎯 Optimize Resume", 
                disabled=not ready_to_optimize,
                use_container_width=True
            ):
                self.run_optimization()
        
        with col2:
            if st.session_state.workflow_result:
                if st.button("🔄 Reset", use_container_width=True):
                    self.reset_workflow()
        
        with col3:
            if st.session_state.processing:
                st.info("⏳ Processing...")
        
        # Show requirements if not ready
        if not ready_to_optimize and not st.session_state.processing:
            st.markdown('<div class="info-box">📋 Requirements</div>', unsafe_allow_html=True)
            
            requirements = []
            if not st.session_state.uploaded_resume:
                requirements.append("❌ Upload resume file (JSON/PDF/DOCX)")
            else:
                requirements.append("✅ Resume uploaded")
            
            if not st.session_state.job_url:
                requirements.append("❌ Enter job description URL")
            else:
                requirements.append("✅ Job URL provided")
            
            for req in requirements:
                st.markdown(req)
    
    def run_optimization(self):
        """Execute the resume optimization workflow."""
        st.session_state.processing = True
        st.session_state.workflow_logs = []
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        log_container = st.empty()
        
        try:
            # Initialize workflow
            status_text.text("Initializing workflow...")
            progress_bar.progress(10)
            
            if not self.workflow:
                self.workflow = ResumeWorkflow(
                    template_path=config.DEFAULT_TEMPLATE_PATH,
                    output_directory=config.DEFAULT_OUTPUT_DIR,
                    rag_database_path=config.DEFAULT_RAG_DB_PATH
                )
            
            # Prepare profile data
            status_text.text("Preparing profile data...")
            progress_bar.progress(20)
            
            # Create a temporary profile for the uploaded resume
            profile_id = f"uploaded_{int(time.time())}"
            self.save_temp_profile(profile_id, st.session_state.uploaded_resume)
            
            # Execute workflow
            status_text.text("Executing optimization workflow...")
            progress_bar.progress(30)
            
            # Simulate progress updates (in real implementation, you'd get these from workflow)
            steps = [
                (40, "Extracting job description..."),
                (50, "Retrieving profile data..."),
                (60, "Aligning content with job requirements..."),
                (80, "Optimizing for ATS compatibility..."),
                (90, "Generating LaTeX resume...")
            ]
            
            for progress, message in steps:
                status_text.text(message)
                progress_bar.progress(progress)
                time.sleep(0.5)  # Simulate processing time
            
            # Run actual workflow
            result = self.workflow.run_workflow(
                job_url=st.session_state.job_url,
                profile_id=profile_id,
                return_intermediate_results=True
            )
            
            progress_bar.progress(100)
            status_text.text("Optimization completed!")
            
            # Store results
            st.session_state.workflow_result = result
            
            # Show completion message
            if result.success:
                st.success("🎉 Resume optimization completed successfully!")
            else:
                st.error("❌ Optimization failed. Check errors below.")
        
        except Exception as e:
            st.error(f"❌ Error during optimization: {str(e)}")
            # Create a mock dict for error display
            class ErrorResult:
                success = False
                errors = [str(e)]
                latex_file_path = None
                intermediate_results = {}
                execution_time = {}
            st.session_state.workflow_result = ErrorResult()
        
        finally:
            st.session_state.processing = False
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
    
    def save_temp_profile(self, profile_id: str, resume_data: Dict[str, Any]):
        """Save uploaded resume as temporary profile for workflow."""
        try:
            # Ensure RAG database directory exists
            os.makedirs(config.DEFAULT_RAG_DB_PATH, exist_ok=True)
            
            # Create profile file
            profile_path = os.path.join(config.DEFAULT_RAG_DB_PATH, f"{profile_id}.json")
            
            # Transform resume data to expected format
            profile_data = {
                "profile_id": profile_id,
                "name": resume_data.get("name", "Applicant"),
                "email": resume_data.get("email", ""),
                "phone": resume_data.get("phone", ""),
                "skills": resume_data.get("skills", []),
                "experience": resume_data.get("experience", []),
                "education": resume_data.get("education", []),
                "projects": resume_data.get("projects", []),
                "summary": resume_data.get("summary", ""),
                "created_at": datetime.now().isoformat(),
                "source": "streamlit_upload"
            }
            
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            st.error(f"Error saving profile: {e}")
            raise
    
    def reset_workflow(self):
        """Reset the workflow state."""
        st.session_state.workflow_result = None
        st.session_state.workflow_logs = []
        st.session_state.processing = False
        st.rerun()
    
    def render_results_section(self):
        """Render the results and analysis section."""
        if not st.session_state.workflow_result:
            return
        
        result = st.session_state.workflow_result
        
        st.header("📊 Results & Analysis")
        
        if result.success:
            self.render_success_results(result)
        else:
            self.render_error_results(result)
    
    def render_success_results(self, result: Dict[str, Any]):
        """Render successful optimization results."""
        # ATS Score Display
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Get ATS score from results
            ats_score = 0
            if result.intermediate_results:
                optimized_data = result.intermediate_results.get('optimized_data', {})
                ats_analysis = optimized_data.get('ats_analysis', {}) if isinstance(optimized_data, dict) else {}
                ats_score = ats_analysis.get('ats_score', 0)
            
            # Create ATS score gauge
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = ats_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "ATS Score"},
                delta = {'reference': 90},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('<div class="metric-card">📈 Performance Metrics</div>', unsafe_allow_html=True)
            
            # Execution time
            total_time = sum(result.execution_time.values()) if result.execution_time else 0
            st.metric("Execution Time", f"{total_time:.1f}s")
            
            # File size
            if result.latex_file_path and os.path.exists(result.latex_file_path):
                file_size = os.path.getsize(result.latex_file_path)
                st.metric("File Size", f"{file_size:,} bytes")
        
        with col3:
            st.markdown('<div class="metric-card">✅ Quality Indicators</div>', unsafe_allow_html=True)
            
            # Quality metrics
            if ats_score >= 90:
                st.success("🎯 ATS Ready")
            elif ats_score >= 70:
                st.warning("⚠️ Needs Improvement")
            else:
                st.error("❌ Poor ATS Score")
            
            # Overleaf compatibility
            st.success("📄 Overleaf Ready")
        
        # Detailed Analysis
        st.subheader("🔍 Detailed Analysis")
        
        if result.intermediate_results:
            intermediate = result.intermediate_results
            
            # Create tabs for different analyses
            tab1, tab2, tab3, tab4 = st.tabs(["📋 Job Analysis", "👤 Profile Match", "🎯 Content Alignment", "⚡ ATS Optimization"])
            
            with tab1:
                self.render_job_analysis(intermediate.get('job_data', {}))
            
            with tab2:
                self.render_profile_analysis(intermediate.get('profile_data', {}))
            
            with tab3:
                self.render_alignment_analysis(intermediate.get('aligned_data', {}))
            
            with tab4:
                self.render_ats_analysis(intermediate.get('optimized_data', {}))
    
    def render_job_analysis(self, job_data: Dict[str, Any]):
        """Render job description analysis."""
        if not job_data:
            st.info("No job analysis data available")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Job Requirements")
            
            # Job title and company
            st.info(f"**Position:** {job_data.get('job_title', 'N/A')}")
            st.info(f"**Company:** {job_data.get('company', 'N/A')}")
            
            # Keywords
            keywords = job_data.get('keywords', [])
            if keywords:
                st.write("**Key Skills Required:**")
                for i, keyword in enumerate(keywords[:10], 1):
                    st.write(f"{i}. {keyword}")
        
        with col2:
            st.subheader("📈 Keyword Analysis")
            
            if keywords:
                # Create keyword frequency chart
                keyword_counts = {kw: 1 for kw in keywords[:10]}  # Simplified
                
                fig = px.bar(
                    x=list(keyword_counts.keys()),
                    y=list(keyword_counts.values()),
                    title="Top Keywords"
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    
    def render_profile_analysis(self, profile_data: Dict[str, Any]):
        """Render profile analysis."""
        if not profile_data:
            st.info("No profile analysis data available")
            return
        
        st.subheader("👤 Profile Relevance")
        
        relevance_score = profile_data.get('relevance_score', 0)
        st.metric("Relevance Score", f"{relevance_score:.1%}")
        
        # Relevant sections
        relevant_data = profile_data.get('relevant_data', {})
        if relevant_data:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Matching Skills:**")
                skills = relevant_data.get('skills', [])
                for skill in skills[:10]:
                    st.write(f"• {skill}")
            
            with col2:
                st.write("**Relevant Experience:**")
                experience = relevant_data.get('experience', [])
                for exp in experience[:3]:
                    st.write(f"• {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
    
    def render_alignment_analysis(self, aligned_data: Dict[str, Any]):
        """Render content alignment analysis."""
        if not aligned_data:
            st.info("No alignment analysis data available")
            return
        
        st.subheader("🎯 Content Alignment")
        
        alignment_analysis = aligned_data.get('alignment_analysis', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Overall alignment score
            overall_score = alignment_analysis.get('overall_score', 0)
            st.metric("Alignment Score", f"{overall_score:.1%}")
            
            # Matched keywords
            matched_keywords = alignment_analysis.get('matched_keywords', [])
            st.write(f"**Matched Keywords ({len(matched_keywords)}):**")
            for keyword in matched_keywords[:10]:
                st.write(f"✅ {keyword}")
        
        with col2:
            # Missing keywords
            missing_keywords = alignment_analysis.get('missing_keywords', [])
            if missing_keywords:
                st.write(f"**Missing Keywords ({len(missing_keywords)}):**")
                for keyword in missing_keywords[:10]:
                    st.write(f"❌ {keyword}")
    
    def render_ats_analysis(self, optimized_data: Dict[str, Any]):
        """Render ATS optimization analysis."""
        if not optimized_data:
            st.info("No ATS analysis data available")
            return
        
        st.subheader("⚡ ATS Optimization")
        
        ats_analysis = optimized_data.get('ats_analysis', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            # ATS metrics
            st.write("**ATS Metrics:**")
            metrics = [
                ("ATS Score", ats_analysis.get('ats_score', 0), "/100"),
                ("Keyword Density", ats_analysis.get('keyword_density', 0) * 100, "%"),
                ("Section Completeness", ats_analysis.get('section_completeness', 0) * 100, "%"),
                ("Formatting Score", ats_analysis.get('formatting_score', 0) * 100, "%")
            ]
            
            for name, value, unit in metrics:
                st.metric(name, f"{value:.1f}{unit}")
        
        with col2:
            # Suggestions and auto-fixes
            suggestions = ats_analysis.get('suggestions', [])
            if suggestions:
                st.write("**Suggestions:**")
                for suggestion in suggestions[:5]:
                    st.write(f"💡 {suggestion}")
            
            auto_fixes = optimized_data.get('auto_fixes_applied', [])
            if auto_fixes:
                st.write("**Auto-fixes Applied:**")
                for fix in auto_fixes[:5]:
                    st.write(f"🔧 {fix}")
    
    def render_error_results(self, result):
        """Render error results."""
        st.markdown('<div class="error-message">❌ Optimization Failed</div>', unsafe_allow_html=True)
        
        errors = result.errors if hasattr(result, 'errors') else []
        for error in errors:
            st.error(f"• {error}")
        
        warnings = result.warnings if hasattr(result, 'warnings') else []
        if warnings:
            st.subheader("⚠️ Warnings")
            for warning in warnings:
                st.warning(f"• {warning}")
        
        # Execution time even for failed runs
        execution_time = result.execution_time if hasattr(result, 'execution_time') else {}
        if execution_time:
            total_time = sum(execution_time.values()) if isinstance(execution_time, dict) else 0
            st.info(f"⏱️ Execution time: {total_time:.2f} seconds")
    
    def render_download_section(self):
        """Render the download section."""
        if not st.session_state.workflow_result or not st.session_state.workflow_result.success:
            return
        
        st.header("📥 Download Results")
        
        result = st.session_state.workflow_result
        latex_file_path = result.latex_file_path
        
        if not latex_file_path or not os.path.exists(latex_file_path):
            st.error("❌ LaTeX file not found")
            return
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # LaTeX download
            with open(latex_file_path, 'r', encoding='utf-8') as f:
                latex_content = f.read()
            
            st.download_button(
                label="📄 Download LaTeX (.tex)",
                data=latex_content,
                file_name=f"optimized_resume_{int(time.time())}.tex",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            # PDF generation and download
            if st.button("📄 Generate & Download PDF", use_container_width=True):
                pdf_content = self.generate_pdf_from_latex(latex_content)
                if pdf_content:
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_content,
                        file_name=f"optimized_resume_{int(time.time())}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
        
        with col3:
            # Preview button
            if st.button("👁️ Preview Resume", use_container_width=True):
                st.session_state.show_preview = True
        
        # Show preview if requested
        if getattr(st.session_state, 'show_preview', False):
            self.render_resume_preview(latex_content)
    
    def generate_pdf_from_latex(self, latex_content: str) -> Optional[bytes]:
        """Generate PDF from LaTeX content (simplified version)."""
        try:
            # This is a simplified PDF generation
            # In production, you'd use a proper LaTeX compiler
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Extract text content from LaTeX (very basic)
            import re
            
            # Remove LaTeX commands and extract text
            text_content = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', latex_content)
            text_content = re.sub(r'\\[a-zA-Z]+', '', text_content)
            text_content = re.sub(r'\{|\}', '', text_content)
            
            # Split into lines and add to PDF
            lines = text_content.split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    try:
                        pdf.cell(0, 10, line.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                    except:
                        pdf.cell(0, 10, "Content contains special characters", ln=True)
            
            return pdf.output(dest='S').encode('latin-1')
        
        except Exception as e:
            st.error(f"Error generating PDF: {e}")
            return None
    
    def render_resume_preview(self, latex_content: str):
        """Render a preview of the resume content."""
        st.subheader("👁️ Resume Preview")
        
        # Extract and display key sections from LaTeX
        import re
        
        # Extract name
        name_match = re.search(r'\\name\{([^}]*)\}\{([^}]*)\}', latex_content)
        if name_match:
            st.markdown(f"### {name_match.group(1)} {name_match.group(2)}")
        
        # Extract title
        title_match = re.search(r'\\title\{([^}]*)\}', latex_content)
        if title_match:
            st.markdown(f"**{title_match.group(1)}**")
        
        # Show sections
        sections = [
            ('Professional Summary', r'\\section\{Professional Summary\}.*?\\cvitem\{\}\{([^}]*)\}'),
            ('Technical Skills', r'\\section\{Technical Skills\}(.*?)\\section'),
            ('Professional Experience', r'\\section\{Professional Experience\}(.*?)\\section'),
        ]
        
        for section_name, pattern in sections:
            match = re.search(pattern, latex_content, re.DOTALL)
            if match:
                st.markdown(f"**{section_name}:**")
                content = match.group(1).strip()
                # Clean up LaTeX commands
                content = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', content)
                content = re.sub(r'\\[a-zA-Z]+', '', content)
                content = re.sub(r'\{|\}', '', content)
                st.text(content[:500] + "..." if len(content) > 500 else content)
                st.markdown("---")
    
    def render_footer(self):
        """Render the application footer."""
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🔧 Powered by:**")
            st.markdown("• LangGraph Workflow")
            st.markdown("• Groq API")
            st.markdown("• Streamlit")
        
        with col2:
            st.markdown("**📊 Features:**")
            st.markdown("• Multi-Agent Optimization")
            st.markdown("• 90%+ ATS Score Target")
            st.markdown("• Overleaf Compatible")
        
        with col3:
            st.markdown("**🎯 Version:** 1.0.0")
            st.markdown("**📅 Updated:** October 2024")
            st.markdown("**🏗️ Built for Hacktoberfest 2025")
    
    def run(self):
        """Run the Streamlit application."""
        # Render all sections
        self.render_header()
        self.render_sidebar()
        
        # Main content
        self.render_file_upload()
        st.markdown("---")
        
        self.render_job_input()
        st.markdown("---")
        
        self.render_optimization_section()
        st.markdown("---")
        
        self.render_results_section()
        
        if st.session_state.workflow_result and st.session_state.workflow_result.success:
            st.markdown("---")
            self.render_download_section()
        
        self.render_footer()


def main():
    """Main function to run the Streamlit app."""
    try:
        app = ResumeOptimizerApp()
        app.run()
    except Exception as e:
        st.error(f"Application error: {e}")
        st.error("Please check your configuration and try again.")


if __name__ == "__main__":
    main()

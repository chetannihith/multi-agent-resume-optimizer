"""
LaTeXFormatterAgent Integration Demo

This script demonstrates the integration of LaTeXFormatterAgent with
simulated outputs from previous agents in the resume optimization pipeline.
"""

import os
import sys
import json
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.latex_formatter_agent import LaTeXFormatterAgent


def simulate_ats_optimizer_output():
    """
    Simulate the output from ATSOptimizerAgent.
    
    Returns:
        Dictionary containing optimized resume data
    """
    return {
        "profile_id": "sarah_johnson_2024",
        "job_title": "Full Stack Developer",
        "name": "Sarah Johnson",
        "ats_analysis": {
            "ats_score": 94,
            "category": "Excellent",
            "keyword_density": 0.85,
            "section_completeness": 1.0,
            "formatting_score": 0.95,
            "suggestions": [
                "Consider adding more cloud computing keywords",
                "Include specific project metrics where possible"
            ]
        },
        "aligned_sections": {
            "summary": "Experienced Full Stack Developer with 4+ years of expertise in React, Node.js, and cloud technologies. Proven track record of building scalable web applications, implementing microservices architecture, and leading cross-functional teams. Strong background in agile development, DevOps practices, and modern JavaScript frameworks.",
            "skills": {
                "aligned_skills": [
                    "JavaScript", "React", "Node.js", "Python", "TypeScript",
                    "MongoDB", "PostgreSQL", "AWS", "Docker", "Kubernetes",
                    "Git", "CI/CD", "REST APIs", "GraphQL", "Microservices"
                ],
                "skill_categories": {
                    "frontend": ["JavaScript", "React", "TypeScript", "HTML5", "CSS3"],
                    "backend": ["Node.js", "Python", "Express.js", "REST APIs", "GraphQL"],
                    "database": ["MongoDB", "PostgreSQL", "Redis"],
                    "devops": ["AWS", "Docker", "Kubernetes", "CI/CD", "Git"],
                    "other": ["Agile", "Scrum", "Team Leadership"]
                }
            },
            "experience": [
                {
                    "title": "Senior Full Stack Developer",
                    "company": "InnovateTech Solutions",
                    "duration": "2022-2024",
                    "location": "Seattle, WA",
                    "description": "Led development of enterprise web applications using React and Node.js. Implemented microservices architecture and deployed on AWS.",
                    "aligned_description": "Led development of scalable enterprise web applications using React, Node.js, and modern JavaScript frameworks. Successfully implemented microservices architecture serving 100,000+ users daily. Deployed and managed applications on AWS cloud infrastructure using Docker containers and Kubernetes orchestration. Collaborated with cross-functional teams in agile development environment to deliver high-quality software solutions."
                },
                {
                    "title": "Full Stack Developer",
                    "company": "WebCraft Studios",
                    "duration": "2020-2022",
                    "location": "Portland, OR",
                    "description": "Built responsive web applications using React and Python. Integrated third-party APIs and optimized database performance.",
                    "aligned_description": "Developed responsive web applications using React frontend and Python backend technologies. Successfully integrated multiple third-party APIs and payment processing systems. Optimized PostgreSQL database queries and implemented caching strategies, resulting in 50% improvement in application performance. Participated in code reviews and mentored junior developers."
                },
                {
                    "title": "Junior Web Developer",
                    "company": "StartupHub Inc.",
                    "duration": "2019-2020",
                    "location": "San Francisco, CA",
                    "description": "Developed web interfaces using HTML, CSS, and JavaScript. Worked on REST API integration and database design.",
                    "aligned_description": "Developed modern web interfaces using HTML5, CSS3, and JavaScript ES6+. Implemented REST API integrations and contributed to database design and optimization. Gained experience with version control systems and agile development methodologies."
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "institution": "University of Washington",
                    "year": "2019",
                    "location": "Seattle, WA",
                    "gpa": "3.6"
                }
            ]
        },
        "relevant_projects": [
            {
                "name": "E-commerce Microservices Platform",
                "description": "Architected and developed a comprehensive microservices-based e-commerce platform handling product catalog, user management, order processing, and payment integration",
                "technologies": "React, Node.js, MongoDB, Docker, Kubernetes, AWS, Redis",
                "impact": "Reduced system response time by 65% and supported 5x user growth with 99.9% uptime",
                "date": "2023"
            },
            {
                "name": "Real-time Collaboration Tool",
                "description": "Built a real-time collaborative workspace application with live document editing, video conferencing, and project management features",
                "technologies": "React, TypeScript, WebSocket, Node.js, PostgreSQL, AWS",
                "impact": "Enabled remote collaboration for 500+ teams, reducing meeting time by 40%",
                "date": "2022"
            },
            {
                "name": "Analytics Dashboard Platform",
                "description": "Created a comprehensive analytics dashboard for business intelligence with real-time data visualization and automated reporting",
                "technologies": "React, D3.js, Python, FastAPI, PostgreSQL, Docker",
                "impact": "Improved decision-making speed by 60% through automated insights and real-time metrics",
                "date": "2021"
            }
        ],
        "auto_fixes_applied": [
            "Added missing 'microservices' keyword to experience descriptions",
            "Enhanced skills section with cloud computing technologies",
            "Improved keyword density for 'React' and 'Node.js'"
        ]
    }


def demonstrate_latex_generation():
    """
    Demonstrate LaTeX resume generation with different scenarios.
    """
    print("LaTeX Formatter Agent Integration Demo")
    print("=" * 50)
    
    # Initialize the LaTeX formatter agent
    agent = LaTeXFormatterAgent(
        template_path="templates/resume_template.tex",
        output_directory="output"
    )
    
    # Get simulated optimized resume data
    optimized_resume = simulate_ats_optimizer_output()
    
    print(f"Processing Resume for: {optimized_resume['name']}")
    print(f"Profile ID: {optimized_resume['profile_id']}")
    print(f"Target Position: {optimized_resume['job_title']}")
    print(f"ATS Score: {optimized_resume['ats_analysis']['ats_score']}/100")
    print()
    
    # Generate LaTeX resume
    print("Generating LaTeX Resume...")
    try:
        output_path = agent.generate_latex_resume(
            optimized_resume, 
            f"{optimized_resume['profile_id']}_resume.tex"
        )
        
        # Get absolute path for display
        absolute_path = os.path.abspath(output_path)
        
        print("SUCCESS: LaTeX Resume Generated!")
        print("-" * 30)
        print(f"File Location: {absolute_path}")
        
        # Show file details
        file_size = os.path.getsize(output_path)
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            line_count = len(content.splitlines())
        
        print(f"File Size: {file_size:,} bytes")
        print(f"Line Count: {line_count}")
        print()
        
        # Validate Overleaf compatibility
        print("Overleaf Compatibility Check:")
        validation = agent.validate_overleaf_compatibility(content)
        print(f"  Compatible: {'YES' if validation['is_compatible'] else 'NO'}")
        
        if validation['warnings']:
            print("  Warnings:")
            for warning in validation['warnings']:
                print(f"    - {warning}")
        
        if validation['errors']:
            print("  Errors:")
            for error in validation['errors']:
                print(f"    - {error}")
        
        if not validation['warnings'] and not validation['errors']:
            print("  No compatibility issues detected!")
        
        print()
        
        # Show content preview
        print("LaTeX Content Preview (first 15 lines):")
        print("-" * 40)
        for i, line in enumerate(content.splitlines()[:15], 1):
            print(f"{i:2d}: {line}")
        print("    ... (content continues)")
        print()
        
        # Show key sections included
        print("Resume Sections Included:")
        sections_found = []
        if "\\section{Professional Summary}" in content:
            sections_found.append("Professional Summary")
        if "\\section{Technical Skills}" in content:
            sections_found.append("Technical Skills")
        if "\\section{Professional Experience}" in content:
            sections_found.append("Professional Experience")
        if "\\section{Key Projects}" in content:
            sections_found.append("Key Projects")
        if "\\section{Education}" in content:
            sections_found.append("Education")
        
        for section in sections_found:
            print(f"  [MATCH] {section}")
        
        print()
        
        # Show Overleaf instructions
        print("NEXT STEPS - Overleaf Upload Instructions:")
        print("=" * 45)
        print("1. Go to https://www.overleaf.com")
        print("2. Sign in or create a free account")
        print("3. Click 'New Project' -> 'Upload Project'")
        print(f"4. Upload the file: {os.path.basename(output_path)}")
        print("5. Click 'Recompile' to generate PDF")
        print("6. Download PDF or continue editing online")
        print()
        print("Template Features:")
        print("  - Modern CV style with professional layout")
        print("  - ATS-friendly formatting (no images/graphics)")
        print("  - Clean section organization")
        print("  - Proper LaTeX escaping for special characters")
        print("  - Overleaf-compatible packages only")
        
        # Show ATS optimization results
        print()
        print("ATS Optimization Summary:")
        print("-" * 25)
        ats_data = optimized_resume['ats_analysis']
        print(f"Overall Score: {ats_data['ats_score']}/100 ({ats_data['category']})")
        print(f"Keyword Density: {ats_data['keyword_density']:.1%}")
        print(f"Section Completeness: {ats_data['section_completeness']:.1%}")
        print(f"Formatting Score: {ats_data['formatting_score']:.1%}")
        
        if optimized_resume.get('auto_fixes_applied'):
            print()
            print("Auto-fixes Applied:")
            for fix in optimized_resume['auto_fixes_applied']:
                print(f"  - {fix}")
        
        return output_path
        
    except Exception as e:
        print(f"ERROR: Failed to generate LaTeX resume")
        print(f"Error details: {e}")
        import traceback
        traceback.print_exc()
        return None


def demonstrate_multiple_formats():
    """
    Demonstrate generating multiple resume formats.
    """
    print("\n" + "=" * 50)
    print("Multiple Format Generation Demo")
    print("=" * 50)
    
    agent = LaTeXFormatterAgent(
        template_path="templates/resume_template.tex",
        output_directory="output"
    )
    
    optimized_resume = simulate_ats_optimizer_output()
    
    # Generate different versions
    formats = [
        ("standard", "Standard format with all sections"),
        ("compact", "Compact format for experienced professionals"),
        ("academic", "Academic format with research focus")
    ]
    
    generated_files = []
    
    for format_name, description in formats:
        print(f"Generating {format_name} format...")
        
        # Modify resume data based on format (simplified for demo)
        modified_resume = optimized_resume.copy()
        
        if format_name == "compact":
            # Limit experience entries for compact format
            modified_resume['aligned_sections']['experience'] = \
                modified_resume['aligned_sections']['experience'][:2]
        
        filename = f"{optimized_resume['profile_id']}_{format_name}.tex"
        
        try:
            output_path = agent.generate_latex_resume(modified_resume, filename)
            generated_files.append((format_name, output_path, description))
            print(f"  [MATCH] Generated: {os.path.basename(output_path)}")
        except Exception as e:
            print(f"  [ERROR] Failed to generate {format_name}: {e}")
    
    print()
    print("Generated Files Summary:")
    print("-" * 25)
    for format_name, file_path, description in generated_files:
        file_size = os.path.getsize(file_path)
        print(f"{format_name.capitalize()}: {os.path.basename(file_path)} ({file_size:,} bytes)")
        print(f"  Description: {description}")
    
    return generated_files


def main():
    """
    Main demonstration function.
    """
    try:
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        
        # Run main demonstration
        latex_file = demonstrate_latex_generation()
        
        if latex_file:
            # Run multiple formats demo
            multiple_files = demonstrate_multiple_formats()
            
            print("\n" + "=" * 50)
            print("Demo Completed Successfully!")
            print("=" * 50)
            print(f"Primary Resume: {os.path.basename(latex_file)}")
            print(f"Additional Formats: {len(multiple_files)} files generated")
            print()
            print("All files are ready for Overleaf upload!")
        else:
            print("Demo failed - check error messages above")
    
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

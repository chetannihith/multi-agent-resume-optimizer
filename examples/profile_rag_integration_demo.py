"""
Profile RAG Agent Integration Demo

This script demonstrates how to use the ProfileRAGAgent with JDExtractorAgent
to create a complete workflow for retrieving relevant applicant information
based on job descriptions.
"""

import sys
import os
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.profile_rag_agent import ProfileRAGAgent
from agents.jd_extractor_agent import JDExtractorAgent


def create_sample_profiles():
    """
    Create sample applicant profiles for demonstration.
    
    Returns:
        List of sample profile dictionaries
    """
    return [
        {
            "profile_id": "alice_ml_engineer",
            "name": "Alice Johnson",
            "email": "alice.johnson@email.com",
            "skills": [
                "Python", "Machine Learning", "TensorFlow", "PyTorch", 
                "Scikit-learn", "Pandas", "NumPy", "AWS", "Docker", 
                "Kubernetes", "SQL", "Git", "REST APIs"
            ],
            "experience": [
                {
                    "title": "Senior ML Engineer",
                    "company": "AI Innovations Inc.",
                    "duration": "2021-2024",
                    "description": "Led development of recommendation systems using TensorFlow and PyTorch. Deployed ML models on AWS using Docker and Kubernetes. Improved model accuracy by 25% through feature engineering and hyperparameter tuning."
                },
                {
                    "title": "Data Scientist",
                    "company": "DataCorp Solutions",
                    "duration": "2019-2021",
                    "description": "Built predictive models for customer churn analysis. Developed ETL pipelines using Python and SQL. Created data visualizations and reports for stakeholders."
                }
            ],
            "projects": [
                {
                    "name": "Real-time Fraud Detection System",
                    "description": "Developed ML-powered fraud detection system processing 1M+ transactions daily",
                    "technologies": "Python, TensorFlow, Apache Kafka, Redis, PostgreSQL",
                    "impact": "Reduced fraud losses by 40%"
                },
                {
                    "name": "Customer Segmentation Platform",
                    "description": "Built unsupervised learning system for customer segmentation and targeting",
                    "technologies": "Python, Scikit-learn, AWS SageMaker, S3",
                    "impact": "Increased marketing ROI by 30%"
                }
            ],
            "education": [
                {
                    "degree": "Master of Science",
                    "field": "Machine Learning",
                    "institution": "Stanford University",
                    "year": "2019",
                    "gpa": "3.8/4.0"
                },
                {
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "institution": "UC Berkeley",
                    "year": "2017",
                    "gpa": "3.7/4.0"
                }
            ],
            "certifications": [
                "AWS Certified Machine Learning - Specialty",
                "TensorFlow Developer Certificate",
                "Google Cloud Professional ML Engineer"
            ]
        },
        {
            "profile_id": "bob_fullstack_dev",
            "name": "Bob Smith",
            "email": "bob.smith@email.com",
            "skills": [
                "JavaScript", "TypeScript", "React", "Node.js", "Express.js",
                "MongoDB", "PostgreSQL", "HTML5", "CSS3", "SASS", "Webpack",
                "Jest", "Cypress", "Docker", "AWS", "Git", "Agile"
            ],
            "experience": [
                {
                    "title": "Senior Full Stack Developer",
                    "company": "WebTech Solutions",
                    "duration": "2020-2024",
                    "description": "Led development of scalable web applications using React and Node.js. Implemented microservices architecture with Docker containers. Mentored junior developers and conducted code reviews."
                },
                {
                    "title": "Frontend Developer",
                    "company": "StartupXYZ",
                    "duration": "2018-2020",
                    "description": "Built responsive web interfaces using React and modern CSS. Optimized application performance and implemented automated testing with Jest and Cypress."
                }
            ],
            "projects": [
                {
                    "name": "E-commerce Platform",
                    "description": "Full-stack e-commerce solution with payment integration and inventory management",
                    "technologies": "React, Node.js, Express, MongoDB, Stripe API",
                    "impact": "Processed $2M+ in transactions"
                },
                {
                    "name": "Real-time Collaboration Tool",
                    "description": "Web-based collaboration platform with real-time messaging and file sharing",
                    "technologies": "React, Socket.io, Node.js, PostgreSQL, AWS S3",
                    "impact": "Used by 10,000+ active users"
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "field": "Software Engineering",
                    "institution": "MIT",
                    "year": "2018",
                    "gpa": "3.6/4.0"
                }
            ],
            "certifications": [
                "AWS Certified Developer - Associate",
                "React Developer Certification",
                "Node.js Certified Developer"
            ]
        },
        {
            "profile_id": "carol_devops_engineer",
            "name": "Carol Davis",
            "email": "carol.davis@email.com",
            "skills": [
                "AWS", "Azure", "Docker", "Kubernetes", "Terraform", "Ansible",
                "Jenkins", "GitLab CI", "Prometheus", "Grafana", "ELK Stack",
                "Python", "Bash", "Linux", "Networking", "Security"
            ],
            "experience": [
                {
                    "title": "Senior DevOps Engineer",
                    "company": "CloudFirst Technologies",
                    "duration": "2019-2024",
                    "description": "Designed and implemented CI/CD pipelines using Jenkins and GitLab CI. Managed Kubernetes clusters on AWS and Azure. Implemented infrastructure as code using Terraform and Ansible."
                },
                {
                    "title": "Systems Administrator",
                    "company": "Enterprise Corp",
                    "duration": "2017-2019",
                    "description": "Managed Linux servers and network infrastructure. Implemented monitoring solutions using Prometheus and Grafana. Automated deployment processes and improved system reliability."
                }
            ],
            "projects": [
                {
                    "name": "Multi-Cloud Infrastructure Platform",
                    "description": "Built automated infrastructure provisioning across AWS and Azure",
                    "technologies": "Terraform, Ansible, Kubernetes, Docker, Python",
                    "impact": "Reduced deployment time by 80%"
                },
                {
                    "name": "Monitoring and Alerting System",
                    "description": "Comprehensive monitoring solution for microservices architecture",
                    "technologies": "Prometheus, Grafana, ELK Stack, Kubernetes",
                    "impact": "Improved system uptime to 99.9%"
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "field": "Information Technology",
                    "institution": "Georgia Tech",
                    "year": "2017",
                    "gpa": "3.5/4.0"
                }
            ],
            "certifications": [
                "AWS Certified Solutions Architect - Professional",
                "Certified Kubernetes Administrator (CKA)",
                "HashiCorp Certified: Terraform Associate"
            ]
        }
    ]


def create_sample_job_descriptions():
    """
    Create sample job descriptions for demonstration.
    
    Returns:
        List of sample job description dictionaries
    """
    return [
        {
            "job_title": "Senior Machine Learning Engineer",
            "company": "TechCorp AI Division",
            "skills": [
                "Python", "TensorFlow", "PyTorch", "Machine Learning",
                "Deep Learning", "AWS", "Docker", "Kubernetes", "MLOps"
            ],
            "requirements": [
                "5+ years of ML engineering experience",
                "Strong Python programming skills",
                "Experience with TensorFlow or PyTorch",
                "Cloud platform experience (AWS/GCP/Azure)",
                "Experience with containerization and orchestration"
            ],
            "responsibilities": [
                "Design and implement ML models for production",
                "Build and maintain ML pipelines",
                "Collaborate with data scientists and engineers",
                "Optimize model performance and scalability",
                "Mentor junior team members"
            ],
            "url": "https://example.com/ml-engineer-job"
        },
        {
            "job_title": "Full Stack Developer",
            "company": "WebDev Solutions",
            "skills": [
                "JavaScript", "React", "Node.js", "TypeScript",
                "MongoDB", "PostgreSQL", "REST APIs", "GraphQL"
            ],
            "requirements": [
                "3+ years of full stack development experience",
                "Proficiency in JavaScript and modern frameworks",
                "Experience with both SQL and NoSQL databases",
                "Knowledge of RESTful API design",
                "Familiarity with version control (Git)"
            ],
            "responsibilities": [
                "Develop responsive web applications",
                "Build and maintain backend APIs",
                "Collaborate with UI/UX designers",
                "Write clean, maintainable code",
                "Participate in code reviews and testing"
            ],
            "url": "https://example.com/fullstack-developer-job"
        },
        {
            "job_title": "DevOps Engineer",
            "company": "CloudScale Inc.",
            "skills": [
                "AWS", "Docker", "Kubernetes", "Terraform", "Jenkins",
                "Python", "Bash", "Linux", "CI/CD", "Monitoring"
            ],
            "requirements": [
                "4+ years of DevOps/SRE experience",
                "Strong experience with AWS or other cloud platforms",
                "Proficiency with containerization (Docker/Kubernetes)",
                "Infrastructure as Code experience (Terraform/CloudFormation)",
                "Experience with CI/CD pipeline implementation"
            ],
            "responsibilities": [
                "Design and maintain cloud infrastructure",
                "Implement CI/CD pipelines",
                "Monitor system performance and reliability",
                "Automate deployment and scaling processes",
                "Ensure security and compliance standards"
            ],
            "url": "https://example.com/devops-engineer-job"
        }
    ]


def demonstrate_integration():
    """
    Demonstrate the integration between JDExtractorAgent and ProfileRAGAgent.
    """
    print("Multi-Agent Resume Optimizer - Profile RAG Integration Demo")
    print("=" * 70)
    
    # Get sample data
    sample_profiles = create_sample_profiles()
    sample_jobs = create_sample_job_descriptions()
    
    # Test with different database types
    for db_type in ["faiss", "chroma"]:
        print(f"\nTesting with {db_type.upper()} Database:")
        print("-" * 50)
        
        try:
            # Initialize ProfileRAGAgent
            rag_agent = ProfileRAGAgent(
                db_type=db_type,
                db_path=f"./demo_data/{db_type}_profiles",
                similarity_threshold=0.3,  # Lower threshold for demo
                max_results=3
            )
            
            # Initialize database
            if not rag_agent.initialize_database(force_recreate=True):
                print(f"Failed to initialize {db_type} database")
                continue
            
            # Add sample profiles to database
            print("Loading applicant profiles...")
            for profile in sample_profiles:
                if rag_agent.add_profile_data(profile):
                    print(f"  Added: {profile['name']} ({profile['profile_id']})")
                else:
                    print(f"  Failed to add: {profile['name']}")
            
            # Save database
            rag_agent.save_database()
            
            # Get database statistics
            stats = rag_agent.get_database_stats()
            print(f"\nDatabase Statistics:")
            print(f"  Total profiles: {stats['total_profiles']}")
            print(f"  Database type: {stats['db_type']}")
            print(f"  Similarity threshold: {stats['similarity_threshold']}")
            
            # Test profile retrieval for each job
            print(f"\nProfile Retrieval Results:")
            print("-" * 30)
            
            for job in sample_jobs:
                print(f"\nJob: {job['job_title']}")
                print(f"Company: {job['company']}")
                
                # Retrieve relevant profile
                relevant_data = rag_agent.retrieve_relevant_profile(job)
                
                print(f"Best Match: {relevant_data['profile_id']}")
                print(f"Total Matches: {relevant_data['total_matches']}")
                
                if relevant_data['similarity_scores']:
                    print(f"Similarity Score: {relevant_data['similarity_scores'][0]:.3f}")
                
                print(f"Relevant Skills ({len(relevant_data['relevant_skills'])}):")
                for skill in relevant_data['relevant_skills'][:5]:  # Show top 5
                    print(f"  - {skill}")
                
                print(f"Relevant Experience ({len(relevant_data['relevant_experience'])}):")
                for exp in relevant_data['relevant_experience'][:2]:  # Show top 2
                    if isinstance(exp, dict):
                        print(f"  - {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
                
                print(f"Relevant Projects ({len(relevant_data['relevant_projects'])}):")
                for proj in relevant_data['relevant_projects'][:2]:  # Show top 2
                    if isinstance(proj, dict):
                        print(f"  - {proj.get('name', 'N/A')}")
                
                # Show JSON output sample
                if relevant_data['profile_id'] != 'no_matches':
                    print("\nSample JSON Output (truncated):")
                    sample_output = {
                        "profile_id": relevant_data['profile_id'],
                        "relevant_skills": relevant_data['relevant_skills'][:3],
                        "similarity_score": relevant_data['similarity_scores'][0] if relevant_data['similarity_scores'] else 0,
                        "total_matches": relevant_data['total_matches']
                    }
                    print(json.dumps(sample_output, indent=2))
                
                print("-" * 30)
        
        except Exception as e:
            print(f"Error with {db_type}: {e}")
            if "dependencies not available" in str(e):
                print(f"Skipping {db_type} - dependencies not installed")
            else:
                import traceback
                traceback.print_exc()
    
    # Demonstrate workflow integration
    print("\n" + "=" * 70)
    print("Workflow Integration Example:")
    print("-" * 40)
    
    try:
        # Simulate JD extraction result
        jd_extraction_result = sample_jobs[0]  # Use first job as example
        
        print("Step 1: Job Description Extraction (Simulated)")
        print(f"  Job Title: {jd_extraction_result['job_title']}")
        print(f"  Skills Required: {', '.join(jd_extraction_result['skills'][:5])}")
        
        print("\nStep 2: Profile RAG Retrieval")
        rag_agent = ProfileRAGAgent(
            db_type="faiss",
            db_path="./demo_data/faiss_profiles",
            similarity_threshold=0.3
        )
        
        if rag_agent.initialize_database():
            # Load one profile for demo
            rag_agent.add_profile_data(sample_profiles[0])
            
            relevant_profile = rag_agent.retrieve_relevant_profile(jd_extraction_result)
            
            print(f"  Best matching profile: {relevant_profile['profile_id']}")
            print(f"  Matching skills: {len(relevant_profile['relevant_skills'])}")
            print(f"  Matching experience: {len(relevant_profile['relevant_experience'])}")
            
            print("\nStep 3: Ready for Content Alignment Agent")
            print("  Input: Job data + Relevant profile data")
            print("  Output: Aligned resume content")
            
            # Show what would be passed to the next agent
            next_agent_input = {
                "job_data": jd_extraction_result,
                "profile_data": relevant_profile,
                "workflow_step": "content_alignment"
            }
            
            print(f"\nData ready for next agent: {len(str(next_agent_input))} characters")
        
    except Exception as e:
        print(f"Workflow demo error: {e}")
    
    print("\n" + "=" * 70)
    print("Integration Demo Complete!")
    print("\nNext Steps:")
    print("1. Install dependencies: pip install faiss-cpu sentence-transformers chromadb")
    print("2. Integrate with JDExtractorAgent for real job URLs")
    print("3. Build ContentAlignmentAgent to use this output")
    print("4. Create end-to-end workflow with ResumePlannerAgent")


def main():
    """
    Main function to run the integration demonstration.
    """
    demonstrate_integration()


if __name__ == "__main__":
    main()

"""
Content Alignment Agent Integration Demo

This script demonstrates the complete workflow from JD extraction through
profile retrieval to content alignment, showing how the ContentAlignmentAgent
integrates with other agents in the multi-agent resume optimizer system.
"""

import sys
import os
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.content_alignment_agent import ContentAlignmentAgent


def create_sample_workflow_data():
    """
    Create sample data representing the output from previous agents.
    
    Returns:
        Tuple of (job_data, profile_data) representing JD extraction and RAG output
    """
    # Sample job data (from JDExtractorAgent)
    job_data = {
        "job_title": "Senior Machine Learning Engineer",
        "company": "AI Innovations Inc.",
        "skills": [
            "Python", "TensorFlow", "PyTorch", "Scikit-learn", "Pandas",
            "NumPy", "AWS", "Docker", "Kubernetes", "MLOps", "Git"
        ],
        "requirements": [
            "5+ years of machine learning experience",
            "Strong Python programming skills",
            "Experience with deep learning frameworks (TensorFlow/PyTorch)",
            "Cloud platform experience (AWS/GCP/Azure)",
            "Experience with containerization and orchestration",
            "Knowledge of MLOps practices and tools",
            "Strong mathematical background in statistics and linear algebra"
        ],
        "responsibilities": [
            "Design and implement machine learning models for production",
            "Build and maintain ML pipelines and infrastructure",
            "Collaborate with data scientists and software engineers",
            "Optimize model performance and scalability",
            "Mentor junior team members and conduct code reviews",
            "Research and evaluate new ML techniques and technologies"
        ],
        "url": "https://example.com/ml-engineer-job"
    }
    
    # Sample profile data (from ProfileRAGAgent)
    profile_data = {
        "profile_id": "alice_ml_engineer",
        "name": "Alice Johnson",
        "relevant_skills": [
            "Python", "Machine Learning", "TensorFlow", "PyTorch", 
            "Scikit-learn", "Pandas", "NumPy", "AWS", "Docker", 
            "Kubernetes", "SQL", "Git", "Statistics", "Linear Algebra"
        ],
        "relevant_experience": [
            {
                "title": "Senior ML Engineer",
                "company": "AI Innovations Inc.",
                "duration": "2021-2024",
                "description": "Led development of recommendation systems using TensorFlow and PyTorch. Deployed ML models on AWS using Docker and Kubernetes. Improved model accuracy by 25% through feature engineering and hyperparameter tuning. Mentored 3 junior engineers and established MLOps best practices."
            },
            {
                "title": "Data Scientist",
                "company": "DataCorp Solutions",
                "duration": "2019-2021",
                "description": "Built predictive models for customer churn analysis using Python and scikit-learn. Developed ETL pipelines processing 10M+ records daily. Created data visualizations and reports for stakeholders. Collaborated with engineering teams on model deployment."
            },
            {
                "title": "ML Research Intern",
                "company": "University AI Lab",
                "duration": "2018-2019",
                "description": "Researched deep learning techniques for computer vision applications. Implemented neural networks using TensorFlow and conducted experiments on large datasets. Published 2 papers in peer-reviewed conferences."
            }
        ],
        "relevant_projects": [
            {
                "name": "Real-time Fraud Detection System",
                "description": "Developed ML-powered fraud detection system processing 1M+ transactions daily using ensemble methods and real-time feature engineering",
                "technologies": "Python, TensorFlow, Apache Kafka, Redis, PostgreSQL, AWS",
                "impact": "Reduced fraud losses by 40% and false positives by 30%"
            },
            {
                "name": "Customer Segmentation Platform",
                "description": "Built unsupervised learning system for customer segmentation using clustering algorithms and dimensionality reduction techniques",
                "technologies": "Python, Scikit-learn, AWS SageMaker, S3, Docker",
                "impact": "Increased marketing ROI by 30% through targeted campaigns"
            }
        ],
        "relevant_education": [
            {
                "degree": "Master of Science",
                "field": "Machine Learning",
                "institution": "Stanford University",
                "year": "2019",
                "gpa": "3.8/4.0"
            }
        ],
        "similarity_scores": [0.85, 0.72],
        "total_matches": 2
    }
    
    return job_data, profile_data


def demonstrate_content_alignment():
    """
    Demonstrate the ContentAlignmentAgent functionality with realistic data.
    """
    print("Multi-Agent Resume Optimizer - Content Alignment Demo")
    print("=" * 65)
    
    # Get sample workflow data
    job_data, profile_data = create_sample_workflow_data()
    
    print("Workflow Step 3: Content Alignment")
    print("-" * 40)
    print(f"Job: {job_data['job_title']}")
    print(f"Company: {job_data['company']}")
    print(f"Applicant: {profile_data['name']} ({profile_data['profile_id']})")
    print(f"Profile Match Score: {profile_data['similarity_scores'][0]:.3f}")
    print()
    
    # Initialize ContentAlignmentAgent
    alignment_agent = ContentAlignmentAgent(
        keyword_weight=1.0,
        experience_weight=1.5,
        skills_weight=1.2,
        min_keyword_length=3
    )
    
    print("Step 1: Keyword Analysis")
    print("-" * 25)
    
    # Extract and display job keywords
    job_keywords = alignment_agent.extract_job_keywords(job_data)
    print("Job Keywords by Category:")
    for category, keywords in job_keywords.items():
        if keywords and category != 'all':
            print(f"  {category.title()}: {', '.join(list(keywords)[:6])}")
    print(f"  Total unique keywords: {len(job_keywords['all'])}")
    print()
    
    print("Step 2: Content Alignment Process")
    print("-" * 35)
    
    # Perform content alignment
    aligned_content = alignment_agent.align_content(job_data, profile_data)
    
    # Display alignment results
    metadata = aligned_content['alignment_metadata']
    print("Alignment Scores:")
    print(f"  Overall Alignment: {metadata['overall_alignment_score']:.3f}")
    print(f"  Skills Alignment: {metadata['skills_alignment_score']:.3f}")
    print(f"  Experience Alignment: {metadata['experience_alignment_score']:.3f}")
    print(f"  Matching Keywords: {len(metadata['matching_keywords'])}")
    print()
    
    print("Step 3: Aligned Content Sections")
    print("-" * 35)
    
    # Show aligned summary
    sections = aligned_content['aligned_sections']
    print("Professional Summary (Aligned):")
    print(f'  "{sections["summary"]}"')
    print()
    
    # Show skills alignment
    skills_data = sections['skills']
    print(f"Skills Alignment ({len(skills_data['matching_skills'])} matching):")
    print("  Top Aligned Skills:")
    for i, skill in enumerate(skills_data['aligned_skills'][:6], 1):
        score = skills_data['skill_scores'].get(skill, 0)
        status = "[MATCH]" if skill in skills_data['matching_skills'] else "      "
        print(f"    {i}. {status} {skill} (score: {score:.3f})")
    print()
    
    # Show skills by category
    categories = skills_data['skill_categories']
    print("  Skills by Category:")
    for category, skills in categories.items():
        if skills:
            print(f"    {category.title()}: {', '.join(skills[:4])}")
    print()
    
    # Show experience alignment
    experiences = sections['experience']
    print("Experience Alignment (Top 3):")
    for i, exp in enumerate(experiences[:3], 1):
        print(f"  {i}. {exp['title']} at {exp['company']}")
        print(f"     Alignment Score: {exp.get('alignment_score', 0):.3f}")
        print(f"     Matching Keywords: {', '.join(exp.get('matching_keywords', [])[:5])}")
        
        # Show original vs aligned description
        original_desc = exp.get('description', '')[:80] + "..."
        aligned_desc = exp.get('aligned_description', original_desc)[:80] + "..."
        
        print(f"     Original: {original_desc}")
        if 'aligned_description' in exp and exp['aligned_description'] != exp.get('description', ''):
            print(f"     Aligned:  {aligned_desc}")
        print()
    
    print("Step 4: Recommendations")
    print("-" * 25)
    recommendations = aligned_content['recommendations']
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    print()
    
    print("Step 5: Output for Next Agent")
    print("-" * 30)
    
    # Prepare data for ATSOptimizerAgent
    ats_input = {
        "profile_id": aligned_content['profile_id'],
        "job_title": aligned_content['job_title'],
        "aligned_summary": sections['summary'],
        "prioritized_skills": skills_data['aligned_skills'][:10],
        "optimized_experiences": [
            {
                "title": exp['title'],
                "company": exp['company'],
                "description": exp.get('aligned_description', exp.get('description', '')),
                "alignment_score": exp.get('alignment_score', 0),
                "matching_keywords": exp.get('matching_keywords', [])
            }
            for exp in experiences[:3]
        ],
        "job_keywords": list(job_keywords['all']),
        "overall_alignment_score": metadata['overall_alignment_score']
    }
    
    print("Data prepared for ATS Optimizer Agent:")
    print(f"  Profile ID: {ats_input['profile_id']}")
    print(f"  Prioritized Skills: {len(ats_input['prioritized_skills'])}")
    print(f"  Optimized Experiences: {len(ats_input['optimized_experiences'])}")
    print(f"  Job Keywords: {len(ats_input['job_keywords'])}")
    print(f"  Data size: {len(str(ats_input))} characters")
    print()
    
    # Show sample JSON output
    print("Sample JSON Output (truncated):")
    sample_output = {
        "profile_id": aligned_content["profile_id"],
        "job_title": aligned_content["job_title"],
        "alignment_metadata": {
            "overall_alignment_score": metadata["overall_alignment_score"],
            "matching_keywords_count": len(metadata["matching_keywords"])
        },
        "aligned_sections": {
            "summary": sections["summary"][:100] + "...",
            "top_skills": skills_data["aligned_skills"][:5],
            "experience_count": len(experiences)
        },
        "recommendations_count": len(recommendations)
    }
    print(json.dumps(sample_output, indent=2))


def demonstrate_keyword_matching_algorithm():
    """
    Demonstrate the core keyword matching algorithm with various scenarios.
    """
    print("\n" + "=" * 65)
    print("Keyword Matching Algorithm Demonstration")
    print("-" * 45)
    
    agent = ContentAlignmentAgent()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "High Alignment - Perfect Match",
            "job_keywords": {"python", "machine", "learning", "tensorflow", "aws"},
            "applicant_text": "Experienced Python developer with machine learning expertise using TensorFlow on AWS"
        },
        {
            "name": "Medium Alignment - Partial Match", 
            "job_keywords": {"python", "machine", "learning", "tensorflow", "aws"},
            "applicant_text": "Python developer with web development experience using Django and PostgreSQL"
        },
        {
            "name": "Low Alignment - Minimal Match",
            "job_keywords": {"python", "machine", "learning", "tensorflow", "aws"},
            "applicant_text": "Java developer with Spring Boot experience and Oracle database knowledge"
        },
        {
            "name": "No Alignment - No Match",
            "job_keywords": {"python", "machine", "learning", "tensorflow", "aws"},
            "applicant_text": "Graphic designer with Photoshop and Illustrator experience"
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\nScenario: {scenario['name']}")
        print(f"Job Keywords: {', '.join(scenario['job_keywords'])}")
        print(f"Applicant Text: {scenario['applicant_text']}")
        
        # Calculate alignment score
        alignment_score = agent.calculate_alignment_score(
            scenario['applicant_text'], 
            scenario['job_keywords']
        )
        
        # Extract applicant keywords
        applicant_keywords = agent.extract_keywords(scenario['applicant_text'])
        matching_keywords = applicant_keywords.intersection(scenario['job_keywords'])
        
        print(f"Alignment Score: {alignment_score:.3f}")
        print(f"Matching Keywords: {', '.join(matching_keywords) if matching_keywords else 'None'}")
        
        # Interpretation
        if alignment_score >= 0.7:
            interpretation = "Excellent match - strong alignment"
        elif alignment_score >= 0.4:
            interpretation = "Good match - moderate alignment"
        elif alignment_score >= 0.1:
            interpretation = "Weak match - limited alignment"
        else:
            interpretation = "Poor match - no significant alignment"
        
        print(f"Interpretation: {interpretation}")
        print("-" * 50)


def main():
    """
    Main function to run the content alignment demonstration.
    """
    try:
        # Main content alignment demo
        demonstrate_content_alignment()
        
        # Keyword matching algorithm demo
        demonstrate_keyword_matching_algorithm()
        
        print("\n" + "=" * 65)
        print("Content Alignment Integration Demo Complete!")
        print("\nKey Features Demonstrated:")
        print("+ Job keyword extraction and categorization")
        print("+ Skills alignment and prioritization")
        print("+ Experience highlighting and rephrasing")
        print("+ Professional summary generation")
        print("+ Alignment scoring and recommendations")
        print("+ Integration with workflow pipeline")
        
        print("\nNext Steps:")
        print("1. Pass aligned content to ATSOptimizerAgent")
        print("2. Optimize for ATS keyword density and formatting")
        print("3. Generate final LaTeX resume with LaTeXFormatterAgent")
        print("4. Complete end-to-end resume optimization workflow")
        
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

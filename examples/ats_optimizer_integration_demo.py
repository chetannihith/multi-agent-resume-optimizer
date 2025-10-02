"""
ATS Optimizer Agent Integration Demo

This script demonstrates the complete workflow from content alignment through
ATS optimization, showing how the ATSOptimizerAgent evaluates and improves
resume content for ATS compatibility with scoring and auto-fix capabilities.
"""

import sys
import os
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.ats_optimizer_agent import ATSOptimizerAgent


def create_sample_aligned_resumes():
    """
    Create sample aligned resume data representing different ATS scenarios.
    
    Returns:
        List of sample aligned resume dictionaries
    """
    # High-scoring resume (should get 90+ ATS score)
    high_score_resume = {
        "profile_id": "alice_ml_engineer",
        "job_title": "Senior Machine Learning Engineer",
        "aligned_sections": {
            "summary": "Experienced Machine Learning Engineer with 5+ years of expertise in Python, TensorFlow, and PyTorch. Specialized in developing scalable ML models and deploying them on AWS cloud infrastructure using Docker and Kubernetes. Proven track record of improving model accuracy and system performance.",
            "skills": {
                "aligned_skills": [
                    "Python", "Machine Learning", "TensorFlow", "PyTorch", 
                    "Scikit-learn", "AWS", "Docker", "Kubernetes", "MLOps",
                    "Deep Learning", "Neural Networks", "Data Science"
                ],
                "alignment_score": 0.92
            },
            "experience": [
                {
                    "title": "Senior ML Engineer",
                    "company": "AI Innovations Inc.",
                    "duration": "2021-2024",
                    "description": "Led development of recommendation systems using TensorFlow and PyTorch. Deployed ML models on AWS using Docker and Kubernetes. Improved model accuracy by 25% through feature engineering and hyperparameter tuning.",
                    "alignment_score": 0.95
                },
                {
                    "title": "Data Scientist",
                    "company": "DataCorp Solutions", 
                    "duration": "2019-2021",
                    "description": "Built predictive models for customer churn analysis using Python and scikit-learn. Developed ETL pipelines processing 10M+ records daily using Apache Spark and AWS.",
                    "alignment_score": 0.88
                }
            ],
            "education": [
                {
                    "degree": "Master of Science",
                    "field": "Machine Learning",
                    "institution": "Stanford University",
                    "year": "2019"
                }
            ],
            "job_keywords": {
                "all": [
                    "python", "machine", "learning", "tensorflow", "pytorch", 
                    "aws", "docker", "kubernetes", "mlops", "deep", "neural",
                    "networks", "data", "science", "models", "algorithms"
                ]
            }
        }
    }
    
    # Medium-scoring resume (should get 70-89 ATS score)
    medium_score_resume = {
        "profile_id": "bob_developer",
        "job_title": "Python Developer",
        "aligned_sections": {
            "summary": "Python developer with web development experience",
            "skills": {
                "aligned_skills": ["Python", "Django", "JavaScript", "HTML", "CSS"],
                "alignment_score": 0.65
            },
            "experience": [
                {
                    "title": "Web Developer",
                    "company": "WebCorp",
                    "description": "Built websites using Python and Django framework",
                    "alignment_score": 0.70
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "institution": "Local University"
                }
            ],
            "job_keywords": {
                "all": [
                    "python", "django", "flask", "postgresql", "redis", "aws",
                    "docker", "git", "rest", "apis", "web", "development",
                    "scalable", "microservices", "testing", "ci", "cd"
                ]
            }
        }
    }
    
    # Low-scoring resume (should get <70 ATS score and trigger auto-fix)
    low_score_resume = {
        "profile_id": "charlie_newgrad",
        "job_title": "Software Engineer",
        "aligned_sections": {
            "summary": "Recent graduate looking for opportunities",
            "skills": {
                "aligned_skills": ["Java", "C++", "Algorithms"],
                "alignment_score": 0.30
            },
            # Missing experience section
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "institution": "University"
                }
            ],
            "job_keywords": {
                "all": [
                    "python", "django", "flask", "postgresql", "redis", "aws",
                    "docker", "kubernetes", "microservices", "rest", "apis",
                    "machine", "learning", "tensorflow", "data", "science"
                ]
            }
        }
    }
    
    return [high_score_resume, medium_score_resume, low_score_resume]


def demonstrate_ats_optimization():
    """
    Demonstrate the ATSOptimizerAgent functionality with different resume scenarios.
    """
    print("Multi-Agent Resume Optimizer - ATS Optimization Demo")
    print("=" * 70)
    
    # Get sample resumes
    sample_resumes = create_sample_aligned_resumes()
    
    print("Workflow Step 4: ATS Optimization")
    print("-" * 40)
    
    # Initialize ATSOptimizerAgent with different configurations
    agents = [
        {
            "name": "Standard ATS Agent",
            "agent": ATSOptimizerAgent(
                target_ats_score=90,
                keyword_density_weight=0.4,
                section_weight=0.3,
                formatting_weight=0.3
            )
        },
        {
            "name": "Keyword-Focused Agent",
            "agent": ATSOptimizerAgent(
                target_ats_score=85,
                keyword_density_weight=0.6,  # Higher weight on keywords
                section_weight=0.2,
                formatting_weight=0.2
            )
        }
    ]
    
    # Test each resume with each agent configuration
    for agent_config in agents:
        agent_name = agent_config["name"]
        agent = agent_config["agent"]
        
        print(f"\n{agent_name} Results:")
        print("=" * 50)
        
        for i, resume in enumerate(sample_resumes, 1):
            print(f"\nResume {i}: {resume['profile_id']} - {resume['job_title']}")
            print("-" * 60)
            
            # Perform ATS optimization
            optimization_results = agent.optimize_resume(resume)
            
            # Display main results
            ats_analysis = optimization_results['ats_analysis']
            print(f"ATS Score: {ats_analysis['ats_score']}/100 ({ats_analysis['category']})")
            print(f"Status: {ats_analysis['status']}")
            print(f"Meets Target: {'YES' if ats_analysis['meets_target'] else 'NO'}")
            
            # Show score breakdown
            breakdown = ats_analysis['score_breakdown']
            print(f"Score Breakdown:")
            print(f"  Keyword Score: {breakdown['keyword_score']}/100")
            print(f"  Section Score: {breakdown['section_score']}/100") 
            print(f"  Formatting Score: {breakdown['formatting_score']}/100")
            
            # Show keyword analysis
            keyword_analysis = optimization_results['keyword_analysis']
            print(f"Keyword Analysis:")
            print(f"  Density: {keyword_analysis['density_score']:.1%}")
            print(f"  Matched: {keyword_analysis['matched_count']}/{keyword_analysis['total_job_keywords']}")
            if keyword_analysis['missing_keywords']:
                missing = ', '.join(keyword_analysis['missing_keywords'][:5])
                print(f"  Missing: {missing}...")
            
            # Show section analysis
            section_analysis = optimization_results['section_analysis']
            print(f"Section Analysis:")
            print(f"  Present: {section_analysis['present_count']}/{section_analysis['total_required']}")
            if section_analysis['missing_sections']:
                print(f"  Missing: {', '.join(section_analysis['missing_sections'])}")
            
            # Show suggestions
            suggestions = optimization_results['suggestions']
            if suggestions:
                print(f"Suggestions ({len(suggestions)}):")
                for j, suggestion in enumerate(suggestions[:3], 1):
                    priority_marker = "!" if suggestion['priority'] == 'High' else "*"
                    print(f"  {j}. {priority_marker} [{suggestion['category']}] {suggestion['suggestion']}")
            
            # Show auto-fix results
            auto_fix = optimization_results['auto_fix_results']
            if auto_fix and auto_fix['fix_count'] > 0:
                print(f"Auto-Fix Applied:")
                print(f"  Fixes: {auto_fix['fix_count']}")
                print(f"  Score Improvement: +{auto_fix.get('score_improvement', 0)}")
                print(f"  Updated Score: {auto_fix.get('updated_ats_score', 'N/A')}")
                for fix in auto_fix['fixes_applied'][:2]:
                    print(f"    - {fix}")
            else:
                print("Auto-Fix: No fixes needed")
            
            print()


def demonstrate_keyword_density_scoring():
    """
    Demonstrate the keyword density scoring function with various scenarios.
    """
    print("\n" + "=" * 70)
    print("Keyword Density Scoring Function Demonstration")
    print("-" * 50)
    
    agent = ATSOptimizerAgent()
    
    # Test scenarios for keyword density
    test_scenarios = [
        {
            "name": "Perfect Match - ML Engineer",
            "resume_keywords": {
                "python", "machine", "learning", "tensorflow", "aws", 
                "docker", "kubernetes", "data", "science", "models"
            },
            "job_keywords": {
                "python", "machine", "learning", "tensorflow", "aws",
                "docker", "kubernetes", "data", "science", "models"
            }
        },
        {
            "name": "High Match - 80% Coverage",
            "resume_keywords": {
                "python", "django", "postgresql", "aws", "docker",
                "git", "rest", "apis", "javascript", "html"
            },
            "job_keywords": {
                "python", "django", "postgresql", "aws", "docker",
                "redis", "flask", "microservices", "kubernetes", "ci"
            }
        },
        {
            "name": "Medium Match - 50% Coverage",
            "resume_keywords": {
                "python", "web", "development", "javascript", "html",
                "css", "react", "node", "mongodb", "express"
            },
            "job_keywords": {
                "python", "django", "flask", "postgresql", "redis",
                "aws", "docker", "kubernetes", "microservices", "rest"
            }
        },
        {
            "name": "Low Match - 20% Coverage",
            "resume_keywords": {
                "java", "spring", "hibernate", "mysql", "tomcat",
                "maven", "junit", "eclipse", "intellij", "git"
            },
            "job_keywords": {
                "python", "django", "flask", "postgresql", "redis",
                "aws", "docker", "kubernetes", "microservices", "git"
            }
        },
        {
            "name": "No Match - 0% Coverage",
            "resume_keywords": {
                "photoshop", "illustrator", "indesign", "creative", "design",
                "graphics", "branding", "typography", "layout", "visual"
            },
            "job_keywords": {
                "python", "django", "flask", "postgresql", "redis",
                "aws", "docker", "kubernetes", "microservices", "rest"
            }
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\nScenario: {scenario['name']}")
        print(f"Resume Keywords: {', '.join(list(scenario['resume_keywords'])[:5])}...")
        print(f"Job Keywords: {', '.join(list(scenario['job_keywords'])[:5])}...")
        
        # Calculate keyword density
        density_result = agent.calculate_keyword_density(
            scenario['resume_keywords'], 
            scenario['job_keywords']
        )
        
        print(f"Keyword Density Score: {density_result['density_score']:.1%}")
        print(f"Matched Keywords: {density_result['matched_count']}/{density_result['total_job_keywords']}")
        
        if density_result['matching_keywords']:
            matching = ', '.join(density_result['matching_keywords'][:3])
            print(f"Sample Matches: {matching}...")
        
        if density_result['missing_keywords']:
            missing = ', '.join(density_result['missing_keywords'][:3])
            print(f"Sample Missing: {missing}...")
        
        # Provide interpretation
        score = density_result['density_score']
        if score >= 0.9:
            interpretation = "Excellent - Resume strongly matches job requirements"
        elif score >= 0.7:
            interpretation = "Good - Strong alignment with job requirements"
        elif score >= 0.5:
            interpretation = "Fair - Moderate alignment, room for improvement"
        elif score >= 0.3:
            interpretation = "Poor - Limited alignment with job requirements"
        else:
            interpretation = "Very Poor - Minimal or no alignment"
        
        print(f"Interpretation: {interpretation}")
        print("-" * 50)


def demonstrate_auto_fix_functionality():
    """
    Demonstrate the auto-fix functionality with before/after comparisons.
    """
    print("\n" + "=" * 70)
    print("Auto-Fix Functionality Demonstration")
    print("-" * 45)
    
    agent = ATSOptimizerAgent(target_ats_score=85)
    
    # Create a resume that needs significant fixes
    problematic_resume = {
        "profile_id": "needs_fixing",
        "job_title": "Data Scientist",
        "aligned_sections": {
            "summary": "Looking for a job",  # Poor summary
            # Missing skills section
            # Missing experience section
            # Missing education section
            "job_keywords": {
                "all": [
                    "python", "machine", "learning", "tensorflow", "pandas",
                    "numpy", "scikit", "learn", "data", "science", "statistics",
                    "visualization", "jupyter", "aws", "sql", "postgresql"
                ]
            }
        }
    }
    
    print("BEFORE Auto-Fix:")
    print("-" * 20)
    
    # Show initial state
    initial_results = agent.optimize_resume(problematic_resume)
    initial_score = initial_results['ats_analysis']['ats_score']
    print(f"Initial ATS Score: {initial_score}/100")
    
    # Show what's missing
    section_analysis = initial_results['section_analysis']
    keyword_analysis = initial_results['keyword_analysis']
    
    print(f"Missing Sections: {', '.join(section_analysis['missing_sections'])}")
    print(f"Keyword Density: {keyword_analysis['density_score']:.1%}")
    print(f"Missing Keywords: {len(keyword_analysis['missing_keywords'])} keywords")
    
    print(f"\nSuggestions Generated: {len(initial_results['suggestions'])}")
    for i, suggestion in enumerate(initial_results['suggestions'][:3], 1):
        auto_fix_status = "Auto-fixable" if suggestion.get('auto_fixable') else "Manual fix needed"
        print(f"  {i}. {suggestion['suggestion']} ({auto_fix_status})")
    
    print("\nAFTER Auto-Fix:")
    print("-" * 15)
    
    # Show auto-fix results
    auto_fix = initial_results['auto_fix_results']
    if auto_fix:
        print(f"Fixes Applied: {auto_fix['fix_count']}")
        print(f"Updated ATS Score: {auto_fix.get('updated_ats_score', 'N/A')}/100")
        print(f"Score Improvement: +{auto_fix.get('score_improvement', 0)}")
        
        print("\nFixes Applied:")
        for i, fix in enumerate(auto_fix['fixes_applied'], 1):
            print(f"  {i}. {fix}")
        
        # Show improved content structure
        fixed_content = auto_fix['fixed_content']
        print(f"\nImproved Content Structure:")
        print(f"  Summary: {'Present' if 'summary' in fixed_content else 'Missing'}")
        print(f"  Skills: {'Present' if 'skills' in fixed_content else 'Missing'}")
        print(f"  Experience: {'Present' if 'experience' in fixed_content else 'Missing'}")
        print(f"  Education: {'Present' if 'education' in fixed_content else 'Missing'}")
        
        if 'skills' in fixed_content and 'aligned_skills' in fixed_content['skills']:
            skills_count = len(fixed_content['skills']['aligned_skills'])
            print(f"  Added Skills: {skills_count} keywords")
    
    print("\nAuto-Fix Effectiveness:")
    if auto_fix and auto_fix.get('score_improvement', 0) > 0:
        improvement = auto_fix['score_improvement']
        if improvement >= 20:
            effectiveness = "Highly Effective"
        elif improvement >= 10:
            effectiveness = "Moderately Effective"
        else:
            effectiveness = "Minimally Effective"
        print(f"  {effectiveness} (+{improvement} points)")
    else:
        print("  No improvement or fixes not applicable")


def main():
    """
    Main function to run the ATS optimization demonstration.
    """
    try:
        # Main ATS optimization demo
        demonstrate_ats_optimization()
        
        # Keyword density scoring demo
        demonstrate_keyword_density_scoring()
        
        # Auto-fix functionality demo
        demonstrate_auto_fix_functionality()
        
        print("\n" + "=" * 70)
        print("ATS Optimizer Integration Demo Complete!")
        
        print("\nKey Features Demonstrated:")
        print("+ Comprehensive ATS scoring (0-100 scale)")
        print("+ Keyword density analysis and optimization")
        print("+ Section presence validation")
        print("+ Formatting rules compliance checking")
        print("+ Intelligent suggestion generation")
        print("+ Automatic issue fixing capabilities")
        print("+ Configurable scoring weights")
        print("+ Before/after improvement tracking")
        
        print("\nATS Optimization Benefits:")
        print("- Improved resume parsing by ATS systems")
        print("- Higher keyword match rates")
        print("- Standardized section structure")
        print("- ATS-friendly formatting")
        print("- Automated compliance checking")
        print("- Quantified optimization scores")
        
        print("\nNext Steps:")
        print("1. Pass optimized content to LaTeXFormatterAgent")
        print("2. Generate final ATS-optimized resume in LaTeX format")
        print("3. Export to Overleaf-compatible format")
        print("4. Complete end-to-end resume optimization pipeline")
        
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

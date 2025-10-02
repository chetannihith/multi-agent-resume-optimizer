"""
Resume Planner Agent Demo

This script demonstrates how to use the ResumePlannerAgent to create
workflow plans for resume tailoring based on job descriptions.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.resume_planner_agent import ResumePlannerAgent


def main():
    """
    Demonstrate ResumePlannerAgent functionality with sample data.
    """
    print("Multi-Agent Resume Optimizer - Planner Demo")
    print("=" * 60)
    
    # Initialize the planner agent
    planner = ResumePlannerAgent()
    
    # Sample job description URLs (replace with real URLs for testing)
    sample_jobs = [
        {
            "url": "https://jobs.example.com/software-engineer",
            "title": "Software Engineer at TechCorp"
        },
        {
            "url": "https://careers.example.com/data-scientist",
            "title": "Data Scientist at DataCorp"
        },
        {
            "url": "https://hiring.example.com/product-manager",
            "title": "Product Manager at ProductCorp"
        }
    ]
    
    # Sample profile IDs
    sample_profiles = ["john_doe_2024", "jane_smith_dev", "alex_data_sci"]
    
    print(f"Workflow ID: {planner.workflow_id}")
    print(f"Created: {planner.created_at}")
    print()
    
    # Demonstrate simple plan creation
    print("Simple Workflow Plans:")
    print("-" * 40)
    
    for i, (job, profile_id) in enumerate(zip(sample_jobs, sample_profiles), 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Profile: {profile_id}")
        print(f"   URL: {job['url']}")
        
        try:
            # Create simple plan
            simple_plan = planner.create_simple_plan(job['url'], profile_id)
            
            print("   Workflow Steps:")
            for step in simple_plan['workflow']:
                print(f"     {step['step']}. {step['agent']} -> {step['output']}")
                
        except Exception as e:
            print(f"   ERROR: {e}")
    
    # Demonstrate detailed plan creation
    print("\n" + "=" * 60)
    print("Detailed Workflow Plan Example:")
    print("-" * 40)
    
    try:
        # Use first job for detailed example
        job = sample_jobs[0]
        profile_id = sample_profiles[0]
        
        detailed_plan = planner.generate_workflow_plan(job['url'], profile_id)
        
        print(f"Job: {job['title']}")
        print(f"Profile: {profile_id}")
        print(f"Estimated Duration: {detailed_plan['estimated_duration_minutes']} minutes")
        print(f"Final Output: {detailed_plan['outputs']['final_resume']}")
        print()
        
        print("Workflow Steps:")
        for step in detailed_plan['workflow']:
            deps = ", ".join(step['dependencies']) if step['dependencies'] else "None"
            print(f"  {step['step']}. {step['agent']}")
            print(f"     Description: {step['description']}")
            print(f"     Duration: {step['estimated_duration_minutes']} min")
            print(f"     Dependencies: {deps}")
            print(f"     Output: {step['outputs']['primary']}")
            print()
        
        print("Dependencies Graph:")
        for agent, deps in detailed_plan['dependencies'].items():
            deps_str = " -> ".join(deps) + " -> " if deps else ""
            print(f"  {deps_str}{agent}")
        
        print(f"\nIntermediate Files ({len(detailed_plan['outputs']['intermediate_files'])}):")
        for file in detailed_plan['outputs']['intermediate_files']:
            print(f"  - {file}")
            
    except Exception as e:
        print(f"ERROR creating detailed plan: {e}")
    
    # Demonstrate input validation
    print("\n" + "=" * 60)
    print("Input Validation Examples:")
    print("-" * 40)
    
    test_cases = [
        ("https://valid-job-url.com/job", "valid_profile_123", "Valid"),
        ("invalid-url", "valid_profile_123", "Invalid URL"),
        ("https://valid-job-url.com/job", "ab", "Profile ID too short"),
        ("", "valid_profile_123", "Empty URL"),
        ("https://valid-job-url.com/job", "", "Empty Profile ID")
    ]
    
    for job_url, profile_id, expected in test_cases:
        try:
            validation = planner.validate_inputs(job_url, profile_id)
            status = "VALID" if validation['valid'] else "INVALID"
            errors = validation['errors'][:1] if validation['errors'] else []
            error_msg = f" ({errors[0]})" if errors else ""
            print(f"  {status}: '{job_url[:30]}...' + '{profile_id}'{error_msg}")
        except Exception as e:
            print(f"  EXCEPTION: {e}")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("1. Replace sample URLs with real job posting URLs")
    print("2. Implement the individual agent classes")
    print("3. Set up CrewAI/LangGraph orchestration")
    print("4. Create RAG database for profile storage")
    print("5. Implement LaTeX template generation")
    print("\nResumePlannerAgent is ready for integration!")


if __name__ == "__main__":
    main()

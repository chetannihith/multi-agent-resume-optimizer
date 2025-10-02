"""
Simple demonstration of the ResumeWorkflow using LangGraph.

This script shows how to use the ResumeWorkflow class to orchestrate
all agents in the resume optimization pipeline.
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from workflow.resume_workflow import ResumeWorkflow


def main():
    """
    Demonstrate the ResumeWorkflow functionality.
    """
    print("Resume Workflow (LangGraph) Demonstration")
    print("=" * 50)
    
    try:
        # Initialize the workflow
        print("Initializing ResumeWorkflow...")
        workflow = ResumeWorkflow(
            template_path="templates/resume_template.tex",
            output_directory="output",
            rag_database_path="data/profiles",
            enable_logging=True,
            log_level="INFO"
        )
        
        # Get workflow status
        status = workflow.get_workflow_status()
        
        print(f"Workflow Name: {status['workflow_name']}")
        print(f"Version: {status['version']}")
        print(f"Agents Configured: {len(status['agents'])}")
        print()
        
        print("Workflow Steps:")
        for i, step in enumerate(status['workflow_steps'], 1):
            agent_name = {
                'extract_job_data': 'JDExtractorAgent',
                'retrieve_profile': 'ProfileRAGAgent', 
                'align_content': 'ContentAlignmentAgent',
                'optimize_ats': 'ATSOptimizerAgent',
                'generate_latex': 'LaTeXFormatterAgent'
            }.get(step, step)
            
            print(f"  {i}. {step} -> {agent_name}")
        
        print()
        print("Configuration:")
        config = status['configuration']
        print(f"  Template Path: {config['template_path']}")
        print(f"  Output Directory: {config['output_directory']}")
        print(f"  RAG Database: {config['rag_database_path']}")
        print()
        
        print("Workflow Features:")
        print("  - LangGraph-based orchestration")
        print("  - State management between agents")
        print("  - Comprehensive error handling")
        print("  - Detailed logging and monitoring")
        print("  - Automatic file generation")
        print("  - Overleaf compatibility validation")
        print()
        
        print("Usage Example:")
        print("  # Initialize workflow")
        print("  workflow = ResumeWorkflow()")
        print()
        print("  # Execute complete pipeline")
        print("  result = workflow.run_workflow(")
        print("      job_url='https://company.com/job-posting',")
        print("      profile_id='user_123'")
        print("  )")
        print()
        print("  # Check results")
        print("  if result['success']:")
        print("      print(f'LaTeX file: {result[\"latex_file_path\"]}') ")
        print("      print('Ready for Overleaf upload!')")
        print("  else:")
        print("      print(f'Errors: {result[\"errors\"]}') ")
        print()
        
        print("Note: For actual execution, ensure:")
        print("  1. Valid job description URL")
        print("  2. Profile data in RAG database")
        print("  3. All dependencies installed")
        print("  4. Network connectivity for job scraping")
        
        print("\n" + "=" * 50)
        print("Workflow initialized successfully!")
        print("Ready for resume optimization pipeline execution.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

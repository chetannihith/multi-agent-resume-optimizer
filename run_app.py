#!/usr/bin/env python3
"""
Startup script for the Multi-Agent Resume Optimizer Streamlit app.

This script provides a convenient way to start the application with
proper environment setup and validation.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'streamlit',
        'python-dotenv', 
        'groq',
        'langchain',
        'langgraph',
        'plotly',
        'fpdf2'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("[ERROR] Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n[INFO] Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("[SUCCESS] All dependencies are installed")
    return True


def check_environment():
    """Check environment configuration."""
    env_file = Path('.env')
    sample_env = Path('sample.env')
    
    if not env_file.exists():
        if sample_env.exists():
            print("[WARNING] .env file not found")
            print("[INFO] Copy sample.env to .env and configure your API keys:")
            print("   cp sample.env .env")
            print("   # Then edit .env with your actual API keys")
        else:
            print("[ERROR] Neither .env nor sample.env found")
            print("[INFO] Create .env file with required configuration")
        return False
    
    # Load and validate environment
    from dotenv import load_dotenv
    load_dotenv()
    
    groq_key = os.getenv('GROQ_API_KEY')
    if not groq_key or groq_key == 'your_groq_api_key_here':
        print("[ERROR] GROQ_API_KEY not configured in .env file")
        print("[INFO] Get your API key from: https://console.groq.com/")
        return False
    
    print("[SUCCESS] Environment configuration is valid")
    return True


def check_directories():
    """Check and create required directories."""
    required_dirs = [
        'templates',
        'output', 
        'data/profiles',
        'logs'
    ]
    
    created_dirs = []
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(dir_path)
    
    if created_dirs:
        print(f"[INFO] Created directories: {', '.join(created_dirs)}")
    
    # Check for template file
    template_path = Path('templates/resume_template.tex')
    if not template_path.exists():
        print("[WARNING] LaTeX template not found at templates/resume_template.tex")
        print("[INFO] The app will use a default template, but you may want to add your own")
    
    print("[SUCCESS] Directory structure is ready")
    return True


def get_streamlit_command():
    """Get the appropriate Streamlit command for the platform."""
    if platform.system() == "Windows":
        return ["python", "-m", "streamlit", "run", "app.py"]
    else:
        return ["streamlit", "run", "app.py"]


def main():
    """Main startup function."""
    print("Multi-Agent Resume Optimizer - Startup")
    print("=" * 50)
    
    # Check current directory
    if not Path('app.py').exists():
        print("[ERROR] app.py not found in current directory")
        print("[INFO] Please run this script from the project root directory")
        sys.exit(1)
    
    # Run all checks
    checks = [
        ("Dependencies", check_dependencies),
        ("Environment", check_environment), 
        ("Directories", check_directories)
    ]
    
    for check_name, check_func in checks:
        print(f"\n[INFO] Checking {check_name}...")
        if not check_func():
            print(f"\n[ERROR] {check_name} check failed")
            print("[INFO] Please fix the issues above and try again")
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("[SUCCESS] All checks passed! Starting Streamlit app...")
    print("[INFO] The app will open in your browser at: http://localhost:8501")
    print("[INFO] Press Ctrl+C to stop the application")
    print("=" * 50)
    
    # Start Streamlit app
    try:
        cmd = get_streamlit_command()
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n\n[INFO] Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Error starting Streamlit: {e}")
        print("[INFO] Try running manually: streamlit run app.py")
    except FileNotFoundError:
        print("\n[ERROR] Streamlit not found in PATH")
        print("[INFO] Install Streamlit: pip install streamlit")


if __name__ == "__main__":
    main()

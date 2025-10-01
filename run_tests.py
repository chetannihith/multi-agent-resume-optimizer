#!/usr/bin/env python3
"""
Test runner script for the Multi-Agent Resume Optimizer project.

This script provides an easy way to run all tests with different configurations
and generate test reports.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle the output."""
    print(f"\n{'='*60}")
    print(f"RUNNING: {description}")
    print(f"COMMAND: {command}")
    print('='*60)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}")
        print("STDOUT:")
        print(e.stdout)
        print("STDERR:")
        print(e.stderr)
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    required_packages = ['pytest', 'requests', 'beautifulsoup4', 'crewai']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True


def run_unit_tests():
    """Run unit tests."""
    return run_command(
        "python -m pytest tests/test_jd_extractor_agent.py -v",
        "Unit Tests for JDExtractorAgent"
    )


def run_crewai_tests():
    """Run CrewAI integration tests."""
    return run_command(
        "python -m pytest tests/test_crewai_integration.py -v",
        "CrewAI Integration Tests"
    )


def run_all_tests():
    """Run all tests."""
    return run_command(
        "python -m pytest tests/ -v --tb=short",
        "All Tests"
    )


def run_tests_with_coverage():
    """Run tests with coverage report."""
    return run_command(
        "python -m pytest tests/ --cov=src --cov-report=html --cov-report=term",
        "Tests with Coverage Report"
    )


def run_demo():
    """Run the complete demonstration."""
    return run_command(
        "python examples/complete_jd_extractor_demo.py",
        "Complete JDExtractorAgent Demonstration"
    )


def main():
    """Main test runner function."""
    print("Multi-Agent Resume Optimizer - Test Runner")
    print("="*60)
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Get command line arguments
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
    else:
        test_type = "all"
    
    success = True
    
    if test_type in ["unit", "all"]:
        success &= run_unit_tests()
    
    if test_type in ["crewai", "integration", "all"]:
        success &= run_crewai_tests()
    
    if test_type in ["coverage", "all"]:
        success &= run_tests_with_coverage()
    
    if test_type in ["demo", "all"]:
        success &= run_demo()
    
    if test_type == "all":
        # Run all tests together
        success &= run_all_tests()
    
    # Print summary
    print(f"\n{'='*60}")
    if success:
        print("✓ ALL TESTS PASSED!")
        print("The JDExtractorAgent is ready for production use.")
    else:
        print("✗ SOME TESTS FAILED!")
        print("Please check the output above for details.")
    print('='*60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

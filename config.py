"""
Configuration management for the Multi-Agent Resume Optimizer.

This module handles environment variables, API keys, and application settings
using python-dotenv for secure configuration management.
"""

import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Configuration class for the Resume Optimizer application.
    
    Manages all environment variables, API keys, and application settings
    with secure defaults and validation.
    """
    
    # Groq API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-8b-8192")
    
    # LangChain Configuration
    LANGCHAIN_TRACING_V2: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "resume-optimizer")
    
    # Application Configuration
    APP_TITLE: str = os.getenv("APP_TITLE", "Multi-Agent Resume Optimizer")
    APP_DESCRIPTION: str = os.getenv("APP_DESCRIPTION", "AI-powered resume optimization with 90%+ ATS score guarantee")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    SUPPORTED_FILE_TYPES: List[str] = os.getenv("SUPPORTED_FILE_TYPES", "json,txt").split(",")
    
    # Workflow Configuration
    DEFAULT_TEMPLATE_PATH: str = os.getenv("DEFAULT_TEMPLATE_PATH", "templates/resume_template.tex")
    DEFAULT_OUTPUT_DIR: str = os.getenv("DEFAULT_OUTPUT_DIR", "output")
    DEFAULT_RAG_DB_PATH: str = os.getenv("DEFAULT_RAG_DB_PATH", "data/profiles")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_DETAILED_LOGGING: bool = os.getenv("ENABLE_DETAILED_LOGGING", "true").lower() == "true"
    
    # UI Configuration
    THEME_PRIMARY_COLOR: str = os.getenv("THEME_PRIMARY_COLOR", "#FF6B6B")
    THEME_BACKGROUND_COLOR: str = os.getenv("THEME_BACKGROUND_COLOR", "#FFFFFF")
    THEME_SECONDARY_BACKGROUND_COLOR: str = os.getenv("THEME_SECONDARY_BACKGROUND_COLOR", "#F0F2F6")
    THEME_TEXT_COLOR: str = os.getenv("THEME_TEXT_COLOR", "#262730")
    
    # Performance Configuration
    MAX_CONCURRENT_WORKFLOWS: int = int(os.getenv("MAX_CONCURRENT_WORKFLOWS", "3"))
    WORKFLOW_TIMEOUT_SECONDS: int = int(os.getenv("WORKFLOW_TIMEOUT_SECONDS", "300"))
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    
    # Security Configuration
    ALLOWED_DOMAINS: List[str] = os.getenv("ALLOWED_DOMAINS", "linkedin.com,indeed.com,glassdoor.com,monster.com,ziprecruiter.com").split(",")
    MAX_REQUESTS_PER_HOUR: int = int(os.getenv("MAX_REQUESTS_PER_HOUR", "100"))
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """
        Validate configuration and return status.
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required API keys
        if not cls.GROQ_API_KEY:
            validation_results["errors"].append("GROQ_API_KEY is required")
            validation_results["valid"] = False
        
        # Check file paths
        if not os.path.exists(os.path.dirname(cls.DEFAULT_TEMPLATE_PATH)):
            validation_results["warnings"].append(f"Template directory does not exist: {os.path.dirname(cls.DEFAULT_TEMPLATE_PATH)}")
        
        if not os.path.exists(cls.DEFAULT_OUTPUT_DIR):
            validation_results["warnings"].append(f"Output directory does not exist: {cls.DEFAULT_OUTPUT_DIR}")
            try:
                os.makedirs(cls.DEFAULT_OUTPUT_DIR, exist_ok=True)
                validation_results["warnings"].append(f"Created output directory: {cls.DEFAULT_OUTPUT_DIR}")
            except Exception as e:
                validation_results["errors"].append(f"Cannot create output directory: {e}")
                validation_results["valid"] = False
        
        # Check numeric values
        if cls.MAX_FILE_SIZE_MB <= 0:
            validation_results["errors"].append("MAX_FILE_SIZE_MB must be positive")
            validation_results["valid"] = False
        
        if cls.WORKFLOW_TIMEOUT_SECONDS <= 0:
            validation_results["errors"].append("WORKFLOW_TIMEOUT_SECONDS must be positive")
            validation_results["valid"] = False
        
        return validation_results
    
    @classmethod
    def get_streamlit_config(cls) -> Dict[str, Any]:
        """
        Get Streamlit-specific configuration.
        
        Returns:
            Dictionary with Streamlit configuration
        """
        return {
            "page_title": cls.APP_TITLE,
            "page_icon": "📄",
            "layout": "wide",
            "initial_sidebar_state": "expanded",
            "menu_items": {
                "Get Help": "https://github.com/your-repo/resume-optimizer",
                "Report a bug": "https://github.com/your-repo/resume-optimizer/issues",
                "About": cls.APP_DESCRIPTION
            }
        }
    
    @classmethod
    def get_groq_config(cls) -> Dict[str, Any]:
        """
        Get Groq API configuration.
        
        Returns:
            Dictionary with Groq configuration
        """
        return {
            "api_key": cls.GROQ_API_KEY,
            "model": cls.GROQ_MODEL,
            "temperature": 0.1,
            "max_tokens": 4096,
            "top_p": 1,
            "stream": False
        }


# Create global config instance
config = Config()

# Validate configuration on import
validation_results = config.validate_config()
if not validation_results["valid"]:
    print("Configuration validation failed:")
    for error in validation_results["errors"]:
        print(f"  ERROR: {error}")

if validation_results["warnings"]:
    print("Configuration warnings:")
    for warning in validation_results["warnings"]:
        print(f"  WARNING: {warning}")


def setup_environment():
    """
    Setup environment variables for the application.
    """
    # Set LangChain environment variables
    if config.LANGCHAIN_TRACING_V2:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
    
    if config.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_API_KEY"] = config.LANGCHAIN_API_KEY
    
    if config.LANGCHAIN_PROJECT:
        os.environ["LANGCHAIN_PROJECT"] = config.LANGCHAIN_PROJECT
    
    # Set Groq environment variables
    if config.GROQ_API_KEY:
        os.environ["GROQ_API_KEY"] = config.GROQ_API_KEY


# Setup environment on import
setup_environment()

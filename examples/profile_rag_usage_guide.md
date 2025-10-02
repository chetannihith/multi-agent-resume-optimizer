# ProfileRAGAgent Usage Guide

## Overview

The `ProfileRAGAgent` is a sophisticated component of the Multi-Agent Resume Optimizer that retrieves relevant applicant information from vector databases based on job description requirements. It supports both FAISS and Chroma vector databases for efficient similarity search.

## Features

### 🔍 **Vector Database Support**
- **FAISS**: High-performance similarity search with CPU optimization
- **Chroma**: Modern vector database with built-in embedding management
- **Automatic Fallback**: Graceful handling when dependencies are missing

### 📊 **Intelligent Profile Matching**
- **Semantic Search**: Uses sentence transformers for meaningful similarity
- **Multi-field Analysis**: Considers skills, experience, projects, and education
- **Relevance Filtering**: Returns only the most relevant profile information
- **Similarity Scoring**: Provides confidence scores for matches

### 🛠 **Production-Ready Features**
- **Persistent Storage**: Saves and loads databases from disk
- **Error Handling**: Robust error handling with detailed logging
- **Performance Optimization**: Efficient indexing and search algorithms
- **Modular Design**: Easy integration with other agents

## Quick Start

### Installation

```bash
# Install required dependencies
pip install faiss-cpu sentence-transformers numpy chromadb
```

### Basic Usage

```python
from agents.profile_rag_agent import ProfileRAGAgent

# Initialize agent
agent = ProfileRAGAgent(
    db_type="faiss",  # or "chroma"
    db_path="./data/profiles",
    similarity_threshold=0.7,
    max_results=5
)

# Initialize database
agent.initialize_database()

# Add profile data
profile_data = {
    "profile_id": "john_doe_2024",
    "skills": ["Python", "Machine Learning", "AWS"],
    "experience": [
        {
            "title": "ML Engineer",
            "company": "TechCorp",
            "description": "Built ML models using Python and TensorFlow"
        }
    ],
    "projects": [
        {
            "name": "Recommendation System",
            "description": "ML-powered recommendations",
            "technologies": "Python, TensorFlow, AWS"
        }
    ]
}

agent.add_profile_data(profile_data)
agent.save_database()

# Retrieve relevant profile based on job description
job_data = {
    "job_title": "Senior ML Engineer",
    "skills": ["Python", "Machine Learning", "TensorFlow"],
    "requirements": ["5+ years ML experience", "Python expertise"]
}

relevant_profile = agent.retrieve_relevant_profile(job_data)
print(f"Best match: {relevant_profile['profile_id']}")
print(f"Relevant skills: {relevant_profile['relevant_skills']}")
```

## API Reference

### ProfileRAGAgent Class

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `db_type` | str | "faiss" | Database type ("faiss" or "chroma") |
| `db_path` | str | "./data/profiles" | Path to database files |
| `model_name` | str | "all-MiniLM-L6-v2" | Sentence transformer model |
| `similarity_threshold` | float | 0.7 | Minimum similarity score |
| `max_results` | int | 10 | Maximum results to return |

#### Key Methods

##### `initialize_database(force_recreate: bool = False) -> bool`
Initialize the vector database.

##### `add_profile_data(profile_data: Dict[str, Any]) -> bool`
Add applicant profile to the database.

##### `retrieve_relevant_profile(job_data: Dict[str, Any]) -> Dict[str, Any]`
Retrieve relevant profile information based on job description.

##### `save_database() -> bool`
Save database state to disk.

##### `get_database_stats() -> Dict[str, Any]`
Get database statistics and information.

## Input/Output Formats

### Profile Data Input Format

```python
{
    "profile_id": "unique_identifier",
    "name": "Full Name",
    "skills": ["Python", "JavaScript", "React"],
    "experience": [
        {
            "title": "Job Title",
            "company": "Company Name",
            "duration": "2020-2023",
            "description": "Job description and achievements"
        }
    ],
    "projects": [
        {
            "name": "Project Name",
            "description": "Project description",
            "technologies": "Tech stack used"
        }
    ],
    "education": [
        {
            "degree": "Degree Type",
            "field": "Field of Study",
            "institution": "University Name",
            "year": "2020"
        }
    ]
}
```

### Job Data Input Format

```python
{
    "job_title": "Job Title",
    "skills": ["Required", "Skills", "List"],
    "requirements": ["Requirement 1", "Requirement 2"],
    "responsibilities": ["Responsibility 1", "Responsibility 2"]
}
```

### Output Format

```python
{
    "profile_id": "matched_profile_id",
    "relevant_skills": ["Matching", "Skills"],
    "relevant_experience": [
        {
            "title": "Relevant Job",
            "company": "Company",
            "description": "Description"
        }
    ],
    "relevant_projects": [
        {
            "name": "Relevant Project",
            "description": "Description",
            "technologies": "Tech stack"
        }
    ],
    "relevant_education": [...],
    "similarity_scores": [0.85, 0.72, 0.68],
    "query_text": "Generated query text",
    "total_matches": 3,
    "retrieved_at": "2024-10-02T10:30:00"
}
```

## Integration with Other Agents

### With JDExtractorAgent

```python
from agents.jd_extractor_agent import JDExtractorAgent
from agents.profile_rag_agent import ProfileRAGAgent

# Extract job description
jd_agent = JDExtractorAgent()
job_data = jd_agent.extract_job_data("https://example.com/job")

# Retrieve relevant profile
rag_agent = ProfileRAGAgent()
rag_agent.initialize_database()
relevant_profile = rag_agent.retrieve_relevant_profile(job_data)
```

### With ResumePlannerAgent

```python
from agents.resume_planner_agent import ResumePlannerAgent
from agents.profile_rag_agent import ProfileRAGAgent

# Plan workflow
planner = ResumePlannerAgent()
workflow_plan = planner.generate_workflow_plan(job_url, profile_id)

# Execute ProfileRAG step
rag_agent = ProfileRAGAgent()
rag_agent.initialize_database()
relevant_profile = rag_agent.retrieve_relevant_profile(job_data)

# Pass to next agent in workflow
next_step_input = {
    "job_data": job_data,
    "profile_data": relevant_profile
}
```

## Performance Considerations

### Database Choice

- **FAISS**: Better for large datasets (10K+ profiles), faster search
- **Chroma**: Better for smaller datasets, easier setup, built-in persistence

### Optimization Tips

1. **Batch Processing**: Add multiple profiles before saving
2. **Similarity Threshold**: Adjust based on your quality requirements
3. **Model Selection**: Use larger models for better accuracy, smaller for speed
4. **Index Persistence**: Save/load indexes to avoid recomputation

### Memory Usage

- FAISS: ~4 bytes per dimension per vector + metadata
- Chroma: Varies based on configuration and data size
- Sentence Transformer: ~100MB for all-MiniLM-L6-v2 model

## Error Handling

The agent provides comprehensive error handling:

```python
try:
    agent = ProfileRAGAgent(db_type="faiss")
    agent.initialize_database()
    result = agent.retrieve_relevant_profile(job_data)
    
    if result["profile_id"] == "error":
        print(f"Error occurred: {result.get('error', 'Unknown error')}")
    elif result["profile_id"] == "no_matches":
        print("No matching profiles found")
    else:
        print(f"Found match: {result['profile_id']}")
        
except ValueError as e:
    if "dependencies not available" in str(e):
        print("Please install required dependencies")
    else:
        print(f"Configuration error: {e}")
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/test_profile_rag_agent.py -v

# Run specific test
python -m pytest tests/test_profile_rag_agent.py::TestProfileRAGAgent::test_retrieve_relevant_profile_faiss -v

# Run with coverage
python -m pytest tests/test_profile_rag_agent.py --cov=src.agents.profile_rag_agent
```

## Examples

See the following example files:
- `examples/profile_rag_integration_demo.py` - Complete integration demonstration
- `src/agents/profile_rag_agent.py` - Main implementation with test block
- `tests/test_profile_rag_agent.py` - Comprehensive test suite

## Next Steps

1. **ContentAlignmentAgent**: Use ProfileRAGAgent output to align resume content
2. **ATSOptimizerAgent**: Optimize the aligned content for ATS systems
3. **LaTeXFormatterAgent**: Generate final resume in LaTeX format
4. **End-to-End Pipeline**: Integrate all agents with ResumePlannerAgent

## Support

For issues or questions:
1. Check the test files for usage examples
2. Review error messages and logs
3. Ensure all dependencies are installed correctly
4. Verify input data formats match the specifications

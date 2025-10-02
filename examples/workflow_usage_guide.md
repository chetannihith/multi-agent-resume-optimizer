# ResumeWorkflow (LangGraph) Usage Guide

## Overview

The `ResumeWorkflow` class provides a comprehensive orchestration system for the Multi-Agent Resume Optimizer using [LangGraph](https://langchain-ai.github.io/langgraph/guides/) for workflow management and state coordination. This system coordinates five specialized agents to transform job descriptions and applicant profiles into optimized, ATS-friendly LaTeX resumes.

## Architecture

### LangGraph Integration

The workflow leverages LangGraph's powerful features:
- **State Management**: Shared state between all agents via `WorkflowState`
- **Graph Orchestration**: Sequential execution with proper dependencies
- **Error Handling**: Graceful error recovery and logging
- **Monitoring**: Comprehensive execution tracking and timing

### Agent Pipeline

```
JDExtractorAgent → ProfileRAGAgent → ContentAlignmentAgent → ATSOptimizerAgent → LaTeXFormatterAgent
```

1. **JDExtractorAgent**: Extracts and parses job description from URL
2. **ProfileRAGAgent**: Retrieves relevant applicant data from vector database
3. **ContentAlignmentAgent**: Aligns content with job requirements
4. **ATSOptimizerAgent**: Optimizes for ATS compatibility (90%+ score target)
5. **LaTeXFormatterAgent**: Generates Overleaf-ready LaTeX resume

## Installation & Setup

### Prerequisites

```bash
# Install required packages
pip install langgraph langchain langchain-core
pip install -r requirements.txt
```

### Directory Structure

```
project/
├── src/workflow/
│   ├── __init__.py
│   └── resume_workflow.py
├── templates/
│   └── resume_template.tex
├── output/                    # Generated LaTeX files
├── data/profiles/            # RAG database
├── logs/                     # Workflow execution logs
└── examples/
    ├── workflow_demo.py
    └── workflow_usage_guide.md
```

## Basic Usage

### 1. Initialize Workflow

```python
from src.workflow.resume_workflow import ResumeWorkflow

# Basic initialization
workflow = ResumeWorkflow()

# Custom configuration
workflow = ResumeWorkflow(
    template_path="custom_templates/my_template.tex",
    output_directory="custom_output",
    rag_database_path="data/my_profiles",
    enable_logging=True,
    log_level="INFO"
)
```

### 2. Execute Complete Pipeline

```python
# Run the full workflow
result = workflow.run_workflow(
    job_url="https://company.com/job-posting",
    profile_id="applicant_123",
    return_intermediate_results=True  # Optional: include step-by-step data
)

# Check results
if result['success']:
    print(f"✓ Success! LaTeX file: {result['latex_file_path']}")
    print("Upload to Overleaf for PDF generation")
else:
    print(f"✗ Errors occurred: {result['errors']}")
```

### 3. Workflow Status and Monitoring

```python
# Get workflow configuration
status = workflow.get_workflow_status()
print(f"Workflow: {status['workflow_name']} v{status['version']}")
print(f"Agents: {list(status['agents'].keys())}")
print(f"Steps: {status['workflow_steps']}")
```

## Advanced Features

### State Management

The workflow uses a shared `WorkflowState` that passes data between agents:

```python
class WorkflowState(TypedDict):
    # Input parameters
    job_url: str
    profile_id: str
    
    # Agent outputs
    job_data: Optional[Dict[str, Any]]
    profile_data: Optional[Dict[str, Any]]
    aligned_data: Optional[Dict[str, Any]]
    optimized_data: Optional[Dict[str, Any]]
    latex_file_path: Optional[str]
    
    # Workflow metadata
    current_step: str
    step_count: int
    errors: list
    warnings: list
    execution_time: Dict[str, float]
```

### Comprehensive Logging

The workflow provides detailed logging at multiple levels:

```python
# Enable detailed logging
workflow = ResumeWorkflow(
    enable_logging=True,
    log_level="DEBUG"  # DEBUG, INFO, WARNING, ERROR
)

# Logs are saved to: logs/resume_workflow_YYYYMMDD_HHMMSS.log
```

### Error Handling and Recovery

```python
result = workflow.run_workflow(job_url, profile_id)

# Detailed error information
if not result['success']:
    print("Workflow Errors:")
    for error in result['errors']:
        print(f"  - {error}")
    
    print("Warnings:")
    for warning in result['warnings']:
        print(f"  - {warning}")
    
    # Check which step failed
    metadata = result['workflow_metadata']
    print(f"Completed {metadata['completed_steps']}/{metadata['total_steps']} steps")
```

### Intermediate Results Access

```python
# Get step-by-step results
result = workflow.run_workflow(
    job_url, 
    profile_id, 
    return_intermediate_results=True
)

if result['success']:
    intermediate = result['intermediate_results']
    
    # Access individual agent outputs
    job_data = intermediate['job_data']
    profile_data = intermediate['profile_data']
    aligned_data = intermediate['aligned_data']
    optimized_data = intermediate['optimized_data']
    
    # Analyze results
    ats_score = optimized_data['ats_analysis']['ats_score']
    print(f"ATS Score: {ats_score}/100")
```

## Workflow Configuration

### Custom Templates

```python
# Use custom LaTeX template
workflow = ResumeWorkflow(
    template_path="templates/academic_resume.tex"
)

# Template should include LangGraph-compatible placeholders:
# {{{FIRST_NAME}}}, {{{LAST_NAME}}}, etc.
```

### RAG Database Configuration

```python
# Configure RAG database location
workflow = ResumeWorkflow(
    rag_database_path="data/company_profiles"
)

# The ProfileRAGAgent will use this path for:
# - FAISS index files
# - Chroma database
# - Profile JSON data
```

### Output Management

```python
# Custom output directory
workflow = ResumeWorkflow(
    output_directory="resumes/generated"
)

# Files are automatically named: {profile_id}_{job_title}_{timestamp}.tex
```

## Integration Examples

### Batch Processing

```python
def process_multiple_applications():
    workflow = ResumeWorkflow()
    
    applications = [
        ("https://company1.com/job1", "user_123"),
        ("https://company2.com/job2", "user_123"),
        ("https://company3.com/job3", "user_456"),
    ]
    
    results = []
    for job_url, profile_id in applications:
        print(f"Processing: {job_url}")
        result = workflow.run_workflow(job_url, profile_id)
        results.append(result)
        
        if result['success']:
            print(f"  ✓ Generated: {result['latex_file_path']}")
        else:
            print(f"  ✗ Failed: {result['errors'][0]}")
    
    return results
```

### Custom Agent Configuration

```python
# Initialize with custom agent settings
workflow = ResumeWorkflow()

# Access individual agents for configuration
workflow.rag_agent.similarity_threshold = 0.8
workflow.ats_agent.target_score = 95
workflow.latex_agent.template_style = "modern"
```

### API Integration

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
workflow = ResumeWorkflow()

@app.route('/optimize-resume', methods=['POST'])
def optimize_resume():
    data = request.json
    job_url = data['job_url']
    profile_id = data['profile_id']
    
    result = workflow.run_workflow(job_url, profile_id)
    
    return jsonify({
        'success': result['success'],
        'latex_file_path': result['latex_file_path'],
        'ats_score': result.get('optimized_data', {}).get('ats_analysis', {}).get('ats_score'),
        'execution_time': result['execution_time']['total'],
        'errors': result['errors']
    })
```

## Performance Optimization

### Execution Timing

```python
result = workflow.run_workflow(job_url, profile_id)

# Analyze performance
timing = result['execution_time']
print(f"Total Time: {timing['total']:.2f}s")
print("Step Breakdown:")
for step, time_taken in timing.items():
    if step != 'total':
        print(f"  {step}: {time_taken:.2f}s")
```

### Memory Management

```python
# For large-scale processing, reinitialize periodically
workflow = ResumeWorkflow()

for i, (job_url, profile_id) in enumerate(applications):
    result = workflow.run_workflow(job_url, profile_id)
    
    # Reinitialize every 100 resumes to free memory
    if i % 100 == 0:
        workflow = ResumeWorkflow()
```

## Error Handling Patterns

### Common Issues and Solutions

1. **Network Timeouts**
```python
result = workflow.run_workflow(job_url, profile_id)
if not result['success'] and 'timeout' in str(result['errors']):
    print("Network timeout - retry with different URL or check connectivity")
```

2. **Missing Profile Data**
```python
if 'No profile data found' in str(result['errors']):
    print("Profile not in RAG database - add profile data first")
```

3. **Template Issues**
```python
if 'Template file not found' in str(result['errors']):
    print("Check template path and ensure file exists")
```

### Graceful Degradation

```python
def robust_workflow_execution(job_url, profile_id, max_retries=3):
    workflow = ResumeWorkflow()
    
    for attempt in range(max_retries):
        try:
            result = workflow.run_workflow(job_url, profile_id)
            if result['success']:
                return result
            else:
                print(f"Attempt {attempt + 1} failed: {result['errors'][0]}")
        except Exception as e:
            print(f"Attempt {attempt + 1} exception: {e}")
        
        if attempt < max_retries - 1:
            print("Retrying...")
    
    return {"success": False, "errors": ["All retry attempts failed"]}
```

## Testing and Validation

### Unit Testing

```python
import pytest
from unittest.mock import patch, MagicMock

def test_workflow_with_mocked_agents():
    with patch('src.workflow.resume_workflow.JDExtractorAgent') as mock_jd:
        mock_jd.return_value.extract_job_data.return_value = {"job_title": "Test"}
        
        workflow = ResumeWorkflow(enable_logging=False)
        # Test workflow logic...
```

### Integration Testing

```python
def test_full_pipeline():
    workflow = ResumeWorkflow()
    
    # Use test data
    test_job_url = "https://example.com/test-job"
    test_profile_id = "test_user"
    
    result = workflow.run_workflow(test_job_url, test_profile_id)
    
    # Validate results
    assert 'execution_time' in result
    assert 'workflow_metadata' in result
```

## Best Practices

### 1. Input Validation
```python
def validate_inputs(job_url, profile_id):
    if not job_url.startswith(('http://', 'https://')):
        raise ValueError("Invalid job URL format")
    
    if not profile_id or len(profile_id) < 3:
        raise ValueError("Invalid profile ID")

# Use before workflow execution
validate_inputs(job_url, profile_id)
result = workflow.run_workflow(job_url, profile_id)
```

### 2. Resource Management
```python
# Use context manager for resource cleanup
class WorkflowManager:
    def __enter__(self):
        self.workflow = ResumeWorkflow()
        return self.workflow
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup resources if needed
        pass

# Usage
with WorkflowManager() as workflow:
    result = workflow.run_workflow(job_url, profile_id)
```

### 3. Configuration Management
```python
import json

# Load configuration from file
with open('workflow_config.json', 'r') as f:
    config = json.load(f)

workflow = ResumeWorkflow(
    template_path=config['template_path'],
    output_directory=config['output_directory'],
    rag_database_path=config['rag_database_path'],
    enable_logging=config['enable_logging'],
    log_level=config['log_level']
)
```

## Troubleshooting

### Debug Mode
```python
# Enable debug logging for detailed information
workflow = ResumeWorkflow(
    enable_logging=True,
    log_level="DEBUG"
)

# Check log file for detailed execution trace
# Location: logs/resume_workflow_YYYYMMDD_HHMMSS.log
```

### Common Issues

1. **LangGraph Import Error**
   - Install: `pip install langgraph langchain langchain-core`

2. **Agent Method Not Found**
   - Check agent method names match workflow calls
   - Verify agent imports are correct

3. **Template Processing Error**
   - Ensure template uses correct placeholder format
   - Check template file encoding (UTF-8)

4. **State Management Issues**
   - Verify WorkflowState TypedDict structure
   - Check state passing between nodes

## API Reference

### ResumeWorkflow Class

#### Constructor
```python
ResumeWorkflow(
    template_path: str = "templates/resume_template.tex",
    output_directory: str = "output",
    rag_database_path: str = "./data/profiles",
    enable_logging: bool = True,
    log_level: str = "INFO"
)
```

#### Methods

- `run_workflow(job_url, profile_id, return_intermediate_results=False)` → `Dict[str, Any]`
- `get_workflow_status()` → `Dict[str, Any]`

#### Workflow State Schema

```python
WorkflowState = TypedDict('WorkflowState', {
    'job_url': str,
    'profile_id': str,
    'job_data': Optional[Dict[str, Any]],
    'profile_data': Optional[Dict[str, Any]],
    'aligned_data': Optional[Dict[str, Any]],
    'optimized_data': Optional[Dict[str, Any]],
    'latex_file_path': Optional[str],
    'current_step': str,
    'step_count': int,
    'errors': list,
    'warnings': list,
    'execution_time': Dict[str, float],
    'messages': Annotated[list[BaseMessage], add_messages]
})
```

## Examples

See the following example files:
- `examples/workflow_demo.py` - Basic workflow demonstration
- `tests/test_workflow.py` - Comprehensive unit and integration tests
- `src/workflow/resume_workflow.py` - Full implementation with examples

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review workflow logs in the `logs/` directory
3. Run the demo script to verify setup
4. Check LangGraph documentation for advanced features

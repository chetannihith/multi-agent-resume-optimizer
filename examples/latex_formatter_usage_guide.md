# LaTeXFormatterAgent Usage Guide

## Overview

The `LaTeXFormatterAgent` is the final agent in the Multi-Agent Resume Optimizer pipeline. It takes optimized resume JSON data and generates professional LaTeX documents that are fully compatible with Overleaf for easy online editing and PDF compilation.

## Key Features

- **Overleaf Compatible**: Uses only packages supported by Overleaf
- **ATS-Friendly**: Generates clean, parseable LaTeX without graphics or complex formatting
- **Professional Templates**: Uses ModernCV package for professional resume layouts
- **Special Character Handling**: Properly escapes LaTeX special characters
- **Flexible Sections**: Handles optional sections (projects, certifications, etc.)
- **Multiple Formats**: Supports different resume styles and layouts

## Installation & Setup

### Prerequisites

```bash
# Install required packages
pip install -r requirements.txt
```

### Directory Structure

```
project/
├── templates/
│   └── resume_template.tex    # LaTeX template file
├── output/                    # Generated LaTeX files
├── src/agents/
│   └── latex_formatter_agent.py
└── examples/
    ├── latex_formatter_integration_demo.py
    └── latex_formatter_usage_guide.md
```

## Basic Usage

### 1. Initialize the Agent

```python
from src.agents.latex_formatter_agent import LaTeXFormatterAgent

# Initialize with default settings
agent = LaTeXFormatterAgent()

# Or customize paths
agent = LaTeXFormatterAgent(
    template_path="custom_templates/my_template.tex",
    output_directory="custom_output",
    default_template_style="modern"
)
```

### 2. Prepare Resume Data

The agent expects optimized resume data from the `ATSOptimizerAgent`:

```python
optimized_resume = {
    "profile_id": "john_doe_2024",
    "job_title": "Software Engineer",
    "name": "John Doe",
    "ats_analysis": {
        "ats_score": 92,
        "category": "Excellent"
    },
    "aligned_sections": {
        "summary": "Experienced software engineer...",
        "skills": {
            "aligned_skills": ["Python", "JavaScript", "React"],
            "skill_categories": {
                "programming": ["Python", "JavaScript"],
                "frameworks": ["React", "Django"]
            }
        },
        "experience": [...],
        "education": [...]
    },
    "relevant_projects": [...]
}
```

### 3. Generate LaTeX Resume

```python
# Generate with automatic filename
output_path = agent.generate_latex_resume(optimized_resume)

# Or specify custom filename
output_path = agent.generate_latex_resume(
    optimized_resume, 
    "john_doe_software_engineer.tex"
)

print(f"Generated: {output_path}")
```

## Advanced Features

### Custom Template Creation

Create your own LaTeX template with placeholders:

```latex
\documentclass[11pt,a4paper,sans]{moderncv}
\moderncvstyle{classic}
\moderncvcolor{blue}

% Personal information
\name{{{FIRST_NAME}}}{{{LAST_NAME}}}
\title{{{JOB_TITLE}}}

\begin{document}
\makecvtitle

% Professional Summary
\section{Professional Summary}
\cvitem{}{{{PROFESSIONAL_SUMMARY}}}

% Skills (repeatable section)
{{#SKILLS_CATEGORIES}}
\cvitem{{{CATEGORY_NAME}}}{{{SKILLS_LIST}}}
{{/SKILLS_CATEGORIES}}

% Experience (repeatable section)
{{#EXPERIENCE_ENTRIES}}
\cventry{{{START_DATE}}--{{END_DATE}}}{{{JOB_TITLE}}}{{{COMPANY_NAME}}}{{{LOCATION}}}{}{%
{{#JOB_DESCRIPTIONS}}
\begin{itemize}
{{#DESCRIPTION_ITEMS}}
\item {{DESCRIPTION_ITEM}}
{{/DESCRIPTION_ITEMS}}
\end{itemize}
{{/JOB_DESCRIPTIONS}}
}
{{/EXPERIENCE_ENTRIES}}

\end{document}
```

### Special Character Handling

The agent automatically escapes LaTeX special characters:

```python
# Input text with special characters
text = "Improved performance by 50% & reduced costs by $10,000"

# Automatically escaped in LaTeX output
escaped = agent.escape_latex_special_chars(text)
# Result: "Improved performance by 50\\% \\& reduced costs by \\$10,000"
```

### Overleaf Compatibility Validation

```python
# Validate generated content
with open(output_path, 'r', encoding='utf-8') as f:
    latex_content = f.read()

validation = agent.validate_overleaf_compatibility(latex_content)

print(f"Compatible: {validation['is_compatible']}")
if validation['warnings']:
    print("Warnings:", validation['warnings'])
```

## Template Placeholders

### Personal Information
- `{{{FIRST_NAME}}}` - First name
- `{{{LAST_NAME}}}` - Last name  
- `{{{JOB_TITLE}}}` - Target job title
- `{{{EMAIL_ADDRESS}}}` - Email address
- `{{{PHONE_NUMBER}}}` - Phone number
- `{{{LINKEDIN_USERNAME}}}` - LinkedIn profile
- `{{{GITHUB_USERNAME}}}` - GitHub profile

### Content Sections
- `{{{PROFESSIONAL_SUMMARY}}}` - Professional summary text

### Repeatable Sections

#### Skills Categories
```latex
{{#SKILLS_CATEGORIES}}
\cvitem{{{CATEGORY_NAME}}}{{{SKILLS_LIST}}}
{{/SKILLS_CATEGORIES}}
```

#### Experience Entries
```latex
{{#EXPERIENCE_ENTRIES}}
\cventry{{{START_DATE}}--{{END_DATE}}}{{{JOB_TITLE}}}{{{COMPANY_NAME}}}{{{LOCATION}}}{}{%
{{#JOB_DESCRIPTIONS}}
\begin{itemize}
{{#DESCRIPTION_ITEMS}}
\item {{DESCRIPTION_ITEM}}
{{/DESCRIPTION_ITEMS}}
\end{itemize}
{{/JOB_DESCRIPTIONS}}
}
{{/EXPERIENCE_ENTRIES}}
```

#### Education Entries
```latex
{{#EDUCATION_ENTRIES}}
\cventry{{{GRADUATION_YEAR}}}{{{DEGREE_TYPE}}}{{{INSTITUTION_NAME}}}{{{LOCATION}}}{{{GPA_INFO}}}{{{ADDITIONAL_INFO}}}
{{/EDUCATION_ENTRIES}}
```

#### Projects (Optional)
```latex
{{#HAS_PROJECTS}}
\section{Key Projects}
{{#PROJECT_ENTRIES}}
\cventry{{{PROJECT_DATE}}}{{{PROJECT_NAME}}}{{{PROJECT_ORGANIZATION}}}{}{}{%
{{PROJECT_DESCRIPTION}}
{{#PROJECT_TECHNOLOGIES}}
\newline\textbf{Technologies:} {{TECHNOLOGIES_LIST}}
{{/PROJECT_TECHNOLOGIES}}
}
{{/PROJECT_ENTRIES}}
{{/HAS_PROJECTS}}
```

## Overleaf Integration

### Step-by-Step Upload Process

1. **Generate LaTeX File**
   ```python
   output_path = agent.generate_latex_resume(optimized_resume)
   ```

2. **Go to Overleaf**
   - Visit https://www.overleaf.com
   - Sign in or create free account

3. **Create New Project**
   - Click "New Project" → "Upload Project"
   - Upload your `.tex` file

4. **Compile PDF**
   - Click "Recompile" button
   - Download PDF when ready

5. **Edit Online** (Optional)
   - Modify content directly in Overleaf
   - Real-time preview available
   - Collaborative editing supported

### Supported Overleaf Packages

The template uses only packages supported by Overleaf:

- `moderncv` - Professional CV template
- `geometry` - Page layout control
- `inputenc` - UTF-8 character encoding
- Standard LaTeX packages

### Overleaf Tips

- **Font Selection**: ModernCV supports multiple fonts
- **Color Themes**: Blue, orange, green, red, purple, grey
- **Styles**: Classic, casual, oldstyle, banking
- **Photo Support**: Optional photo inclusion
- **Multi-page**: Automatic page breaks

## Error Handling

### Common Issues & Solutions

1. **Template Not Found**
   ```python
   # Error: FileNotFoundError
   # Solution: Check template path
   agent = LaTeXFormatterAgent(template_path="correct/path/template.tex")
   ```

2. **Special Characters**
   ```python
   # Error: LaTeX compilation errors
   # Solution: Characters are auto-escaped, but check for unusual symbols
   ```

3. **Missing Sections**
   ```python
   # Error: Empty sections in output
   # Solution: Ensure resume data has required fields
   if not resume_data.get('aligned_sections', {}).get('experience'):
       print("Warning: No experience data found")
   ```

4. **Overleaf Compatibility**
   ```python
   # Check compatibility before upload
   validation = agent.validate_overleaf_compatibility(latex_content)
   if not validation['is_compatible']:
       print("Compatibility issues:", validation['errors'])
   ```

## Integration with Other Agents

### Complete Pipeline Example

```python
from src.agents.jd_extractor_agent import JDExtractorAgent
from src.agents.profile_rag_agent import ProfileRAGAgent
from src.agents.content_alignment_agent import ContentAlignmentAgent
from src.agents.ats_optimizer_agent import ATSOptimizerAgent
from src.agents.latex_formatter_agent import LaTeXFormatterAgent

# Initialize agents
jd_agent = JDExtractorAgent()
rag_agent = ProfileRAGAgent()
alignment_agent = ContentAlignmentAgent()
ats_agent = ATSOptimizerAgent()
latex_agent = LaTeXFormatterAgent()

# Process pipeline
job_data = jd_agent.extract_job_data(job_url)
profile_data = rag_agent.retrieve_profile(job_data, profile_id)
aligned_data = alignment_agent.align_content(job_data, profile_data)
optimized_data = ats_agent.optimize_resume(aligned_data)
latex_file = latex_agent.generate_latex_resume(optimized_data)

print(f"Final resume: {latex_file}")
```

## Best Practices

### 1. Data Validation
```python
# Validate input data before processing
required_fields = ['profile_id', 'name', 'job_title', 'aligned_sections']
for field in required_fields:
    if field not in resume_data:
        raise ValueError(f"Missing required field: {field}")
```

### 2. File Management
```python
# Organize output files by date/user
from datetime import datetime

timestamp = datetime.now().strftime('%Y%m%d')
filename = f"{profile_id}_{timestamp}_resume.tex"
```

### 3. Template Customization
```python
# Create role-specific templates
templates = {
    'software_engineer': 'templates/tech_resume.tex',
    'data_scientist': 'templates/data_resume.tex',
    'product_manager': 'templates/pm_resume.tex'
}

template_path = templates.get(job_category, 'templates/default.tex')
agent = LaTeXFormatterAgent(template_path=template_path)
```

### 4. Quality Assurance
```python
# Always validate output
output_path = agent.generate_latex_resume(resume_data)

# Check file size (should be reasonable)
file_size = os.path.getsize(output_path)
if file_size < 1000:  # Less than 1KB might indicate issues
    print("Warning: Generated file seems too small")

# Validate Overleaf compatibility
with open(output_path, 'r', encoding='utf-8') as f:
    content = f.read()
    
validation = agent.validate_overleaf_compatibility(content)
if validation['warnings']:
    print("Compatibility warnings:", validation['warnings'])
```

## Performance Considerations

- **Template Caching**: Templates are loaded once per agent instance
- **File I/O**: Output files are written directly to disk
- **Memory Usage**: Large resume datasets are processed in chunks
- **Concurrent Processing**: Multiple resumes can be generated in parallel

## Troubleshooting

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

agent = LaTeXFormatterAgent()
# Detailed logging will be shown
```

### Common LaTeX Errors
1. **Undefined control sequence**: Check template syntax
2. **Missing packages**: Ensure Overleaf compatibility
3. **Encoding issues**: Use UTF-8 encoding consistently
4. **Special characters**: Verify proper escaping

### Testing
```python
# Run unit tests
python -m pytest tests/test_latex_formatter_agent.py -v

# Run integration demo
python examples/latex_formatter_integration_demo.py
```

## API Reference

### LaTeXFormatterAgent Class

#### Constructor
```python
LaTeXFormatterAgent(
    template_path: str = "templates/resume_template.tex",
    output_directory: str = "output", 
    default_template_style: str = "professional"
)
```

#### Methods

- `generate_latex_resume(optimized_resume, output_filename=None)` → `str`
- `populate_template(template_content, resume_data)` → `str`
- `escape_latex_special_chars(text)` → `str`
- `validate_overleaf_compatibility(latex_content)` → `Dict[str, Any]`
- `format_skills_by_category(skills_data)` → `List[Dict[str, str]]`
- `format_experience_entries(experience_data)` → `List[Dict[str, Any]]`
- `format_education_entries(education_data)` → `List[Dict[str, str]]`

## Examples

See the following example files:
- `examples/latex_formatter_integration_demo.py` - Complete integration demo
- `tests/test_latex_formatter_agent.py` - Unit tests with examples
- `templates/resume_template.tex` - Default template

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review unit tests for usage examples  
3. Run the integration demo to verify setup
4. Check Overleaf documentation for LaTeX-specific issues

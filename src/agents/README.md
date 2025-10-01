# JDExtractorAgent

The JDExtractorAgent is a Python class that extracts structured job description data from web URLs using web scraping techniques.

## Features

- **URL Validation**: Validates input URLs before processing
- **Web Scraping**: Fetches HTML content from job posting URLs
- **Text Extraction**: Extracts clean text from HTML content
- **Structured Data Extraction**: Extracts:
  - Job title (from H1 tags or title tags)
  - Required skills (from structured lists)
  - Job responsibilities (from structured lists)
  - Job requirements (from structured lists)
- **JSON Output**: Returns structured data in JSON format
- **Error Handling**: Graceful error handling for network issues

## Usage

### Basic Usage

```python
from src.agents.jd_extractor_agent import JDExtractorAgent

# Initialize the agent
agent = JDExtractorAgent()

# Extract job data from URL
job_data = agent.extract_job_data("https://example.com/job-posting")

# Convert to JSON
json_output = agent.to_json(job_data)
print(json_output)
```

### Testing with Local Files

```python
# For testing with local HTML files
with open("sample_job.html", "r") as f:
    html_content = f.read()

agent = JDExtractorAgent()
job_title = agent.extract_job_title(html_content)
skills = agent.extract_skills(html_content)
responsibilities = agent.extract_responsibilities(html_content)
requirements = agent.extract_requirements(html_content)
```

## Output Format

The agent returns a dictionary with the following structure:

```json
{
  "job_title": "Software Engineer - AI/ML Team",
  "skills": [
    "Python programming (3+ years experience)",
    "FastAPI framework",
    "RAG implementation"
  ],
  "responsibilities": [
    "Develop AI workflows using Python and FastAPI",
    "Integrate APIs and build scalable microservices"
  ],
  "requirements": [
    "Bachelor's degree in Computer Science or related field",
    "3+ years of Python development experience"
  ],
  "url": "https://example.com/job-posting",
  "raw_text_length": 1187
}
```

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
- lxml

## Installation

```bash
pip install -r requirements.txt
```

## Testing

Run the test script to see the agent in action:

```bash
python examples/test_jd_extractor.py
```

## Notes

- The agent works best with well-structured HTML job postings
- It prioritizes HTML structure over text patterns for extraction
- Network requests have a 30-second timeout by default
- The agent includes a realistic user agent string to avoid blocking

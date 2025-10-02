# ContentAlignmentAgent Usage Guide

## Overview

The `ContentAlignmentAgent` is a crucial component of the Multi-Agent Resume Optimizer that rewrites applicant information to match job description keywords. It processes job data and applicant profiles to create aligned resume content that emphasizes relevant skills and experiences.

## Features

### 🔍 **Keyword Matching Engine**
- **Smart Extraction**: Extracts keywords from job titles, skills, requirements, and responsibilities
- **Stop Word Filtering**: Excludes common words to focus on meaningful terms
- **Categorized Analysis**: Organizes keywords by job section for targeted alignment
- **Similarity Scoring**: Calculates alignment scores between applicant content and job requirements

### 📝 **Content Rewriting**
- **Experience Highlighting**: Prioritizes experiences that match job requirements
- **Skills Alignment**: Reorders and categorizes skills based on job relevance
- **Summary Generation**: Creates professional summaries aligned with job descriptions
- **Sentence Rephrasing**: Enhances descriptions to emphasize alignment (basic implementation)

### 📊 **Intelligent Analysis**
- **Alignment Scoring**: Provides quantitative measures of content alignment
- **Recommendation Engine**: Suggests improvements for better job matching
- **Priority Ranking**: Orders content by relevance to job requirements
- **Category Organization**: Groups skills into technical, soft, tools, and other categories

## Quick Start

### Basic Usage

```python
from agents.content_alignment_agent import ContentAlignmentAgent

# Initialize agent
agent = ContentAlignmentAgent(
    keyword_weight=1.0,
    experience_weight=1.5,
    skills_weight=1.2,
    min_keyword_length=3
)

# Job data (from JDExtractorAgent)
job_data = {
    "job_title": "Senior Python Developer",
    "skills": ["Python", "Django", "PostgreSQL", "AWS"],
    "requirements": ["5+ years Python experience", "Web framework knowledge"],
    "responsibilities": ["Develop web applications", "Design REST APIs"]
}

# Profile data (from ProfileRAGAgent)
profile_data = {
    "profile_id": "john_doe_2024",
    "relevant_skills": ["Python", "Django", "JavaScript", "PostgreSQL"],
    "relevant_experience": [
        {
            "title": "Python Developer",
            "company": "TechCorp",
            "description": "Built web applications using Python and Django"
        }
    ]
}

# Align content
aligned_content = agent.align_content(job_data, profile_data)

# Access results
print(f"Alignment Score: {aligned_content['alignment_metadata']['overall_alignment_score']:.3f}")
print(f"Aligned Summary: {aligned_content['aligned_sections']['summary']}")
print(f"Top Skills: {aligned_content['aligned_sections']['skills']['aligned_skills'][:5]}")
```

## API Reference

### ContentAlignmentAgent Class

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword_weight` | float | 1.0 | Base weight for keyword matching |
| `experience_weight` | float | 1.5 | Weight multiplier for experience matches |
| `skills_weight` | float | 1.2 | Weight multiplier for skills matches |
| `min_keyword_length` | int | 3 | Minimum length for keywords to consider |

#### Key Methods

##### `extract_keywords(text: str) -> Set[str]`
Extract keywords from text, excluding stop words and short terms.

##### `extract_job_keywords(job_data: Dict[str, Any]) -> Dict[str, Set[str]]`
Extract keywords from different sections of job description.

##### `calculate_alignment_score(text: str, job_keywords: Set[str]) -> float`
Calculate alignment score between text and job keywords (0.0 to 1.0).

##### `align_content(job_data: Dict[str, Any], profile_data: Dict[str, Any]) -> Dict[str, Any]`
Main method that aligns applicant content with job requirements.

##### `highlight_matching_experiences(experiences: List[Dict], job_keywords: Dict) -> List[Dict]`
Highlight and prioritize experiences that match job requirements.

##### `align_skills_section(skills: List[str], job_keywords: Dict) -> Dict[str, Any]`
Align skills section with job requirements and categorize skills.

##### `generate_aligned_summary(profile_data: Dict, job_data: Dict, job_keywords: Dict) -> str`
Generate a professional summary aligned with job requirements.

## Input/Output Formats

### Job Data Input Format

```python
{
    "job_title": "Job Title",
    "skills": ["Required", "Skills", "List"],
    "requirements": ["Requirement 1", "Requirement 2"],
    "responsibilities": ["Responsibility 1", "Responsibility 2"]
}
```

### Profile Data Input Format

```python
{
    "profile_id": "unique_identifier",
    "relevant_skills": ["Skill 1", "Skill 2"],
    "relevant_experience": [
        {
            "title": "Job Title",
            "company": "Company Name",
            "description": "Job description"
        }
    ]
}
```

### Output Format

```python
{
    "profile_id": "profile_identifier",
    "job_title": "Job Title",
    "alignment_metadata": {
        "overall_alignment_score": 0.75,
        "skills_alignment_score": 0.80,
        "experience_alignment_score": 0.70,
        "job_keywords_count": 25,
        "matching_keywords": ["keyword1", "keyword2"],
        "processed_at": "2024-10-02T12:00:00"
    },
    "aligned_sections": {
        "summary": "Aligned professional summary...",
        "skills": {
            "aligned_skills": ["Skill 1", "Skill 2"],
            "matching_skills": ["Skill 1"],
            "skill_categories": {
                "technical": ["Python", "JavaScript"],
                "tools": ["Git", "Docker"],
                "soft": ["Leadership"],
                "other": ["Other Skills"]
            },
            "alignment_score": 0.80,
            "skill_scores": {"Skill 1": 0.9, "Skill 2": 0.7}
        },
        "experience": [
            {
                "title": "Job Title",
                "company": "Company",
                "description": "Original description",
                "aligned_description": "Enhanced description",
                "alignment_score": 0.85,
                "matching_keywords": ["keyword1", "keyword2"]
            }
        ],
        "job_keywords": {
            "title": ["job", "title", "keywords"],
            "skills": ["skill", "keywords"],
            "requirements": ["requirement", "keywords"],
            "responsibilities": ["responsibility", "keywords"],
            "all": ["all", "unique", "keywords"]
        }
    },
    "recommendations": [
        "Recommendation 1",
        "Recommendation 2"
    ]
}
```

## Algorithm Details

### Keyword Matching Algorithm

The core keyword matching algorithm works as follows:

1. **Keyword Extraction**:
   - Convert text to lowercase
   - Extract words using regex pattern `\b[a-zA-Z]+\b`
   - Filter out stop words and words shorter than `min_keyword_length`

2. **Alignment Score Calculation**:
   ```python
   alignment_score = len(matching_keywords) / len(job_keywords)
   ```

3. **Experience Prioritization**:
   - Calculate alignment for job title and description separately
   - Weight description more heavily: `(title_score + desc_score * 2) / 3`
   - Sort experiences by alignment score (highest first)

4. **Skills Categorization**:
   - **Technical**: Programming languages, frameworks, databases
   - **Tools**: Development tools, version control, project management
   - **Soft**: Leadership, communication, problem-solving
   - **Other**: Skills that don't fit other categories

### Alignment Scoring

- **Overall Alignment**: Weighted average of skills and experience alignment
- **Skills Alignment**: Average alignment score of all skills
- **Experience Alignment**: Average alignment score of all experiences
- **Scores Range**: 0.0 (no alignment) to 1.0 (perfect alignment)

### Content Enhancement

1. **Summary Generation**:
   - Incorporates years of experience (estimated)
   - Highlights top matching skills
   - Adds job-specific specialization statements
   - Includes achievement and collaboration statements

2. **Experience Enhancement**:
   - Identifies matching keywords in descriptions
   - Adds quantifiable achievements when missing
   - Emphasizes relevant technologies and methodologies

## Integration Examples

### With JDExtractorAgent and ProfileRAGAgent

```python
from agents.jd_extractor_agent import JDExtractorAgent
from agents.profile_rag_agent import ProfileRAGAgent
from agents.content_alignment_agent import ContentAlignmentAgent

# Step 1: Extract job description
jd_agent = JDExtractorAgent()
job_data = jd_agent.extract_job_data("https://example.com/job")

# Step 2: Retrieve relevant profile
rag_agent = ProfileRAGAgent()
rag_agent.initialize_database()
profile_data = rag_agent.retrieve_relevant_profile(job_data)

# Step 3: Align content
alignment_agent = ContentAlignmentAgent()
aligned_content = alignment_agent.align_content(job_data, profile_data)

# Step 4: Prepare for ATS optimization
ats_input = {
    "aligned_summary": aligned_content["aligned_sections"]["summary"],
    "prioritized_skills": aligned_content["aligned_sections"]["skills"]["aligned_skills"],
    "optimized_experiences": aligned_content["aligned_sections"]["experience"],
    "job_keywords": aligned_content["aligned_sections"]["job_keywords"]["all"]
}
```

### With ResumePlannerAgent Workflow

```python
from agents.resume_planner_agent import ResumePlannerAgent
from agents.content_alignment_agent import ContentAlignmentAgent

# Plan workflow
planner = ResumePlannerAgent()
workflow_plan = planner.generate_workflow_plan(job_url, profile_id)

# Execute content alignment step
alignment_agent = ContentAlignmentAgent()
aligned_content = alignment_agent.align_content(job_data, profile_data)

# Update workflow status
planner.update_step_status(3, "completed", {
    "alignment_score": aligned_content["alignment_metadata"]["overall_alignment_score"],
    "output_file": "aligned_resume.json"
})
```

## Performance Considerations

### Optimization Tips

1. **Keyword Filtering**: Adjust `min_keyword_length` based on your domain
2. **Weight Tuning**: Modify weights based on job type importance
3. **Batch Processing**: Process multiple profiles against the same job for efficiency
4. **Caching**: Cache job keyword extraction for repeated use

### Memory Usage

- Minimal memory footprint
- Keywords stored as sets for efficient intersection operations
- No external dependencies beyond standard library

### Processing Speed

- Fast keyword extraction using regex
- Efficient set operations for matching
- Linear time complexity for most operations
- Typical processing time: < 100ms per profile

## Testing

The agent includes comprehensive unit tests covering:

- Keyword extraction and filtering
- Alignment score calculation
- Experience highlighting and prioritization
- Skills categorization and alignment
- Summary generation
- Error handling
- Integration scenarios

Run tests with:
```bash
python -m pytest tests/test_content_alignment_agent.py -v
```

## Examples

See the following example files:
- `examples/content_alignment_integration_demo.py` - Complete integration demonstration
- `src/agents/content_alignment_agent.py` - Main implementation with test block
- `tests/test_content_alignment_agent.py` - Comprehensive test suite

## Limitations and Future Enhancements

### Current Limitations

1. **Simple Keyword Matching**: Uses basic string matching, not semantic similarity
2. **Basic Rephrasing**: Limited sentence enhancement capabilities
3. **Static Categories**: Fixed skill categorization rules
4. **No Context Awareness**: Doesn't understand job context or industry nuances

### Planned Enhancements

1. **Semantic Matching**: Integrate with sentence transformers for better alignment
2. **Advanced NLP**: Use language models for sophisticated rephrasing
3. **Dynamic Categories**: Learn skill categories from job descriptions
4. **Industry Adaptation**: Customize alignment strategies by industry
5. **A/B Testing**: Compare alignment strategies for effectiveness

## Support

For issues or questions:
1. Check the test files for usage examples
2. Review the integration demo for workflow patterns
3. Examine alignment scores and recommendations for insights
4. Verify input data formats match specifications

## Next Steps

1. **ATSOptimizerAgent**: Use ContentAlignmentAgent output for ATS optimization
2. **LaTeXFormatterAgent**: Format aligned content into professional resume
3. **End-to-End Pipeline**: Complete integration with all workflow agents
4. **Performance Tuning**: Optimize alignment algorithms for specific use cases

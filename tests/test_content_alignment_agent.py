"""
Tests for ContentAlignmentAgent.

This module contains unit tests for the ContentAlignmentAgent class,
testing keyword matching, content alignment, and rephrasing functionality.
"""

import pytest
from src.agents.content_alignment_agent import ContentAlignmentAgent


class TestContentAlignmentAgent:
    """Test cases for ContentAlignmentAgent."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.agent = ContentAlignmentAgent(
            keyword_weight=1.0,
            experience_weight=1.5,
            skills_weight=1.2,
            min_keyword_length=3
        )
        
        # Sample job data
        self.sample_job_data = {
            "job_title": "Senior Python Developer",
            "skills": ["Python", "Django", "PostgreSQL", "AWS", "Docker"],
            "requirements": [
                "5+ years Python experience",
                "Web framework knowledge",
                "Database experience"
            ],
            "responsibilities": [
                "Develop web applications",
                "Design REST APIs",
                "Collaborate with teams"
            ]
        }
        
        # Sample profile data
        self.sample_profile_data = {
            "profile_id": "test_user_123",
            "name": "Test User",
            "relevant_skills": ["Python", "Django", "JavaScript", "PostgreSQL", "Git"],
            "relevant_experience": [
                {
                    "title": "Python Developer",
                    "company": "TechCorp",
                    "duration": "2020-2023",
                    "description": "Developed web applications using Python and Django framework. Worked with PostgreSQL databases and REST APIs."
                },
                {
                    "title": "Software Engineer",
                    "company": "WebCorp",
                    "duration": "2018-2020",
                    "description": "Built frontend applications using JavaScript and React. Collaborated with backend teams on API integration."
                }
            ]
        }
    
    def test_initialization(self):
        """Test agent initialization."""
        assert self.agent.keyword_weight == 1.0
        assert self.agent.experience_weight == 1.5
        assert self.agent.skills_weight == 1.2
        assert self.agent.min_keyword_length == 3
        assert len(self.agent.stop_words) > 0
    
    def test_extract_keywords_basic(self):
        """Test basic keyword extraction."""
        text = "Python developer with Django experience"
        keywords = self.agent.extract_keywords(text)
        
        assert "python" in keywords
        assert "developer" in keywords
        assert "django" in keywords
        assert "experience" in keywords
        assert "with" not in keywords  # Stop word should be excluded
    
    def test_extract_keywords_empty_input(self):
        """Test keyword extraction with empty input."""
        assert self.agent.extract_keywords("") == set()
        assert self.agent.extract_keywords(None) == set()
    
    def test_extract_keywords_short_words(self):
        """Test that short words are excluded."""
        text = "I am a Python developer"
        keywords = self.agent.extract_keywords(text)
        
        assert "python" in keywords
        assert "developer" in keywords
        assert "am" not in keywords  # Too short
        assert "a" not in keywords   # Too short
    
    def test_extract_job_keywords(self):
        """Test job keyword extraction from different sections."""
        job_keywords = self.agent.extract_job_keywords(self.sample_job_data)
        
        assert "python" in job_keywords["title"]
        assert "senior" in job_keywords["title"]
        assert "developer" in job_keywords["title"]
        
        assert "python" in job_keywords["skills"]
        assert "django" in job_keywords["skills"]
        assert "postgresql" in job_keywords["skills"]
        
        assert "python" in job_keywords["requirements"]
        assert "experience" in job_keywords["requirements"]
        
        assert "develop" in job_keywords["responsibilities"]
        assert "design" in job_keywords["responsibilities"]
        
        # Check that all keywords are in the 'all' category
        assert "python" in job_keywords["all"]
        assert "django" in job_keywords["all"]
        assert len(job_keywords["all"]) > 0
    
    def test_extract_job_keywords_empty_data(self):
        """Test job keyword extraction with empty data."""
        empty_job = {}
        job_keywords = self.agent.extract_job_keywords(empty_job)
        
        for category in ["title", "skills", "requirements", "responsibilities", "all"]:
            assert job_keywords[category] == set()
    
    def test_calculate_alignment_score(self):
        """Test alignment score calculation."""
        job_keywords = {"python", "django", "web", "development"}
        
        # Perfect match
        text1 = "Python Django web development"
        score1 = self.agent.calculate_alignment_score(text1, job_keywords)
        assert score1 == 1.0
        
        # Partial match
        text2 = "Python web programming"
        score2 = self.agent.calculate_alignment_score(text2, job_keywords)
        assert 0.0 < score2 < 1.0
        
        # No match
        text3 = "Java Spring Boot application"
        score3 = self.agent.calculate_alignment_score(text3, job_keywords)
        assert score3 == 0.0
        
        # Empty inputs
        assert self.agent.calculate_alignment_score("", job_keywords) == 0.0
        assert self.agent.calculate_alignment_score(text1, set()) == 0.0
    
    def test_highlight_matching_experiences(self):
        """Test experience highlighting functionality."""
        job_keywords = self.agent.extract_job_keywords(self.sample_job_data)
        experiences = self.sample_profile_data["relevant_experience"]
        
        highlighted = self.agent.highlight_matching_experiences(experiences, job_keywords)
        
        assert len(highlighted) == len(experiences)
        
        # Check that alignment scores are added
        for exp in highlighted:
            assert "alignment_score" in exp
            assert "matching_keywords" in exp
            assert isinstance(exp["alignment_score"], float)
            assert isinstance(exp["matching_keywords"], list)
        
        # Check that experiences are sorted by alignment score
        scores = [exp["alignment_score"] for exp in highlighted]
        assert scores == sorted(scores, reverse=True)
        
        # First experience should have higher score (more Python/Django content)
        assert highlighted[0]["title"] == "Python Developer"
    
    def test_highlight_matching_experiences_empty_input(self):
        """Test experience highlighting with empty input."""
        job_keywords = {"all": set()}
        
        result = self.agent.highlight_matching_experiences([], job_keywords)
        assert result == []
        
        # Test with non-dict items
        invalid_experiences = ["not a dict", 123, None]
        result = self.agent.highlight_matching_experiences(invalid_experiences, job_keywords)
        assert result == []
    
    def test_rephrase_for_alignment(self):
        """Test text rephrasing for alignment."""
        original_text = "Worked on web development projects"
        job_keywords = {"python", "django", "web", "development"}
        matching_keywords = {"web", "development"}
        
        rephrased = self.agent.rephrase_for_alignment(
            original_text, job_keywords, matching_keywords
        )
        
        assert len(rephrased) >= len(original_text)
        assert "web" in rephrased.lower()
        assert "development" in rephrased.lower()
    
    def test_rephrase_for_alignment_empty_input(self):
        """Test rephrasing with empty input."""
        assert self.agent.rephrase_for_alignment("", set(), set()) == ""
        
        text = "Some text"
        assert self.agent.rephrase_for_alignment(text, set(), set()) == text
    
    def test_align_skills_section(self):
        """Test skills section alignment."""
        job_keywords = self.agent.extract_job_keywords(self.sample_job_data)
        skills = self.sample_profile_data["relevant_skills"]
        
        aligned_skills = self.agent.align_skills_section(skills, job_keywords)
        
        assert "aligned_skills" in aligned_skills
        assert "matching_skills" in aligned_skills
        assert "skill_categories" in aligned_skills
        assert "alignment_score" in aligned_skills
        assert "skill_scores" in aligned_skills
        
        # Check that Python and Django are in matching skills
        matching_skills = aligned_skills["matching_skills"]
        assert "Python" in matching_skills
        assert "Django" in matching_skills
        
        # Check alignment score is reasonable
        assert 0.0 <= aligned_skills["alignment_score"] <= 1.0
        
        # Check skill categories
        categories = aligned_skills["skill_categories"]
        assert "technical" in categories
        assert "soft" in categories
        assert "tools" in categories
        assert "other" in categories
    
    def test_align_skills_section_empty_input(self):
        """Test skills alignment with empty input."""
        job_keywords = {"all": set()}
        
        result = self.agent.align_skills_section([], job_keywords)
        
        assert result["aligned_skills"] == []
        assert result["matching_skills"] == []
        assert result["alignment_score"] == 0.0
    
    def test_generate_aligned_summary(self):
        """Test aligned summary generation."""
        job_keywords = self.agent.extract_job_keywords(self.sample_job_data)
        
        summary = self.agent.generate_aligned_summary(
            self.sample_profile_data, self.sample_job_data, job_keywords
        )
        
        assert isinstance(summary, str)
        assert len(summary) > 50  # Should be a substantial summary
        assert summary.endswith(".")  # Should end with period
        
        # Should contain some relevant terms
        summary_lower = summary.lower()
        assert "experience" in summary_lower or "professional" in summary_lower
    
    def test_generate_aligned_summary_minimal_data(self):
        """Test summary generation with minimal data."""
        minimal_profile = {"name": "Test User"}
        minimal_job = {"job_title": "Developer"}
        job_keywords = {"all": set()}
        
        summary = self.agent.generate_aligned_summary(
            minimal_profile, minimal_job, job_keywords
        )
        
        assert isinstance(summary, str)
        assert len(summary) > 0
    
    def test_align_content_complete(self):
        """Test complete content alignment process."""
        aligned_content = self.agent.align_content(
            self.sample_job_data, self.sample_profile_data
        )
        
        # Check main structure
        assert "profile_id" in aligned_content
        assert "job_title" in aligned_content
        assert "alignment_metadata" in aligned_content
        assert "aligned_sections" in aligned_content
        assert "recommendations" in aligned_content
        
        # Check metadata
        metadata = aligned_content["alignment_metadata"]
        assert "overall_alignment_score" in metadata
        assert "skills_alignment_score" in metadata
        assert "experience_alignment_score" in metadata
        assert "processed_at" in metadata
        
        # Check aligned sections
        sections = aligned_content["aligned_sections"]
        assert "summary" in sections
        assert "skills" in sections
        assert "experience" in sections
        assert "job_keywords" in sections
        
        # Check that summary is a string
        assert isinstance(sections["summary"], str)
        
        # Check that skills section has proper structure
        skills_data = sections["skills"]
        assert "aligned_skills" in skills_data
        assert "alignment_score" in skills_data
        
        # Check that experiences are limited to top 5
        assert len(sections["experience"]) <= 5
        
        # Check recommendations
        assert isinstance(aligned_content["recommendations"], list)
    
    def test_align_content_error_handling(self):
        """Test content alignment error handling."""
        # Test with invalid job data
        invalid_job = None
        
        result = self.agent.align_content(invalid_job, self.sample_profile_data)
        
        assert "error" in result
        assert result["profile_id"] == "test_user_123"
        assert result["alignment_metadata"]["overall_alignment_score"] == 0.0
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        # Test with low alignment
        recommendations_low = self.agent._generate_recommendations(
            0.2, {"alignment_score": 0.1}, []
        )
        assert len(recommendations_low) > 0
        assert any("emphasizing more relevant" in rec for rec in recommendations_low)
        
        # Test with high alignment
        recommendations_high = self.agent._generate_recommendations(
            0.8, {"alignment_score": 0.7}, [{"alignment_score": 0.8}]
        )
        assert len(recommendations_high) > 0
        assert any("Excellent alignment" in rec for rec in recommendations_high)
    
    def test_to_json(self):
        """Test JSON serialization."""
        aligned_content = self.agent.align_content(
            self.sample_job_data, self.sample_profile_data
        )
        
        json_str = self.agent.to_json(aligned_content)
        
        assert isinstance(json_str, str)
        assert len(json_str) > 100  # Should be substantial JSON
        assert '"profile_id"' in json_str
        assert '"alignment_metadata"' in json_str
        
        # Should be valid JSON
        import json
        parsed = json.loads(json_str)
        assert parsed["profile_id"] == aligned_content["profile_id"]
    
    def test_keyword_matching_algorithm(self):
        """Test the core keyword matching algorithm with dummy data."""
        # Dummy job requirements
        job_requirements = {
            "skills": ["Python", "Machine Learning", "TensorFlow", "AWS"],
            "experience": ["5+ years Python development", "ML model deployment"],
            "responsibilities": ["Build ML pipelines", "Optimize model performance"]
        }
        
        # Dummy applicant data
        applicant_data = {
            "skills": ["Python", "JavaScript", "TensorFlow", "Docker"],
            "experience": [
                {
                    "title": "ML Engineer",
                    "description": "Built machine learning pipelines using Python and TensorFlow. Deployed models on AWS cloud platform."
                },
                {
                    "title": "Web Developer", 
                    "description": "Developed web applications using JavaScript and React framework."
                }
            ]
        }
        
        # Extract keywords from job requirements
        job_text = " ".join(job_requirements["skills"] + job_requirements["experience"] + job_requirements["responsibilities"])
        job_keywords = self.agent.extract_keywords(job_text)
        
        # Test skill matching
        applicant_skills_text = " ".join(applicant_data["skills"])
        skill_alignment = self.agent.calculate_alignment_score(applicant_skills_text, job_keywords)
        
        assert skill_alignment > 0.0  # Should have some alignment
        
        # Test experience matching
        for exp in applicant_data["experience"]:
            exp_alignment = self.agent.calculate_alignment_score(exp["description"], job_keywords)
            
            if "ML Engineer" in exp["title"]:
                assert exp_alignment > 0.2  # ML experience should align well
            else:
                assert exp_alignment >= 0.0  # Web dev might have lower alignment
        
        # Test keyword intersection
        applicant_keywords = self.agent.extract_keywords(applicant_skills_text)
        common_keywords = job_keywords.intersection(applicant_keywords)
        
        assert "python" in common_keywords
        assert "tensorflow" in common_keywords
        assert len(common_keywords) >= 2  # Should have at least 2 matching keywords
    
    def test_experience_prioritization(self):
        """Test that experiences are properly prioritized by relevance."""
        # Create experiences with different levels of alignment
        experiences = [
            {
                "title": "Web Developer",
                "description": "Built websites using HTML and CSS"
            },
            {
                "title": "Python Developer", 
                "description": "Developed Python applications using Django framework and PostgreSQL database"
            },
            {
                "title": "Data Analyst",
                "description": "Analyzed data using Excel and PowerBI"
            }
        ]
        
        job_keywords = self.agent.extract_job_keywords(self.sample_job_data)
        highlighted = self.agent.highlight_matching_experiences(experiences, job_keywords)
        
        # Python Developer should be ranked highest
        assert highlighted[0]["title"] == "Python Developer"
        assert highlighted[0]["alignment_score"] > highlighted[1]["alignment_score"]
        assert highlighted[0]["alignment_score"] > highlighted[2]["alignment_score"]
        
        # Check matching keywords
        python_exp = highlighted[0]
        assert "python" in python_exp["matching_keywords"]
        assert "django" in python_exp["matching_keywords"]
    
    def test_skills_categorization(self):
        """Test that skills are properly categorized."""
        mixed_skills = [
            "Python", "Leadership", "Git", "Communication", 
            "JavaScript", "Problem Solving", "Docker", "Teamwork"
        ]
        
        job_keywords = {"all": set(self.agent.extract_keywords(" ".join(mixed_skills)))}
        aligned_skills = self.agent.align_skills_section(mixed_skills, job_keywords)
        
        categories = aligned_skills["skill_categories"]
        
        # Check technical skills
        assert "Python" in categories["technical"] or "Python" in categories["other"]
        assert "JavaScript" in categories["technical"] or "JavaScript" in categories["other"]
        
        # Check tools
        assert "Git" in categories["tools"] or "Git" in categories["other"]
        
        # Check soft skills
        assert "Leadership" in categories["soft"] or "Leadership" in categories["other"]
        assert "Communication" in categories["soft"] or "Communication" in categories["other"]


if __name__ == "__main__":
    pytest.main([__file__])

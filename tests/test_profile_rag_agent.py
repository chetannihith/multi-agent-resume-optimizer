"""
Tests for ProfileRAGAgent.

This module contains unit tests for the ProfileRAGAgent class,
testing vector database operations, profile retrieval, and similarity search.
"""

import json
import os
import tempfile
import shutil
import pytest
from unittest.mock import patch, MagicMock
from src.agents.profile_rag_agent import ProfileRAGAgent


class TestProfileRAGAgent:
    """Test cases for ProfileRAGAgent."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for test databases
        self.test_dir = tempfile.mkdtemp()
        
        # Sample profile data
        self.sample_profile = {
            "profile_id": "test_user_123",
            "name": "Test User",
            "skills": ["Python", "JavaScript", "React", "Machine Learning"],
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Test Corp",
                    "duration": "2020-2023",
                    "description": "Developed web applications using Python and React"
                }
            ],
            "projects": [
                {
                    "name": "ML Project",
                    "description": "Built machine learning model for predictions",
                    "technologies": "Python, TensorFlow, AWS"
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science",
                    "field": "Computer Science",
                    "institution": "Test University",
                    "year": "2020"
                }
            ]
        }
        
        # Sample job data
        self.sample_job_data = {
            "job_title": "Python Developer",
            "skills": ["Python", "Machine Learning", "AWS"],
            "requirements": ["3+ years Python experience", "ML framework knowledge"],
            "responsibilities": ["Develop ML applications", "Code review"]
        }
    
    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        # Try to clean up, but don't fail if files are locked (Windows issue with Chroma)
        if os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except PermissionError:
                # Files may be locked by Chroma on Windows, ignore cleanup error
                pass
    
    def test_initialization_faiss(self):
        """Test FAISS agent initialization."""
        try:
            agent = ProfileRAGAgent(
                db_type="faiss",
                db_path=self.test_dir,
                similarity_threshold=0.7,
                max_results=5
            )
            assert agent.db_type == "faiss"
            assert agent.db_path == self.test_dir
            assert agent.similarity_threshold == 0.7
            assert agent.max_results == 5
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("FAISS dependencies not available")
            else:
                raise
    
    def test_initialization_chroma(self):
        """Test Chroma agent initialization."""
        try:
            agent = ProfileRAGAgent(
                db_type="chroma",
                db_path=self.test_dir,
                similarity_threshold=0.6,
                max_results=10
            )
            assert agent.db_type == "chroma"
            assert agent.db_path == self.test_dir
            assert agent.similarity_threshold == 0.6
            assert agent.max_results == 10
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("Chroma dependencies not available")
            else:
                raise
    
    def test_initialization_invalid_db_type(self):
        """Test initialization with invalid database type."""
        with pytest.raises(ValueError, match="Unsupported database type"):
            ProfileRAGAgent(db_type="invalid_db")
    
    def test_profile_to_text(self):
        """Test profile to text conversion."""
        try:
            agent = ProfileRAGAgent(db_type="faiss", db_path=self.test_dir)
            text = agent._profile_to_text(self.sample_profile)
            
            assert "Python" in text
            assert "JavaScript" in text
            assert "Software Engineer" in text
            assert "ML Project" in text
            assert "Computer Science" in text
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("Dependencies not available")
            else:
                raise
    
    def test_job_data_to_query(self):
        """Test job data to query conversion."""
        try:
            agent = ProfileRAGAgent(db_type="faiss", db_path=self.test_dir)
            query = agent._job_data_to_query(self.sample_job_data)
            
            assert "Python Developer" in query
            assert "Python" in query
            assert "Machine Learning" in query
            assert "Develop ML applications" in query
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("Dependencies not available")
            else:
                raise
    
    def test_database_initialization_faiss(self):
        """Test FAISS database initialization."""
        try:
            agent = ProfileRAGAgent(db_type="faiss", db_path=self.test_dir)
            result = agent.initialize_database()
            assert result is True
            assert agent.faiss_index is not None
            assert isinstance(agent.faiss_metadata, list)
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("FAISS dependencies not available")
            else:
                raise
    
    def test_database_initialization_chroma(self):
        """Test Chroma database initialization."""
        try:
            agent = ProfileRAGAgent(db_type="chroma", db_path=self.test_dir)
            result = agent.initialize_database()
            assert result is True
            assert agent.chroma_client is not None
            assert agent.chroma_collection is not None
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("Chroma dependencies not available")
            else:
                raise
    
    def test_add_profile_data_faiss(self):
        """Test adding profile data to FAISS."""
        try:
            agent = ProfileRAGAgent(db_type="faiss", db_path=self.test_dir)
            agent.initialize_database()
            
            result = agent.add_profile_data(self.sample_profile)
            assert result is True
            assert len(agent.faiss_metadata) == 1
            assert agent.faiss_metadata[0]["id"] == "test_user_123"
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("FAISS dependencies not available")
            else:
                raise
    
    def test_add_profile_data_chroma(self):
        """Test adding profile data to Chroma."""
        try:
            agent = ProfileRAGAgent(db_type="chroma", db_path=self.test_dir)
            agent.initialize_database()
            
            result = agent.add_profile_data(self.sample_profile)
            assert result is True
            
            # Check if data was added
            count = agent.chroma_collection.count()
            assert count == 1
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("Chroma dependencies not available")
            else:
                raise
    
    def test_retrieve_relevant_profile_faiss(self):
        """Test retrieving relevant profile from FAISS."""
        try:
            agent = ProfileRAGAgent(
                db_type="faiss", 
                db_path=self.test_dir,
                similarity_threshold=0.1  # Low threshold for testing
            )
            agent.initialize_database()
            agent.add_profile_data(self.sample_profile)
            
            result = agent.retrieve_relevant_profile(self.sample_job_data)
            
            assert "profile_id" in result
            assert "relevant_skills" in result
            assert "relevant_experience" in result
            assert "relevant_projects" in result
            assert "similarity_scores" in result
            assert result["profile_id"] == "test_user_123"
            assert "Python" in result["relevant_skills"]
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("FAISS dependencies not available")
            else:
                raise
    
    def test_retrieve_relevant_profile_chroma(self):
        """Test retrieving relevant profile from Chroma."""
        try:
            agent = ProfileRAGAgent(
                db_type="chroma", 
                db_path=self.test_dir,
                similarity_threshold=0.1  # Low threshold for testing
            )
            agent.initialize_database()
            agent.add_profile_data(self.sample_profile)
            
            result = agent.retrieve_relevant_profile(self.sample_job_data)
            
            assert "profile_id" in result
            assert "relevant_skills" in result
            assert "relevant_experience" in result
            assert "relevant_projects" in result
            assert result["profile_id"] == "test_user_123"
            assert "Python" in result["relevant_skills"]
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("Chroma dependencies not available")
            else:
                raise
    
    def test_retrieve_no_matches(self):
        """Test retrieving when no profiles match."""
        try:
            agent = ProfileRAGAgent(
                db_type="faiss", 
                db_path=self.test_dir,
                similarity_threshold=0.99  # Very high threshold
            )
            agent.initialize_database()
            agent.add_profile_data(self.sample_profile)
            
            # Job data with no matching skills
            unrelated_job = {
                "job_title": "Accountant",
                "skills": ["Excel", "QuickBooks"],
                "requirements": ["CPA certification"],
                "responsibilities": ["Manage books"]
            }
            
            result = agent.retrieve_relevant_profile(unrelated_job)
            assert result["profile_id"] == "no_matches"
            assert len(result["relevant_skills"]) == 0
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("FAISS dependencies not available")
            else:
                raise
    
    def test_get_database_stats_faiss(self):
        """Test getting database statistics for FAISS."""
        try:
            agent = ProfileRAGAgent(db_type="faiss", db_path=self.test_dir)
            agent.initialize_database()
            agent.add_profile_data(self.sample_profile)
            
            stats = agent.get_database_stats()
            assert stats["db_type"] == "faiss"
            assert stats["total_profiles"] == 1
            assert stats["index_size"] == 1
            assert "embedding_dimension" in stats
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("FAISS dependencies not available")
            else:
                raise
    
    def test_get_database_stats_chroma(self):
        """Test getting database statistics for Chroma."""
        try:
            agent = ProfileRAGAgent(db_type="chroma", db_path=self.test_dir)
            agent.initialize_database()
            agent.add_profile_data(self.sample_profile)
            
            stats = agent.get_database_stats()
            assert stats["db_type"] == "chroma"
            assert stats["total_profiles"] == 1
            assert "collection_name" in stats
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("Chroma dependencies not available")
            else:
                raise
    
    def test_save_database_faiss(self):
        """Test saving FAISS database."""
        try:
            agent = ProfileRAGAgent(db_type="faiss", db_path=self.test_dir)
            agent.initialize_database()
            agent.add_profile_data(self.sample_profile)
            
            result = agent.save_database()
            assert result is True
            
            # Check if files were created
            index_path = os.path.join(self.test_dir, "faiss_index.bin")
            metadata_path = os.path.join(self.test_dir, "faiss_metadata.json")
            assert os.path.exists(index_path)
            assert os.path.exists(metadata_path)
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("FAISS dependencies not available")
            else:
                raise
    
    def test_save_database_chroma(self):
        """Test saving Chroma database."""
        try:
            agent = ProfileRAGAgent(db_type="chroma", db_path=self.test_dir)
            agent.initialize_database()
            agent.add_profile_data(self.sample_profile)
            
            result = agent.save_database()
            assert result is True  # Chroma auto-saves
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("Chroma dependencies not available")
            else:
                raise
    
    def test_process_search_results(self):
        """Test processing search results."""
        try:
            agent = ProfileRAGAgent(db_type="faiss", db_path=self.test_dir)
            
            # Mock search results
            mock_results = [
                (0.8, {
                    "id": "test_user_123",
                    "profile_data": self.sample_profile
                })
            ]
            
            processed = agent._process_search_results(mock_results, self.sample_job_data)
            
            assert processed["profile_id"] == "test_user_123"
            assert "Python" in processed["relevant_skills"]
            assert len(processed["relevant_experience"]) > 0
            assert len(processed["similarity_scores"]) > 0
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("Dependencies not available")
            else:
                raise
    
    def test_process_empty_search_results(self):
        """Test processing empty search results."""
        try:
            agent = ProfileRAGAgent(db_type="faiss", db_path=self.test_dir)
            
            processed = agent._process_search_results([], self.sample_job_data)
            
            assert processed["profile_id"] == "no_matches"
            assert len(processed["relevant_skills"]) == 0
            assert len(processed["relevant_experience"]) == 0
            assert len(processed["similarity_scores"]) == 0
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("Dependencies not available")
            else:
                raise
    
    def test_error_handling_retrieve_profile(self):
        """Test error handling in retrieve_relevant_profile."""
        try:
            agent = ProfileRAGAgent(db_type="faiss", db_path=self.test_dir)
            # Don't initialize database to cause error
            
            result = agent.retrieve_relevant_profile(self.sample_job_data)
            
            # When no database is initialized, it returns no_matches instead of error
            assert result["profile_id"] in ["error", "no_matches"]
            assert len(result["relevant_skills"]) == 0
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("FAISS dependencies not available")
            else:
                raise
    
    def test_multiple_profiles_ranking(self):
        """Test that multiple profiles are ranked by similarity."""
        try:
            agent = ProfileRAGAgent(
                db_type="faiss", 
                db_path=self.test_dir,
                similarity_threshold=0.1
            )
            agent.initialize_database()
            
            # Add multiple profiles
            profile1 = {
                "profile_id": "python_expert",
                "skills": ["Python", "Machine Learning", "TensorFlow", "AWS"],
                "experience": [{"title": "ML Engineer", "description": "Python ML work"}]
            }
            
            profile2 = {
                "profile_id": "java_expert", 
                "skills": ["Java", "Spring", "Hibernate"],
                "experience": [{"title": "Java Developer", "description": "Java enterprise work"}]
            }
            
            agent.add_profile_data(profile1)
            agent.add_profile_data(profile2)
            
            # Search for Python job
            python_job = {
                "job_title": "Python ML Engineer",
                "skills": ["Python", "Machine Learning", "TensorFlow"],
                "requirements": ["Python expertise", "ML experience"]
            }
            
            result = agent.retrieve_relevant_profile(python_job)
            
            # Should match the Python expert better
            assert result["profile_id"] == "python_expert"
            assert "Python" in result["relevant_skills"]
            assert "Machine Learning" in result["relevant_skills"]
        except ValueError as e:
            if "dependencies not available" in str(e):
                pytest.skip("FAISS dependencies not available")
            else:
                raise


if __name__ == "__main__":
    pytest.main([__file__])

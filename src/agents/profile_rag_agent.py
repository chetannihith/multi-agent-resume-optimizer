"""
ProfileRAGAgent - Retrieves applicant information from vector database.

This module contains the ProfileRAGAgent class that loads applicant data
from FAISS or Chroma vector databases and retrieves the most relevant
information based on job description requirements.
"""

import json
import os
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import logging

try:
    import numpy as np
    import faiss
    from sentence_transformers import SentenceTransformer
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    np = None
    faiss = None
    SentenceTransformer = None

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    chromadb = None


class ProfileRAGAgent:
    """
    Agent for retrieving applicant information from vector databases.
    
    This agent supports both FAISS and Chroma vector databases for storing
    and retrieving applicant profile information including skills, projects,
    and experience based on job description similarity.
    """
    
    def __init__(
        self, 
        db_type: str = "faiss",
        db_path: str = "./data/profiles",
        model_name: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.7,
        max_results: int = 10
    ):
        """
        Initialize the ProfileRAGAgent.
        
        Args:
            db_type: Type of vector database ("faiss" or "chroma")
            db_path: Path to the database files
            model_name: Name of the sentence transformer model
            similarity_threshold: Minimum similarity score for results
            max_results: Maximum number of results to return
            
        Raises:
            ValueError: If db_type is not supported or dependencies missing
        """
        self.db_type = db_type.lower()
        self.db_path = db_path
        self.similarity_threshold = similarity_threshold
        self.max_results = max_results
        
        # Validate database type and dependencies
        if self.db_type == "faiss" and not FAISS_AVAILABLE:
            raise ValueError(
                "FAISS dependencies not available. Install with: "
                "pip install faiss-cpu sentence-transformers numpy"
            )
        elif self.db_type == "chroma" and not CHROMA_AVAILABLE:
            raise ValueError(
                "Chroma dependencies not available. Install with: "
                "pip install chromadb"
            )
        elif self.db_type not in ["faiss", "chroma"]:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        # Initialize sentence transformer model
        if self.db_type == "faiss":
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
        else:
            self.model = None  # Chroma handles embeddings internally
            
        # Initialize database connections
        self.faiss_index = None
        self.faiss_metadata = []
        self.chroma_client = None
        self.chroma_collection = None
        
        # Create database directory if it doesn't exist
        os.makedirs(self.db_path, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def initialize_database(self, force_recreate: bool = False) -> bool:
        """
        Initialize the vector database.
        
        Args:
            force_recreate: Whether to recreate the database if it exists
            
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            if self.db_type == "faiss":
                return self._initialize_faiss(force_recreate)
            else:
                return self._initialize_chroma(force_recreate)
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            return False
    
    def _initialize_faiss(self, force_recreate: bool = False) -> bool:
        """
        Initialize FAISS vector database.
        
        Args:
            force_recreate: Whether to recreate the database if it exists
            
        Returns:
            True if initialization successful, False otherwise
        """
        index_path = os.path.join(self.db_path, "faiss_index.bin")
        metadata_path = os.path.join(self.db_path, "faiss_metadata.json")
        
        if not force_recreate and os.path.exists(index_path):
            # Load existing index
            try:
                self.faiss_index = faiss.read_index(index_path)
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    self.faiss_metadata = json.load(f)
                self.logger.info(f"Loaded existing FAISS index with {len(self.faiss_metadata)} entries")
                return True
            except Exception as e:
                self.logger.warning(f"Failed to load existing index: {e}")
        
        # Create new index
        self.faiss_index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
        self.faiss_metadata = []
        self.logger.info("Created new FAISS index")
        return True
    
    def _initialize_chroma(self, force_recreate: bool = False) -> bool:
        """
        Initialize Chroma vector database.
        
        Args:
            force_recreate: Whether to recreate the database if it exists
            
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Initialize Chroma client
            self.chroma_client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            collection_name = "applicant_profiles"
            
            if force_recreate:
                try:
                    self.chroma_client.delete_collection(collection_name)
                except Exception:
                    pass  # Collection might not exist
            
            # Get or create collection
            try:
                self.chroma_collection = self.chroma_client.get_collection(collection_name)
                self.logger.info(f"Loaded existing Chroma collection: {collection_name}")
            except Exception:
                self.chroma_collection = self.chroma_client.create_collection(
                    name=collection_name,
                    metadata={"description": "Applicant profile embeddings"}
                )
                self.logger.info(f"Created new Chroma collection: {collection_name}")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Chroma: {e}")
            return False
    
    def add_profile_data(self, profile_data: Dict[str, Any]) -> bool:
        """
        Add applicant profile data to the vector database.
        
        Args:
            profile_data: Dictionary containing applicant profile information
            
        Returns:
            True if data added successfully, False otherwise
        """
        try:
            if self.db_type == "faiss":
                return self._add_to_faiss(profile_data)
            else:
                return self._add_to_chroma(profile_data)
        except Exception as e:
            self.logger.error(f"Failed to add profile data: {e}")
            return False
    
    def _add_to_faiss(self, profile_data: Dict[str, Any]) -> bool:
        """
        Add profile data to FAISS index.
        
        Args:
            profile_data: Dictionary containing applicant profile information
            
        Returns:
            True if data added successfully, False otherwise
        """
        # Create text representation of profile for embedding
        profile_text = self._profile_to_text(profile_data)
        
        # Generate embedding
        embedding = self.model.encode([profile_text])
        
        # Normalize for cosine similarity
        faiss.normalize_L2(embedding)
        
        # Add to index
        self.faiss_index.add(embedding)
        
        # Add metadata
        metadata_entry = {
            "id": profile_data.get("profile_id", str(uuid.uuid4())),
            "profile_data": profile_data,
            "text": profile_text,
            "added_at": datetime.now().isoformat()
        }
        self.faiss_metadata.append(metadata_entry)
        
        return True
    
    def _add_to_chroma(self, profile_data: Dict[str, Any]) -> bool:
        """
        Add profile data to Chroma collection.
        
        Args:
            profile_data: Dictionary containing applicant profile information
            
        Returns:
            True if data added successfully, False otherwise
        """
        profile_id = profile_data.get("profile_id", str(uuid.uuid4()))
        profile_text = self._profile_to_text(profile_data)
        
        self.chroma_collection.add(
            documents=[profile_text],
            metadatas=[{
                "profile_id": profile_id,
                "profile_data": json.dumps(profile_data),
                "added_at": datetime.now().isoformat()
            }],
            ids=[profile_id]
        )
        
        return True
    
    def _profile_to_text(self, profile_data: Dict[str, Any]) -> str:
        """
        Convert profile data to text representation for embedding.
        
        Args:
            profile_data: Dictionary containing applicant profile information
            
        Returns:
            Text representation of the profile
        """
        text_parts = []
        
        # Add skills
        if "skills" in profile_data:
            skills = profile_data["skills"]
            if isinstance(skills, list):
                text_parts.append("Skills: " + ", ".join(skills))
            elif isinstance(skills, str):
                text_parts.append("Skills: " + skills)
        
        # Add experience
        if "experience" in profile_data:
            experience = profile_data["experience"]
            if isinstance(experience, list):
                for exp in experience:
                    if isinstance(exp, dict):
                        exp_text = f"Experience: {exp.get('title', '')} at {exp.get('company', '')}. {exp.get('description', '')}"
                        text_parts.append(exp_text)
                    else:
                        text_parts.append(f"Experience: {exp}")
            elif isinstance(experience, str):
                text_parts.append("Experience: " + experience)
        
        # Add projects
        if "projects" in profile_data:
            projects = profile_data["projects"]
            if isinstance(projects, list):
                for project in projects:
                    if isinstance(project, dict):
                        proj_text = f"Project: {project.get('name', '')}. {project.get('description', '')}. Technologies: {project.get('technologies', '')}"
                        text_parts.append(proj_text)
                    else:
                        text_parts.append(f"Project: {project}")
            elif isinstance(projects, str):
                text_parts.append("Projects: " + projects)
        
        # Add education
        if "education" in profile_data:
            education = profile_data["education"]
            if isinstance(education, list):
                for edu in education:
                    if isinstance(edu, dict):
                        edu_text = f"Education: {edu.get('degree', '')} in {edu.get('field', '')} from {edu.get('institution', '')}"
                        text_parts.append(edu_text)
                    else:
                        text_parts.append(f"Education: {edu}")
            elif isinstance(education, str):
                text_parts.append("Education: " + education)
        
        return " ".join(text_parts)
    
    def retrieve_relevant_profile(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve relevant profile information based on job description.
        
        Args:
            job_data: Dictionary containing job description data from JDExtractorAgent
            
        Returns:
            Dictionary containing relevant profile information
        """
        try:
            # Create query text from job data
            query_text = self._job_data_to_query(job_data)
            
            if self.db_type == "faiss":
                results = self._search_faiss(query_text)
            else:
                results = self._search_chroma(query_text)
            
            # Process and filter results
            relevant_data = self._process_search_results(results, job_data)
            
            return {
                "profile_id": relevant_data.get("profile_id", "unknown"),
                "relevant_skills": relevant_data.get("relevant_skills", []),
                "relevant_experience": relevant_data.get("relevant_experience", []),
                "relevant_projects": relevant_data.get("relevant_projects", []),
                "relevant_education": relevant_data.get("relevant_education", []),
                "similarity_scores": relevant_data.get("similarity_scores", []),
                "query_text": query_text,
                "total_matches": len(results),
                "retrieved_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve relevant profile: {e}")
            return {
                "profile_id": "error",
                "relevant_skills": [],
                "relevant_experience": [],
                "relevant_projects": [],
                "relevant_education": [],
                "similarity_scores": [],
                "query_text": "",
                "total_matches": 0,
                "error": str(e),
                "retrieved_at": datetime.now().isoformat()
            }
    
    def _job_data_to_query(self, job_data: Dict[str, Any]) -> str:
        """
        Convert job description data to query text.
        
        Args:
            job_data: Dictionary containing job description data
            
        Returns:
            Query text for similarity search
        """
        query_parts = []
        
        # Add job title
        if "job_title" in job_data and job_data["job_title"]:
            query_parts.append(job_data["job_title"])
        
        # Add skills
        if "skills" in job_data and job_data["skills"]:
            if isinstance(job_data["skills"], list):
                query_parts.extend(job_data["skills"])
            else:
                query_parts.append(str(job_data["skills"]))
        
        # Add requirements
        if "requirements" in job_data and job_data["requirements"]:
            if isinstance(job_data["requirements"], list):
                query_parts.extend(job_data["requirements"])
            else:
                query_parts.append(str(job_data["requirements"]))
        
        # Add responsibilities
        if "responsibilities" in job_data and job_data["responsibilities"]:
            if isinstance(job_data["responsibilities"], list):
                query_parts.extend(job_data["responsibilities"])
            else:
                query_parts.append(str(job_data["responsibilities"]))
        
        return " ".join(query_parts)
    
    def _search_faiss(self, query_text: str) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Search FAISS index for similar profiles.
        
        Args:
            query_text: Query text for similarity search
            
        Returns:
            List of tuples containing (similarity_score, metadata)
        """
        if self.faiss_index is None or self.faiss_index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.model.encode([query_text])
        faiss.normalize_L2(query_embedding)
        
        # Search
        k = min(self.max_results, self.faiss_index.ntotal)
        scores, indices = self.faiss_index.search(query_embedding, k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if score >= self.similarity_threshold and idx < len(self.faiss_metadata):
                results.append((float(score), self.faiss_metadata[idx]))
        
        return results
    
    def _search_chroma(self, query_text: str) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Search Chroma collection for similar profiles.
        
        Args:
            query_text: Query text for similarity search
            
        Returns:
            List of tuples containing (similarity_score, metadata)
        """
        if self.chroma_collection is None:
            return []
        
        try:
            results = self.chroma_collection.query(
                query_texts=[query_text],
                n_results=self.max_results
            )
            
            processed_results = []
            if results["distances"] and results["metadatas"]:
                for distance, metadata in zip(results["distances"][0], results["metadatas"][0]):
                    # Convert distance to similarity (Chroma uses distance, we want similarity)
                    similarity = 1.0 - distance
                    if similarity >= self.similarity_threshold:
                        # Parse profile data from metadata
                        profile_data = json.loads(metadata["profile_data"])
                        metadata_with_profile = {
                            "id": metadata["profile_id"],
                            "profile_data": profile_data,
                            "added_at": metadata["added_at"]
                        }
                        processed_results.append((similarity, metadata_with_profile))
            
            return processed_results
        except Exception as e:
            self.logger.error(f"Chroma search failed: {e}")
            return []
    
    def _process_search_results(
        self, 
        results: List[Tuple[float, Dict[str, Any]]], 
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process search results to extract relevant information.
        
        Args:
            results: List of search results with similarity scores
            job_data: Original job description data
            
        Returns:
            Dictionary containing processed relevant information
        """
        if not results:
            return {
                "profile_id": "no_matches",
                "relevant_skills": [],
                "relevant_experience": [],
                "relevant_projects": [],
                "relevant_education": [],
                "similarity_scores": []
            }
        
        # Use the best matching profile
        best_score, best_metadata = results[0]
        profile_data = best_metadata["profile_data"]
        
        # Extract job requirements for filtering
        job_skills = set()
        if "skills" in job_data and job_data["skills"]:
            if isinstance(job_data["skills"], list):
                job_skills.update([skill.lower() for skill in job_data["skills"]])
            else:
                job_skills.add(str(job_data["skills"]).lower())
        
        job_keywords = set()
        for key in ["requirements", "responsibilities"]:
            if key in job_data and job_data[key]:
                if isinstance(job_data[key], list):
                    job_keywords.update([item.lower() for item in job_data[key]])
                else:
                    job_keywords.add(str(job_data[key]).lower())
        
        # Filter relevant skills
        relevant_skills = []
        if "skills" in profile_data:
            profile_skills = profile_data["skills"]
            if isinstance(profile_skills, list):
                for skill in profile_skills:
                    if any(job_skill in skill.lower() for job_skill in job_skills):
                        relevant_skills.append(skill)
            elif isinstance(profile_skills, str):
                if any(job_skill in profile_skills.lower() for job_skill in job_skills):
                    relevant_skills.append(profile_skills)
        
        # Filter relevant experience
        relevant_experience = []
        if "experience" in profile_data:
            experience = profile_data["experience"]
            if isinstance(experience, list):
                for exp in experience:
                    if isinstance(exp, dict):
                        exp_text = f"{exp.get('title', '')} {exp.get('description', '')}".lower()
                        if any(keyword in exp_text for keyword in job_keywords | job_skills):
                            relevant_experience.append(exp)
                    else:
                        if any(keyword in str(exp).lower() for keyword in job_keywords | job_skills):
                            relevant_experience.append(exp)
        
        # Filter relevant projects
        relevant_projects = []
        if "projects" in profile_data:
            projects = profile_data["projects"]
            if isinstance(projects, list):
                for project in projects:
                    if isinstance(project, dict):
                        proj_text = f"{project.get('name', '')} {project.get('description', '')} {project.get('technologies', '')}".lower()
                        if any(keyword in proj_text for keyword in job_keywords | job_skills):
                            relevant_projects.append(project)
                    else:
                        if any(keyword in str(project).lower() for keyword in job_keywords | job_skills):
                            relevant_projects.append(project)
        
        # Include all education (usually relevant)
        relevant_education = profile_data.get("education", [])
        
        return {
            "profile_id": best_metadata.get("id", "unknown"),
            "relevant_skills": relevant_skills,
            "relevant_experience": relevant_experience,
            "relevant_projects": relevant_projects,
            "relevant_education": relevant_education,
            "similarity_scores": [score for score, _ in results[:5]]  # Top 5 scores
        }
    
    def save_database(self) -> bool:
        """
        Save the current database state to disk.
        
        Returns:
            True if save successful, False otherwise
        """
        try:
            if self.db_type == "faiss":
                return self._save_faiss()
            else:
                # Chroma auto-saves with PersistentClient
                return True
        except Exception as e:
            self.logger.error(f"Failed to save database: {e}")
            return False
    
    def _save_faiss(self) -> bool:
        """
        Save FAISS index and metadata to disk.
        
        Returns:
            True if save successful, False otherwise
        """
        if self.faiss_index is None:
            return False
        
        index_path = os.path.join(self.db_path, "faiss_index.bin")
        metadata_path = os.path.join(self.db_path, "faiss_metadata.json")
        
        # Save index
        faiss.write_index(self.faiss_index, index_path)
        
        # Save metadata
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.faiss_metadata, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved FAISS database with {len(self.faiss_metadata)} entries")
        return True
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current database.
        
        Returns:
            Dictionary containing database statistics
        """
        stats = {
            "db_type": self.db_type,
            "db_path": self.db_path,
            "similarity_threshold": self.similarity_threshold,
            "max_results": self.max_results
        }
        
        if self.db_type == "faiss":
            stats.update({
                "total_profiles": len(self.faiss_metadata) if self.faiss_metadata else 0,
                "index_size": self.faiss_index.ntotal if self.faiss_index else 0,
                "embedding_dimension": self.embedding_dim
            })
        else:
            try:
                count = self.chroma_collection.count() if self.chroma_collection else 0
                stats.update({
                    "total_profiles": count,
                    "collection_name": self.chroma_collection.name if self.chroma_collection else None
                })
            except Exception:
                stats.update({
                    "total_profiles": 0,
                    "collection_name": None
                })
        
        return stats


def main():
    """
    Main function for testing the ProfileRAGAgent with dummy data.
    """
    print("ProfileRAGAgent Test")
    print("=" * 50)
    
    # Create dummy applicant data
    dummy_profiles = [
        {
            "profile_id": "john_doe_2024",
            "name": "John Doe",
            "skills": [
                "Python", "JavaScript", "React", "Node.js", "SQL", 
                "Machine Learning", "TensorFlow", "AWS", "Docker", "Git"
            ],
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "TechCorp Inc.",
                    "duration": "2021-2024",
                    "description": "Led development of microservices architecture using Python and Docker. Implemented ML models for recommendation systems."
                },
                {
                    "title": "Full Stack Developer",
                    "company": "StartupXYZ",
                    "duration": "2019-2021",
                    "description": "Built web applications using React and Node.js. Managed AWS infrastructure and CI/CD pipelines."
                }
            ],
            "projects": [
                {
                    "name": "E-commerce Recommendation Engine",
                    "description": "Built ML-powered recommendation system using TensorFlow and Python",
                    "technologies": "Python, TensorFlow, AWS, Docker"
                },
                {
                    "name": "Real-time Chat Application",
                    "description": "Developed scalable chat app with React frontend and Node.js backend",
                    "technologies": "React, Node.js, Socket.io, MongoDB"
                }
            ],
            "education": [
                {
                    "degree": "Master of Science",
                    "field": "Computer Science",
                    "institution": "Tech University",
                    "year": "2019"
                }
            ]
        },
        {
            "profile_id": "jane_smith_dev",
            "name": "Jane Smith",
            "skills": [
                "Java", "Spring Boot", "Kubernetes", "PostgreSQL", 
                "Microservices", "REST APIs", "Jenkins", "Terraform"
            ],
            "experience": [
                {
                    "title": "Backend Engineer",
                    "company": "Enterprise Solutions",
                    "duration": "2020-2024",
                    "description": "Designed and implemented microservices using Java Spring Boot. Managed Kubernetes deployments."
                }
            ],
            "projects": [
                {
                    "name": "Banking API Platform",
                    "description": "Built secure REST APIs for banking operations using Spring Boot",
                    "technologies": "Java, Spring Boot, PostgreSQL, Kubernetes"
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Engineering",
                    "field": "Software Engineering",
                    "institution": "Engineering College",
                    "year": "2020"
                }
            ]
        }
    ]
    
    # Create dummy job description
    dummy_job_data = {
        "job_title": "Senior Python Developer",
        "skills": [
            "Python", "Machine Learning", "TensorFlow", "AWS", 
            "Docker", "Microservices", "REST APIs"
        ],
        "requirements": [
            "5+ years Python experience",
            "Experience with ML frameworks",
            "Cloud platform experience (AWS/GCP)",
            "Containerization with Docker"
        ],
        "responsibilities": [
            "Develop ML-powered applications",
            "Design scalable microservices",
            "Collaborate with cross-functional teams",
            "Mentor junior developers"
        ]
    }
    
    # Test with different database types
    for db_type in ["faiss", "chroma"]:
        print(f"\nTesting with {db_type.upper()} database:")
        print("-" * 30)
        
        try:
            # Initialize agent
            agent = ProfileRAGAgent(
                db_type=db_type,
                db_path=f"./test_data/{db_type}_profiles",
                similarity_threshold=0.3,  # Lower threshold for demo
                max_results=5
            )
            
            # Initialize database
            if not agent.initialize_database(force_recreate=True):
                print(f"Failed to initialize {db_type} database")
                continue
            
            # Add dummy profiles
            print("Adding dummy profiles...")
            for profile in dummy_profiles:
                if agent.add_profile_data(profile):
                    print(f"  Added profile: {profile['name']}")
                else:
                    print(f"  Failed to add profile: {profile['name']}")
            
            # Save database
            agent.save_database()
            
            # Get database stats
            stats = agent.get_database_stats()
            print(f"Database stats: {stats['total_profiles']} profiles")
            
            # Retrieve relevant profile
            print(f"\nSearching for relevant profile...")
            print(f"Job: {dummy_job_data['job_title']}")
            
            relevant_data = agent.retrieve_relevant_profile(dummy_job_data)
            
            print(f"Best match: {relevant_data['profile_id']}")
            print(f"Similarity scores: {relevant_data['similarity_scores']}")
            print(f"Relevant skills: {relevant_data['relevant_skills']}")
            print(f"Relevant experience count: {len(relevant_data['relevant_experience'])}")
            print(f"Relevant projects count: {len(relevant_data['relevant_projects'])}")
            
            # Display first relevant experience if available
            if relevant_data['relevant_experience']:
                exp = relevant_data['relevant_experience'][0]
                if isinstance(exp, dict):
                    print(f"Top experience: {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}")
            
        except Exception as e:
            print(f"Error testing {db_type}: {e}")
            if "dependencies not available" in str(e):
                print(f"Skipping {db_type} - dependencies not installed")
            else:
                import traceback
                traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("ProfileRAGAgent test completed!")
    print("Note: Install dependencies with:")
    print("  pip install faiss-cpu sentence-transformers numpy chromadb")


if __name__ == "__main__":
    main()

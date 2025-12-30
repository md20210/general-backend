"""Comparison Service for ChromaDB vs Elasticsearch."""
import logging
import time
from typing import Dict, Any, List, Optional
from uuid import UUID
from backend.services.vector_store import VectorStore
from backend.services.elasticsearch_service import ElasticsearchService

logger = logging.getLogger(__name__)


class ElasticsearchComparisonService:
    """Service to compare ChromaDB and Elasticsearch performance and features."""

    def __init__(self):
        """Initialize both vector stores."""
        self.chromadb = VectorStore()
        self.elasticsearch = ElasticsearchService()
        logger.info("ElasticsearchComparisonService initialized")

    async def compare_search_performance(
        self,
        user_id: str,
        job_description: str,
        required_skills: Optional[List[str]] = None,
        project_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Compare search performance between ChromaDB and Elasticsearch.

        Args:
            user_id: User ID for searching
            job_description: Job description text
            required_skills: List of required skills
            project_id: Optional ChromaDB project ID

        Returns:
            Comparison results with timing and match quality
        """
        comparison_results = {
            "chromadb": {},
            "elasticsearch": {},
            "performance_comparison": {},
            "feature_comparison": {}
        }

        # 1. ChromaDB Search
        try:
            start_time = time.time()
            chromadb_results = self.chromadb.query(
                user_id=UUID(user_id) if isinstance(user_id, str) else user_id,
                query_text=job_description,
                project_id=project_id,
                n_results=10
            )
            chromadb_time_ms = (time.time() - start_time) * 1000

            # Handle empty results
            if not chromadb_results or not isinstance(chromadb_results, list):
                chromadb_results = []

            comparison_results["chromadb"] = {
                "search_time_ms": chromadb_time_ms,
                "results": chromadb_results,
                "total_matches": len(chromadb_results),
                "relevance_scores": [r.get("distance", 0) for r in chromadb_results[:5]] if chromadb_results else []
            }
        except Exception as e:
            logger.warning(f"ChromaDB search skipped (no data or error): {e}")
            comparison_results["chromadb"] = {
                "error": str(e),
                "search_time_ms": 0,
                "total_matches": 0,
                "results": [],
                "relevance_scores": []
            }

        # 2. Elasticsearch Search
        try:
            if not self.elasticsearch.is_available():
                raise Exception("Elasticsearch service not available")

            es_results = await self.elasticsearch.search_cv_match(
                job_description=job_description,
                required_skills=required_skills,
                user_id=user_id
            )

            comparison_results["elasticsearch"] = {
                "search_time_ms": es_results["search_time_ms"],
                "results": es_results["matches"],
                "total_matches": es_results["total_matches"],
                "max_score": es_results.get("max_score", 0),
                "relevance_scores": [m["score"] for m in es_results["matches"][:5]] if es_results["matches"] else []
            }
        except Exception as e:
            logger.error(f"Elasticsearch search error: {e}")
            comparison_results["elasticsearch"] = {
                "error": str(e),
                "search_time_ms": 0,
                "total_matches": 0,
                "results": [],
                "relevance_scores": []
            }

        # 3. Performance Comparison
        chromadb_time = comparison_results["chromadb"].get("search_time_ms", 0)
        es_time = comparison_results["elasticsearch"].get("search_time_ms", 0)

        if chromadb_time > 0 and es_time > 0:
            speedup = chromadb_time / es_time if es_time > 0 else 0
            comparison_results["performance_comparison"] = {
                "chromadb_time_ms": chromadb_time,
                "elasticsearch_time_ms": es_time,
                "speedup_factor": round(speedup, 2),
                "faster_system": "Elasticsearch" if es_time < chromadb_time else "ChromaDB",
                "time_saved_ms": abs(chromadb_time - es_time),
                "percentage_difference": round(abs(chromadb_time - es_time) / max(chromadb_time, es_time) * 100, 2)
            }

        # 4. Feature Comparison
        comparison_results["feature_comparison"] = {
            "chromadb": {
                "features": ["Vector embeddings", "Semantic search", "Distance-based similarity"],
                "strengths": ["Simple API", "Lightweight", "Good for small datasets"],
                "limitations": ["No fuzzy matching", "No synonyms", "Limited query types"]
            },
            "elasticsearch": {
                "features": [
                    "Full-text search",
                    "Fuzzy matching (typo tolerance)",
                    "Synonym support",
                    "Multi-field weighted search",
                    "Aggregations and analytics",
                    "Highlighting",
                    "Advanced filtering"
                ],
                "strengths": [
                    "Production-ready",
                    "Scales horizontally",
                    "Rich query DSL",
                    "Real-time analytics"
                ],
                "limitations": ["More complex setup", "Resource intensive"]
            }
        }

        return comparison_results

    async def get_advanced_features_demo(
        self,
        user_id: str,
        required_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Demonstrate Elasticsearch's advanced features.

        Args:
            user_id: User ID to search
            required_skills: Skills to search for

        Returns:
            Advanced feature results
        """
        demo_results = {}

        # 1. Fuzzy Matching (typo tolerance)
        try:
            if not self.elasticsearch.is_available():
                raise Exception("Elasticsearch not available")

            fuzzy_matches = await self.elasticsearch.get_fuzzy_matches(
                skills=required_skills,
                user_id=user_id
            )
            demo_results["fuzzy_matching"] = {
                "description": "Handles typos and misspellings automatically",
                "example": "Searching 'Pythn' matches 'Python'",
                "results": fuzzy_matches,
                "benefit": "Catches candidates even with typos in CV or job description"
            }
        except Exception as e:
            logger.warning(f"Fuzzy matching demo skipped: {e}")
            demo_results["fuzzy_matching"] = {
                "description": "Handles typos and misspellings automatically",
                "error": str(e),
                "results": []
            }

        # 2. Synonym Support
        try:
            if not self.elasticsearch.is_available():
                raise Exception("Elasticsearch not available")

            synonym_matches = await self.elasticsearch.get_synonym_matches(
                skills=required_skills,
                user_id=user_id
            )
            demo_results["synonym_matching"] = {
                "description": "Matches related terms and synonyms",
                "examples": [
                    "JavaScript → JS → ECMAScript",
                    "Docker → Containerization",
                    "Kubernetes → K8s",
                    "Machine Learning → ML → AI"
                ],
                "results": synonym_matches,
                "benefit": "Finds candidates using different terminology for same skill"
            }
        except Exception as e:
            logger.warning(f"Synonym matching demo skipped: {e}")
            demo_results["synonym_matching"] = {
                "description": "Matches related terms and synonyms",
                "error": str(e),
                "results": []
            }

        # 3. Skill Aggregations
        try:
            if not self.elasticsearch.is_available():
                raise Exception("Elasticsearch not available")

            aggregations = await self.elasticsearch.get_skill_aggregations(user_id=user_id)
            demo_results["aggregations"] = {
                "description": "Analytics and statistics on skills, experience, education",
                "results": aggregations,
                "benefit": "Understand skill distribution and market trends"
            }
        except Exception as e:
            logger.warning(f"Aggregations demo skipped: {e}")
            demo_results["aggregations"] = {
                "description": "Analytics and statistics on skills, experience, education",
                "error": str(e),
                "results": {}
            }

        # 4. Multi-field Weighted Search
        demo_results["weighted_search"] = {
            "description": "Different fields have different importance weights",
            "configuration": {
                "skills": "3x weight (most important)",
                "cv_text": "2x weight",
                "job_titles": "1.5x weight"
            },
            "benefit": "Skills matches are prioritized over general CV text matches"
        }

        # 5. Highlighting
        demo_results["highlighting"] = {
            "description": "Shows exactly where matches were found",
            "benefit": "Quickly see which parts of CV match job requirements",
            "example": "Highlights 'Python' in CV when searching for Python developer"
        }

        return demo_results

    async def generate_comparison_report(
        self,
        user_id: str,
        job_description: str,
        required_skills: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive comparison report.

        Args:
            user_id: User ID
            job_description: Job description text
            required_skills: List of required skills

        Returns:
            Full comparison report
        """
        # Get search comparison
        search_comparison = await self.compare_search_performance(
            user_id=user_id,
            job_description=job_description,
            required_skills=required_skills
        )

        # Get advanced features demo
        advanced_features = await self.get_advanced_features_demo(
            user_id=user_id,
            required_skills=required_skills or []
        )

        # Build comprehensive report
        report = {
            "summary": {
                "chromadb_search_time_ms": search_comparison["chromadb"].get("search_time_ms", 0),
                "elasticsearch_search_time_ms": search_comparison["elasticsearch"].get("search_time_ms", 0),
                "performance_winner": search_comparison["performance_comparison"].get("faster_system", "Unknown"),
                "speedup_factor": search_comparison["performance_comparison"].get("speedup_factor", 0)
            },
            "search_comparison": search_comparison,
            "advanced_features": advanced_features,
            "recommendation": self._generate_recommendation(search_comparison, advanced_features)
        }

        return report

    def _generate_recommendation(
        self,
        search_comparison: Dict[str, Any],
        advanced_features: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate recommendation based on comparison results."""
        chromadb_time = search_comparison["chromadb"].get("search_time_ms", 0)
        es_time = search_comparison["elasticsearch"].get("search_time_ms", 0)

        if es_time < chromadb_time:
            speed_rec = f"Elasticsearch is {search_comparison['performance_comparison'].get('percentage_difference', 0)}% faster"
        else:
            speed_rec = "ChromaDB has competitive performance for simple queries"

        return {
            "performance": speed_rec,
            "features": "Elasticsearch provides fuzzy matching, synonyms, and advanced analytics that ChromaDB doesn't support",
            "use_case_chromadb": "Best for: Simple semantic search, small datasets, minimal setup",
            "use_case_elasticsearch": "Best for: Production job matching, typo tolerance, synonym support, analytics, large scale",
            "overall": "Elasticsearch is recommended for job matching due to fuzzy search and synonym support"
        }

    def close(self):
        """Close connections."""
        try:
            self.elasticsearch.close()
            logger.info("ElasticsearchComparisonService connections closed")
        except Exception as e:
            logger.error(f"Error closing connections: {e}")

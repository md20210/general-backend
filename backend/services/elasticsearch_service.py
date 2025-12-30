"""Elasticsearch Service for advanced search and comparison with ChromaDB."""
import logging
import time
from typing import Dict, Any, List, Optional
from elasticsearch import Elasticsearch, AsyncElasticsearch
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class ElasticsearchService:
    """Service for Elasticsearch operations and advanced search features."""

    def __init__(self):
        """Initialize Elasticsearch client."""
        self.client = None
        self.cv_index = "elastic_showcase_cv"
        self.job_index = "elastic_showcase_jobs"

        try:
            # Get Elasticsearch connection details from environment
            self.es_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
            self.es_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
            self.es_user = os.getenv("ELASTICSEARCH_USER", "elastic")
            self.es_password = os.getenv("ELASTICSEARCH_PASSWORD", "")
            self.es_use_ssl = os.getenv("ELASTICSEARCH_USE_SSL", "false").lower() == "true"

            # Build Elasticsearch URL with proper scheme
            scheme = "https" if self.es_use_ssl else "http"
            es_url = f"{scheme}://{self.es_host}:{self.es_port}"

            logger.info(f"Connecting to Elasticsearch at: {es_url}")

            # Initialize Elasticsearch client
            self.client = Elasticsearch(
                hosts=[es_url],
                basic_auth=(self.es_user, self.es_password) if self.es_password else None,
                verify_certs=self.es_use_ssl,
                ssl_show_warn=False,
            )

            # Initialize indices
            self._ensure_indices()
            logger.info("✅ ElasticsearchService initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️  Elasticsearch not available: {e}")
            logger.warning("Elasticsearch features will be disabled")
            self.client = None

    def is_available(self) -> bool:
        """Check if Elasticsearch is available."""
        return self.client is not None

    def _ensure_indices(self):
        """Create indices if they don't exist with optimized mappings."""
        if not self.is_available():
            return
        # CV Index - optimized for skills, experience, education
        cv_mapping = {
            "mappings": {
                "properties": {
                    "user_id": {"type": "keyword"},
                    "cv_text": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "english": {"type": "text", "analyzer": "english"}
                        }
                    },
                    "skills": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "experience_years": {"type": "integer"},
                    "education_level": {"type": "keyword"},
                    "job_titles": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "homepage_url": {"type": "keyword"},
                    "linkedin_url": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "skill_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "synonym_filter"]
                        }
                    },
                    "filter": {
                        "synonym_filter": {
                            "type": "synonym",
                            "synonyms": [
                                "python, py",
                                "javascript, js, ecmascript",
                                "typescript, ts",
                                "react, reactjs",
                                "vue, vuejs",
                                "angular, angularjs",
                                "node, nodejs, node.js",
                                "docker, containerization",
                                "kubernetes, k8s",
                                "aws, amazon web services",
                                "gcp, google cloud platform",
                                "azure, microsoft azure",
                                "sql, structured query language",
                                "nosql, mongodb, cassandra",
                                "ci/cd, continuous integration, continuous deployment",
                                "ml, machine learning, ai, artificial intelligence",
                                "devops, dev ops"
                            ]
                        }
                    }
                }
            }
        }

        # Job Index - optimized for job descriptions and requirements
        job_mapping = {
            "mappings": {
                "properties": {
                    "user_id": {"type": "keyword"},
                    "job_description": {
                        "type": "text",
                        "analyzer": "english",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "required_skills": {
                        "type": "text",
                        "analyzer": "skill_analyzer",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "job_url": {"type": "keyword"},
                    "created_at": {"type": "date"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }

        try:
            # Create CV index
            if not self.client.indices.exists(index=self.cv_index):
                self.client.indices.create(index=self.cv_index, body=cv_mapping)
                logger.info(f"Created index: {self.cv_index}")

            # Create Job index
            if not self.client.indices.exists(index=self.job_index):
                self.client.indices.create(index=self.job_index, body=job_mapping)
                logger.info(f"Created index: {self.job_index}")
        except Exception as e:
            logger.warning(f"Error creating indices (may already exist): {e}")

    async def index_cv_data(
        self,
        user_id: str,
        cv_text: str,
        skills: List[str],
        experience_years: Optional[int] = None,
        education_level: Optional[str] = None,
        job_titles: Optional[List[str]] = None,
        homepage_url: Optional[str] = None,
        linkedin_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Index CV data into Elasticsearch.

        Args:
            user_id: Unique user identifier
            cv_text: Full CV text
            skills: List of extracted skills
            experience_years: Years of experience
            education_level: Education level
            job_titles: List of previous job titles
            homepage_url: Personal homepage URL
            linkedin_url: LinkedIn profile URL

        Returns:
            Indexing result with document ID
        """
        doc = {
            "user_id": user_id,
            "cv_text": cv_text,
            "skills": " ".join(skills) if skills else "",
            "experience_years": experience_years,
            "education_level": education_level,
            "job_titles": " ".join(job_titles) if job_titles else "",
            "homepage_url": homepage_url,
            "linkedin_url": linkedin_url,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        try:
            # Use user_id as document ID to enable updates
            result = self.client.index(
                index=self.cv_index,
                id=user_id,
                document=doc
            )
            logger.info(f"Indexed CV for user {user_id}: {result['result']}")
            return {"status": "success", "result": result["result"], "id": user_id}
        except Exception as e:
            logger.error(f"Error indexing CV for user {user_id}: {e}")
            raise

    async def search_cv_match(
        self,
        job_description: str,
        required_skills: Optional[List[str]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for CV matches using advanced Elasticsearch features.

        Args:
            job_description: Job description text
            required_skills: List of required skills
            user_id: Optional user ID to search specific user's CV

        Returns:
            Search results with timing and match details
        """
        start_time = time.time()

        # Build multi-field query with weights
        must_clauses = []
        should_clauses = []

        # Filter by user if specified
        if user_id:
            must_clauses.append({"term": {"user_id": user_id}})

        # Match against job description (weighted)
        should_clauses.append({
            "multi_match": {
                "query": job_description,
                "fields": ["cv_text^2", "skills^3", "job_titles^1.5"],
                "type": "best_fields",
                "fuzziness": "AUTO"
            }
        })

        # Match required skills with fuzzy matching
        if required_skills:
            for skill in required_skills:
                should_clauses.append({
                    "match": {
                        "skills": {
                            "query": skill,
                            "fuzziness": "AUTO",
                            "boost": 2.0
                        }
                    }
                })

        query = {
            "query": {
                "bool": {
                    "must": must_clauses if must_clauses else [{"match_all": {}}],
                    "should": should_clauses,
                    "minimum_should_match": 1 if should_clauses else 0
                }
            },
            "highlight": {
                "fields": {
                    "cv_text": {},
                    "skills": {},
                    "job_titles": {}
                }
            },
            "size": 10
        }

        try:
            result = self.client.search(index=self.cv_index, body=query)
            search_time_ms = (time.time() - start_time) * 1000

            hits = result["hits"]["hits"]
            total_matches = result["hits"]["total"]["value"]

            # Extract matches and highlights
            matches = []
            for hit in hits:
                match_data = {
                    "user_id": hit["_source"]["user_id"],
                    "score": hit["_score"],
                    "highlights": hit.get("highlight", {}),
                    "skills": hit["_source"].get("skills", ""),
                    "experience_years": hit["_source"].get("experience_years"),
                    "education_level": hit["_source"].get("education_level")
                }
                matches.append(match_data)

            return {
                "search_time_ms": search_time_ms,
                "total_matches": total_matches,
                "matches": matches,
                "max_score": result["hits"]["max_score"]
            }
        except Exception as e:
            logger.error(f"Error searching CV: {e}")
            raise

    async def get_fuzzy_matches(
        self,
        skills: List[str],
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Find fuzzy matches for skills (handles typos).

        Args:
            skills: List of skills to search for
            user_id: User ID to search

        Returns:
            List of fuzzy matches with edit distance
        """
        fuzzy_results = []

        for skill in skills:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"user_id": user_id}},
                            {"match": {
                                "skills": {
                                    "query": skill,
                                    "fuzziness": "AUTO"
                                }
                            }}
                        ]
                    }
                },
                "highlight": {
                    "fields": {"skills": {}}
                }
            }

            try:
                result = self.client.search(index=self.cv_index, body=query)
                if result["hits"]["total"]["value"] > 0:
                    hit = result["hits"]["hits"][0]
                    fuzzy_results.append({
                        "searched_skill": skill,
                        "matched_text": hit.get("highlight", {}).get("skills", []),
                        "score": hit["_score"]
                    })
            except Exception as e:
                logger.error(f"Error in fuzzy search for skill '{skill}': {e}")

        return fuzzy_results

    async def get_synonym_matches(
        self,
        skills: List[str],
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Find synonym matches using Elasticsearch synonym filter.

        Args:
            skills: List of skills to search for
            user_id: User ID to search

        Returns:
            List of synonym matches
        """
        synonym_results = []

        for skill in skills:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"user_id": user_id}},
                            {"match": {
                                "skills": {
                                    "query": skill,
                                    "analyzer": "skill_analyzer"
                                }
                            }}
                        ]
                    }
                }
            }

            try:
                result = self.client.search(index=self.cv_index, body=query)
                if result["hits"]["total"]["value"] > 0:
                    hit = result["hits"]["hits"][0]
                    synonym_results.append({
                        "searched_skill": skill,
                        "score": hit["_score"],
                        "cv_skills": hit["_source"].get("skills", "")
                    })
            except Exception as e:
                logger.error(f"Error in synonym search for skill '{skill}': {e}")

        return synonym_results

    async def get_skill_aggregations(
        self,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get skill aggregations and clusters.

        Args:
            user_id: Optional user ID filter

        Returns:
            Aggregation results with skill clusters
        """
        query = {
            "query": {
                "term": {"user_id": user_id}
            } if user_id else {"match_all": {}},
            "aggs": {
                "skill_terms": {
                    "terms": {
                        "field": "skills.keyword",
                        "size": 50
                    }
                },
                "avg_experience": {
                    "avg": {
                        "field": "experience_years"
                    }
                },
                "education_breakdown": {
                    "terms": {
                        "field": "education_level"
                    }
                }
            },
            "size": 0
        }

        try:
            result = self.client.search(index=self.cv_index, body=query)
            return {
                "skill_clusters": result["aggregations"]["skill_terms"]["buckets"],
                "avg_experience": result["aggregations"]["avg_experience"]["value"],
                "education_breakdown": result["aggregations"]["education_breakdown"]["buckets"]
            }
        except Exception as e:
            logger.error(f"Error getting skill aggregations: {e}")
            return {}

    def close(self):
        """Close Elasticsearch connection."""
        try:
            self.client.close()
            logger.info("Elasticsearch connection closed")
        except Exception as e:
            logger.error(f"Error closing Elasticsearch connection: {e}")

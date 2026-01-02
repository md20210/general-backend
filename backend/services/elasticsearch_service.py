"""Elasticsearch Service for advanced search and comparison with ChromaDB."""
import logging
import time
from typing import Dict, Any, List, Optional
from elasticsearch import Elasticsearch, AsyncElasticsearch
from datetime import datetime
import os
from backend.services.llm_gateway import LLMGateway

logger = logging.getLogger(__name__)


class ElasticsearchService:
    """Service for Elasticsearch operations and advanced search features."""

    def __init__(self):
        """Initialize Elasticsearch client."""
        self.client = None
        self.cv_index = "elastic_showcase_cv"
        self.job_index = "elastic_showcase_jobs"
        self.llm_gateway = LLMGateway()  # For generating embeddings

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
                    "chunk_index": {"type": "integer"},
                    "databases": {"type": "keyword"},
                    "programming_languages": {"type": "keyword"},
                    "companies": {"type": "keyword"},
                    "certifications": {"type": "keyword"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 768,
                        "index": True,
                        "similarity": "cosine"
                    },
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

    def _extract_structured_fields(self, text: str) -> Dict[str, List[str]]:
        """Extract structured fields from CV text using keyword matching."""
        text_lower = text.lower()

        # Database keywords
        database_keywords = {
            "postgresql": ["postgresql", "postgres", "psql"],
            "elasticsearch": ["elasticsearch", "elastic", "es cluster"],
            "chromadb": ["chromadb", "chroma"],
            "pgvector": ["pgvector", "pg_vector"],
            "mongodb": ["mongodb", "mongo"],
            "redis": ["redis"],
            "mysql": ["mysql"],
            "oracle": ["oracle database", "oracle"],
            "mssql": ["sql server", "mssql", "microsoft sql"],
            "cassandra": ["cassandra"],
            "dynamodb": ["dynamodb", "dynamo"],
            "neo4j": ["neo4j"],
            "sqlite": ["sqlite"]
        }

        # Programming language keywords
        language_keywords = {
            "python": ["python", "py3", "python3"],
            "javascript": ["javascript", "js", "node.js", "nodejs"],
            "typescript": ["typescript", "ts"],
            "java": ["java", " java "],  # Space to avoid matching javascript
            "go": ["golang", " go "],
            "rust": ["rust"],
            "c++": ["c++", "cpp"],
            "c#": ["c#", "csharp"],
            "php": ["php"],
            "ruby": ["ruby"],
            "swift": ["swift"],
            "kotlin": ["kotlin"],
            "scala": ["scala"],
            "r": [" r "],
            "sql": ["sql", "t-sql", "pl/sql"]
        }

        # Company keywords
        company_keywords = {
            "cognizant": ["cognizant"],
            "deutsche telekom": ["deutsche telekom", "telekom"],
            "sap": ["sap"],
            "mercedes-benz": ["mercedes-benz", "mercedes", "daimler"],
            "google": ["google"],
            "microsoft": ["microsoft"],
            "amazon": ["amazon", "aws"],
            "ibm": ["ibm"]
        }

        # Certification keywords
        certification_keywords = {
            "togaf": ["togaf"],
            "aws certified": ["aws certified", "aws certification"],
            "azure certified": ["azure certified"],
            "gcp certified": ["gcp certified"],
            "cissp": ["cissp"],
            "pmp": ["pmp"],
            "scrum master": ["scrum master", "csm"],
            "enterprise architect": ["enterprise architect certified"]
        }

        def extract_matches(keywords_dict):
            """Extract matching keywords from text."""
            found = []
            for name, patterns in keywords_dict.items():
                if any(pattern in text_lower for pattern in patterns):
                    found.append(name)
            return found

        return {
            "databases": extract_matches(database_keywords),
            "programming_languages": extract_matches(language_keywords),
            "companies": extract_matches(company_keywords),
            "certifications": extract_matches(certification_keywords)
        }

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
        Index CV data into Elasticsearch as chunked documents.

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
        try:
            # First, delete any existing chunks for this user
            delete_query = {"query": {"term": {"user_id": user_id}}}
            try:
                self.client.delete_by_query(index=self.cv_index, body=delete_query)
                logger.info(f"Deleted existing CV chunks for user {user_id}")
            except Exception as del_err:
                logger.warning(f"No existing chunks to delete for user {user_id}: {del_err}")

            # Chunk the CV text into smaller pieces (similar to pgvector)
            chunk_size = 800  # characters per chunk (increased for better semantic context)
            overlap = 150     # overlap between chunks for context continuity

            chunks = []
            start = 0
            chunk_index = 0

            while start < len(cv_text):
                end = start + chunk_size
                chunk_text = cv_text[start:end]

                # Try to break at sentence boundary if possible
                if end < len(cv_text):
                    last_period = chunk_text.rfind('.')
                    last_newline = chunk_text.rfind('\n')
                    break_point = max(last_period, last_newline)
                    if break_point > chunk_size * 0.7:  # Only break if we're at least 70% through
                        chunk_text = chunk_text[:break_point + 1]
                        end = start + break_point + 1

                chunks.append({
                    "text": chunk_text.strip(),
                    "index": chunk_index
                })

                # Move start position with overlap
                start = end - overlap
                chunk_index += 1

            logger.info(f"Split CV into {len(chunks)} chunks for user {user_id}")

            # Extract structured fields from full CV text (once for all chunks)
            structured_fields = self._extract_structured_fields(cv_text)
            logger.info(f"Extracted structured fields: "
                       f"databases={len(structured_fields['databases'])}, "
                       f"languages={len(structured_fields['programming_languages'])}, "
                       f"companies={len(structured_fields['companies'])}")

            # Index each chunk as a separate document
            indexed_count = 0
            skills_str = " ".join(skills) if skills else ""
            job_titles_str = " ".join(job_titles) if job_titles else ""

            for chunk in chunks:
                # Generate embedding for this chunk using Ollama
                try:
                    chunk_embedding = self.llm_gateway.embed(chunk["text"], model="nomic-embed-text")
                    logger.info(f"Generated embedding for chunk {chunk['index']}, dims: {len(chunk_embedding)}")
                except Exception as embed_err:
                    logger.error(f"Failed to generate embedding for chunk {chunk['index']}: {embed_err}")
                    # Continue without embedding rather than failing the entire indexing
                    chunk_embedding = None

                doc = {
                    "user_id": user_id,
                    "cv_text": chunk["text"],
                    "chunk_index": chunk["index"],
                    "skills": skills_str,
                    "experience_years": experience_years,
                    "education_level": education_level,
                    "job_titles": job_titles_str,
                    "homepage_url": homepage_url,
                    "linkedin_url": linkedin_url,
                    "databases": structured_fields["databases"],
                    "programming_languages": structured_fields["programming_languages"],
                    "companies": structured_fields["companies"],
                    "certifications": structured_fields["certifications"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }

                # Add embedding if generated successfully
                if chunk_embedding:
                    doc["embedding"] = chunk_embedding

                # Use user_id + chunk_index as document ID
                doc_id = f"{user_id}_chunk_{chunk['index']}"
                result = self.client.index(
                    index=self.cv_index,
                    id=doc_id,
                    document=doc
                )
                indexed_count += 1

            logger.info(f"Successfully indexed {indexed_count} CV chunks for user {user_id}")
            return {
                "status": "success",
                "result": "created",
                "chunks_indexed": indexed_count,
                "id": user_id
            }
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

    async def phrase_search(
        self,
        phrase: str,
        user_id: Optional[str] = None,
        slop: int = 2
    ) -> Dict[str, Any]:
        """
        Phrase matching - find exact phrases with configurable slop.

        Args:
            phrase: Exact phrase to search for
            user_id: Optional user ID filter
            slop: Number of positions tokens can be apart (default: 2)

        Returns:
            Phrase match results
        """
        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_phrase": {
                                "cv_text": {
                                    "query": phrase,
                                    "slop": slop
                                }
                            }
                        }
                    ],
                    "filter": [{"term": {"user_id": user_id}}] if user_id else []
                }
            },
            "highlight": {
                "fields": {"cv_text": {"fragment_size": 150}}
            }
        }

        try:
            result = self.client.search(index=self.cv_index, body=query)
            return {
                "total_matches": result["hits"]["total"]["value"],
                "matches": [
                    {
                        "score": hit["_score"],
                        "highlights": hit.get("highlight", {}).get("cv_text", [])
                    }
                    for hit in result["hits"]["hits"]
                ]
            }
        except Exception as e:
            logger.error(f"Phrase search error: {e}")
            return {"total_matches": 0, "matches": []}

    async def wildcard_search(
        self,
        pattern: str,
        field: str = "skills",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Wildcard search - pattern matching with * and ?.

        Args:
            pattern: Wildcard pattern (e.g., "Java*", "Pyth?n")
            field: Field to search in
            user_id: Optional user ID filter

        Returns:
            Wildcard match results
        """
        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "wildcard": {
                                field: {
                                    "value": pattern.lower(),
                                    "case_insensitive": True
                                }
                            }
                        }
                    ],
                    "filter": [{"term": {"user_id": user_id}}] if user_id else []
                }
            }
        }

        try:
            result = self.client.search(index=self.cv_index, body=query)
            return {
                "total_matches": result["hits"]["total"]["value"],
                "matches": [
                    {
                        "user_id": hit["_source"]["user_id"],
                        "matched_field": hit["_source"].get(field, "")
                    }
                    for hit in result["hits"]["hits"]
                ]
            }
        except Exception as e:
            logger.error(f"Wildcard search error: {e}")
            return {"total_matches": 0, "matches": []}

    async def get_advanced_aggregations(
        self,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Advanced aggregations with experience buckets and skill co-occurrence.

        Args:
            user_id: Optional user ID filter

        Returns:
            Advanced aggregation results
        """
        query = {
            "query": {
                "term": {"user_id": user_id}
            } if user_id else {"match_all": {}},
            "aggs": {
                # Experience level buckets
                "experience_levels": {
                    "range": {
                        "field": "experience_years",
                        "ranges": [
                            {"key": "Junior", "to": 2},
                            {"key": "Mid-Level", "from": 2, "to": 5},
                            {"key": "Senior", "from": 5, "to": 10},
                            {"key": "Expert", "from": 10}
                        ]
                    }
                },
                # Education breakdown
                "education_distribution": {
                    "terms": {
                        "field": "education_level",
                        "size": 10
                    }
                },
                # Top skills
                "top_skills": {
                    "terms": {
                        "field": "skills.keyword",
                        "size": 50
                    }
                },
                # Average experience
                "stats_experience": {
                    "stats": {
                        "field": "experience_years"
                    }
                },
                # Skills per experience level
                "skills_by_experience": {
                    "range": {
                        "field": "experience_years",
                        "ranges": [
                            {"key": "0-2 years", "to": 2},
                            {"key": "2-5 years", "from": 2, "to": 5},
                            {"key": "5+ years", "from": 5}
                        ]
                    },
                    "aggs": {
                        "skills": {
                            "terms": {
                                "field": "skills.keyword",
                                "size": 20
                            }
                        }
                    }
                }
            },
            "size": 0
        }

        try:
            result = self.client.search(index=self.cv_index, body=query)
            aggs = result["aggregations"]

            return {
                "experience_levels": aggs["experience_levels"]["buckets"],
                "education_distribution": aggs["education_distribution"]["buckets"],
                "top_skills": aggs["top_skills"]["buckets"],
                "experience_stats": aggs["stats_experience"],
                "skills_by_experience": [
                    {
                        "experience_range": bucket["key"],
                        "candidate_count": bucket["doc_count"],
                        "top_skills": bucket["skills"]["buckets"]
                    }
                    for bucket in aggs["skills_by_experience"]["buckets"]
                ]
            }
        except Exception as e:
            logger.error(f"Advanced aggregations error: {e}")
            return {}

    async def explain_match(
        self,
        user_id: str,
        job_description: str,
        required_skills: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Use Explain API to show why a match scored the way it did.

        Args:
            user_id: User ID to explain
            job_description: Job description text
            required_skills: Required skills

        Returns:
            Explanation of match scoring
        """
        # Build the same query as search_cv_match
        should_clauses = [
            {
                "multi_match": {
                    "query": job_description,
                    "fields": ["cv_text^2", "skills^3", "job_titles^1.5"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            }
        ]

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
                    "must": [{"term": {"user_id": user_id}}],
                    "should": should_clauses,
                    "minimum_should_match": 1
                }
            }
        }

        try:
            # Use explain API
            explanation = self.client.explain(
                index=self.cv_index,
                id=user_id,
                body=query
            )

            return {
                "matched": explanation.get("matched", False),
                "score": explanation.get("explanation", {}).get("value", 0),
                "explanation": self._format_explanation(explanation.get("explanation", {}))
            }
        except Exception as e:
            logger.error(f"Explain match error: {e}")
            return {"matched": False, "error": str(e)}

    def _format_explanation(self, explanation: Dict[str, Any]) -> Dict[str, Any]:
        """Format explanation tree into readable structure."""
        if not explanation:
            return {}

        formatted = {
            "value": explanation.get("value", 0),
            "description": explanation.get("description", ""),
        }

        # Recursively format details
        if "details" in explanation and explanation["details"]:
            formatted["breakdown"] = [
                self._format_explanation(detail)
                for detail in explanation["details"]
            ]

        return formatted

    async def get_search_suggestions(
        self,
        prefix: str,
        field: str = "skills",
        size: int = 10
    ) -> List[str]:
        """
        Get autocomplete suggestions for search.

        Args:
            prefix: Text prefix for suggestions
            field: Field to get suggestions from
            size: Maximum number of suggestions

        Returns:
            List of suggested terms
        """
        query = {
            "suggest": {
                "skill_suggest": {
                    "prefix": prefix,
                    "completion": {
                        "field": f"{field}.keyword",
                        "size": size,
                        "skip_duplicates": True
                    }
                }
            }
        }

        try:
            result = self.client.search(index=self.cv_index, body=query)
            suggestions = result.get("suggest", {}).get("skill_suggest", [])

            if suggestions:
                options = suggestions[0].get("options", [])
                return [opt["text"] for opt in options]
            return []
        except Exception as e:
            logger.error(f"Search suggestions error: {e}")
            return []

    async def multi_index_search(
        self,
        query_text: str,
        indices: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search across multiple indices simultaneously.

        Args:
            query_text: Search query
            indices: List of indices to search (default: cv and job indices)

        Returns:
            Combined search results from all indices
        """
        if indices is None:
            indices = [self.cv_index, self.job_index]

        query = {
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": ["*"],
                    "type": "best_fields"
                }
            },
            "size": 5
        }

        try:
            result = self.client.search(index=indices, body=query)

            return {
                "total_matches": result["hits"]["total"]["value"],
                "matches_by_index": self._group_by_index(result["hits"]["hits"]),
                "search_time_ms": result.get("took", 0)
            }
        except Exception as e:
            logger.error(f"Multi-index search error: {e}")
            return {"total_matches": 0, "matches_by_index": {}}

    def _group_by_index(self, hits: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group search hits by index."""
        grouped = {}
        for hit in hits:
            index = hit["_index"]
            if index not in grouped:
                grouped[index] = []
            grouped[index].append({
                "id": hit["_id"],
                "score": hit["_score"],
                "source": hit["_source"]
            })
        return grouped

    async def hybrid_search(self, query: str, user_id: str, top_k: int = 3) -> list:
        """
        Optimized hybrid search with weighted Vector (70%) + BM25 (30%) combination.

        This method demonstrates advanced Elasticsearch capabilities:
        1. Semantic Vector Search (kNN) - 70% weight (dominant for natural language)
        2. BM25 keyword search - 30% weight (precision for exact terms)
        3. Separate BM25 and Vector queries with manual score normalization
        4. Field boosting optimized for CV data
        5. Reduced BM25 noise through focused field selection

        Args:
            query: Search query
            user_id: User ID to filter documents
            top_k: Number of top results to return

        Returns:
            List of search results with text, source, and weighted combined score
        """
        try:
            if not self.is_available():
                logger.warning("Elasticsearch not available for hybrid search")
                return []

            # Generate query embedding for kNN search
            try:
                query_embedding = self.llm_gateway.embed(query, model="nomic-embed-text")
                logger.info(f"Generated query embedding, dims: {len(query_embedding)}")
            except Exception as embed_err:
                logger.error(f"Failed to generate query embedding: {embed_err}")
                # Fall back to BM25-only if embedding fails
                query_embedding = None

            if not query_embedding:
                # BM25-only fallback
                logger.info(f"🔍 Elasticsearch BM25-only search (kNN unavailable): user_id={user_id}, query='{query}'")
                search_body = {
                    "size": top_k,
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "multi_match": {
                                        "query": query,
                                        "fields": [
                                            "cv_text",
                                            "skills^2",
                                            "databases^3",
                                            "programming_languages^2",
                                            "companies^1.5"
                                        ],
                                        "fuzziness": "AUTO"
                                    }
                                }
                            ],
                            "filter": [{"term": {"user_id": user_id}}]
                        }
                    },
                    "_source": ["cv_text", "skills", "experience_years", "job_titles", "user_id",
                               "databases", "programming_languages", "companies", "certifications", "chunk_index"]
                }
                response = self.client.search(index=self.cv_index, body=search_body)
                logger.info(f"📊 BM25-only returned {response['hits']['total']['value']} hits")
            else:
                # OPTIMIZED HYBRID: 70% Vector + 30% BM25
                # Strategy: Run both searches separately, then combine with weights

                # Step 1: Vector Search (kNN) - Higher candidate pool for better recall
                logger.info(f"🔍 Running Vector Search (70% weight)...")
                vector_search = {
                    "size": top_k * 5,  # Get more candidates for merging
                    "knn": {
                        "field": "embedding",
                        "query_vector": query_embedding,
                        "k": top_k * 5,
                        "num_candidates": 100,  # Large candidate pool for precision
                        "filter": [{"term": {"user_id": user_id}}]
                    },
                    "_source": ["cv_text", "skills", "experience_years", "job_titles", "user_id",
                               "databases", "programming_languages", "companies", "certifications", "chunk_index"]
                }

                # Step 2: BM25 Search - Focused fields to reduce noise
                logger.info(f"🔍 Running BM25 Search (30% weight)...")
                bm25_search = {
                    "size": top_k * 5,
                    "query": {
                        "bool": {
                            "should": [
                                # Focused on important structured fields only
                                {
                                    "multi_match": {
                                        "query": query,
                                        "fields": [
                                            "skills^3",        # High boost for exact skill matches
                                            "databases^4",      # Highest for database names
                                            "programming_languages^3",
                                            "companies^2",
                                            "job_titles^2"
                                        ],
                                        "type": "best_fields",  # Best field wins (less noise than cross_fields)
                                        "fuzziness": "AUTO"
                                    }
                                },
                                # Secondary: cv_text for general context
                                {
                                    "match": {
                                        "cv_text": {
                                            "query": query,
                                            "boost": 0.5  # Lower boost to avoid overwhelming structured fields
                                        }
                                    }
                                }
                            ],
                            "filter": [{"term": {"user_id": user_id}}]
                        }
                    },
                    "_source": ["cv_text", "skills", "experience_years", "job_titles", "user_id",
                               "databases", "programming_languages", "companies", "certifications", "chunk_index"]
                }

                # Execute both searches
                vector_response = self.client.search(index=self.cv_index, body=vector_search)
                bm25_response = self.client.search(index=self.cv_index, body=bm25_search)

                # Step 3: Merge results with weighted scoring (70% Vector + 30% BM25)
                vector_results = {}
                bm25_results = {}

                # Normalize vector scores
                max_vector_score = max([hit['_score'] for hit in vector_response['hits']['hits']], default=1.0)
                for hit in vector_response['hits']['hits']:
                    doc_id = hit['_id']
                    normalized_score = hit['_score'] / max_vector_score if max_vector_score > 0 else 0
                    vector_results[doc_id] = {
                        'score': normalized_score,
                        'doc': hit
                    }

                # Normalize BM25 scores
                max_bm25_score = max([hit['_score'] for hit in bm25_response['hits']['hits']], default=1.0)
                for hit in bm25_response['hits']['hits']:
                    doc_id = hit['_id']
                    normalized_score = hit['_score'] / max_bm25_score if max_bm25_score > 0 else 0
                    bm25_results[doc_id] = {
                        'score': normalized_score,
                        'doc': hit
                    }

                # Combine with weights: 70% Vector + 30% BM25
                VECTOR_WEIGHT = 0.7
                BM25_WEIGHT = 0.3

                combined_results = {}
                all_doc_ids = set(vector_results.keys()) | set(bm25_results.keys())

                for doc_id in all_doc_ids:
                    vector_score = vector_results.get(doc_id, {}).get('score', 0.0)
                    bm25_score = bm25_results.get(doc_id, {}).get('score', 0.0)

                    combined_score = (VECTOR_WEIGHT * vector_score) + (BM25_WEIGHT * bm25_score)

                    # Get the document (prefer vector result if both exist)
                    doc = vector_results.get(doc_id, bm25_results.get(doc_id))['doc']

                    combined_results[doc_id] = {
                        'score': combined_score,
                        'vector_score': vector_score,
                        'bm25_score': bm25_score,
                        'doc': doc
                    }

                # Sort by combined score and take top_k
                sorted_results = sorted(
                    combined_results.values(),
                    key=lambda x: x['score'],
                    reverse=True
                )[:top_k]

                # Reconstruct response in Elasticsearch format
                response = {
                    'hits': {
                        'total': {'value': len(sorted_results)},
                        'hits': [r['doc'] for r in sorted_results]
                    }
                }

                logger.info(f"📊 Hybrid Search: Vector={len(vector_results)}, BM25={len(bm25_results)}, Combined={len(sorted_results)}")
                logger.info(f"💡 Weights: {VECTOR_WEIGHT*100}% Vector + {BM25_WEIGHT*100}% BM25")

            # Parse results
            results = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                text = source.get("cv_text", "").strip()

                # Each document is already a focused chunk, no need for sentence extraction
                results.append({
                    "text": text,
                    "content": text,  # Add 'content' field for consistency with compare-query expectations
                    "source": f"cv.pdf (chunk {source.get('chunk_index', 0)})",
                    "score": hit["_score"] / 10,  # Normalize score to 0-1 range
                    "metadata": {
                        "skills": source.get("skills", ""),
                        "experience": source.get("experience_years"),
                        "job_titles": source.get("job_titles", ""),
                        "databases": source.get("databases", []),
                        "programming_languages": source.get("programming_languages", []),
                        "companies": source.get("companies", []),
                        "certifications": source.get("certifications", []),
                        "chunk_index": source.get("chunk_index", 0)
                    }
                })

            logger.info(f"Hybrid search returned {len(results)} results for query: {query}")
            return results

        except Exception as e:
            logger.error(f"Error in hybrid search: {e}", exc_info=True)
            return []

    async def delete_user_cv_data(self, user_id: str):
        """
        Delete all CV data for a specific user from Elasticsearch.

        Args:
            user_id: User ID whose data should be deleted
        """
        try:
            if not self.is_available():
                logger.warning("Elasticsearch not available for deletion")
                return

            # Delete from CV index
            delete_query = {
                "query": {
                    "term": {
                        "user_id": user_id
                    }
                }
            }

            response = self.client.delete_by_query(
                index=self.cv_index,
                body=delete_query
            )

            deleted_count = response.get('deleted', 0)
            logger.info(f"Deleted {deleted_count} CV documents for user {user_id} from Elasticsearch")

        except Exception as e:
            logger.error(f"Error deleting user CV data from Elasticsearch: {e}", exc_info=True)
            raise

    def close(self):
        """Close Elasticsearch connection."""
        try:
            self.client.close()
            logger.info("Elasticsearch connection closed")
        except Exception as e:
            logger.error(f"Error closing Elasticsearch connection: {e}")

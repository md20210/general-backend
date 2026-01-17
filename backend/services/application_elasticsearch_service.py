"""
Elasticsearch Service for Application Tracker
Handles document indexing and hybrid search for job applications
"""
from typing import List, Dict, Any, Optional
from elasticsearch import Elasticsearch
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


class ApplicationElasticsearchService:
    """Service for Elasticsearch operations for Application Tracker"""

    def __init__(self):
        """Initialize Elasticsearch client"""
        self.es = None
        self.index_name = "application_tracker_documents"
        self._connect()

    def _connect(self):
        """Connect to Elasticsearch"""
        try:
            # Build Elasticsearch URL
            protocol = "https" if settings.ELASTICSEARCH_USE_SSL == "true" else "http"
            es_url = f"{protocol}://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}"

            self.es = Elasticsearch(
                [es_url],
                basic_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD) if settings.ELASTICSEARCH_PASSWORD else None,
                verify_certs=False if settings.ELASTICSEARCH_USE_SSL == "true" else None,
            )

            # Test connection
            if self.es.ping():
                logger.info(f"✅ Application Tracker: Connected to Elasticsearch at {es_url}")
            else:
                logger.warning(f"⚠️ Application Tracker: Elasticsearch ping failed at {es_url}")
        except Exception as e:
            logger.error(f"❌ Application Tracker: Failed to connect to Elasticsearch: {e}")
            self.es = None

    def create_index(self):
        """Create index for application documents with optimized search"""
        if not self.es:
            logger.error("Elasticsearch not connected")
            return False

        # Index mapping optimized for job application documents
        mapping = {
            "mappings": {
                "properties": {
                    "document_id": {"type": "integer"},  # ApplicationDocument.id
                    "application_id": {"type": "integer"},
                    "user_id": {"type": "keyword"},
                    "company_name": {"type": "text", "analyzer": "standard"},
                    "position": {"type": "text", "analyzer": "standard"},
                    "filename": {"type": "keyword"},
                    "file_path": {"type": "keyword"},
                    "doc_type": {"type": "keyword"},  # cv, cover_letter, certificate, etc.
                    "content": {
                        "type": "text",
                        "analyzer": "standard",
                        "term_vector": "with_positions_offsets"  # For highlighting
                    },
                    "created_at": {"type": "date"},
                    "indexed_at": {"type": "date"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "standard": {
                            "type": "standard",
                            "stopwords": "_english_"
                        }
                    }
                }
            }
        }

        try:
            if self.es.indices.exists(index=self.index_name):
                logger.info(f"Index {self.index_name} already exists")
                return True

            self.es.indices.create(index=self.index_name, body=mapping)
            logger.info(f"✅ Created index: {self.index_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create index: {e}")
            return False

    def index_document(self, document_id: int, application_id: int, user_id: str,
                      company_name: str, position: Optional[str], filename: str,
                      file_path: str, doc_type: str, content: str, created_at: str) -> bool:
        """Index a single application document"""
        if not self.es:
            logger.warning("Elasticsearch not connected, skipping indexing")
            return False

        try:
            doc = {
                "document_id": document_id,
                "application_id": application_id,
                "user_id": str(user_id),
                "company_name": company_name,
                "position": position or "",
                "filename": filename,
                "file_path": file_path,
                "doc_type": doc_type,
                "content": content,
                "created_at": created_at,
                "indexed_at": "now"
            }

            self.es.index(index=self.index_name, id=document_id, document=doc)
            logger.debug(f"✅ Indexed document {document_id} for {company_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to index document {document_id}: {e}")
            return False

    def search(self, query: str, user_id: str, company_filter: Optional[str] = None,
              doc_type_filter: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search application documents with filters

        Args:
            query: Search query
            user_id: Filter by user
            company_filter: Optional company name filter
            doc_type_filter: Optional document type filter (cv, cover_letter, etc.)
            limit: Maximum results to return

        Returns:
            List of matching documents with scores
        """
        if not self.es:
            logger.warning("Elasticsearch not connected, returning empty results")
            return []

        try:
            # Build query
            must_clauses = [
                {"term": {"user_id": str(user_id)}},
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["content^2", "company_name^1.5", "position", "filename"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                }
            ]

            if company_filter:
                must_clauses.append({"match": {"company_name": company_filter}})

            if doc_type_filter:
                must_clauses.append({"term": {"doc_type": doc_type_filter}})

            search_query = {
                "query": {
                    "bool": {
                        "must": must_clauses
                    }
                },
                "size": limit,
                "highlight": {
                    "fields": {
                        "content": {
                            "fragment_size": 150,
                            "number_of_fragments": 3
                        }
                    }
                }
            }

            response = self.es.search(index=self.index_name, body=search_query)

            # Format results
            results = []
            for hit in response["hits"]["hits"]:
                results.append({
                    "document_id": hit["_source"]["document_id"],
                    "application_id": hit["_source"]["application_id"],
                    "company_name": hit["_source"]["company_name"],
                    "position": hit["_source"]["position"],
                    "filename": hit["_source"]["filename"],
                    "doc_type": hit["_source"]["doc_type"],
                    "content": hit["_source"]["content"],
                    "score": hit["_score"],
                    "highlights": hit.get("highlight", {}).get("content", [])
                })

            logger.info(f"📊 Elasticsearch found {len(results)} results for query: {query[:50]}...")
            return results

        except Exception as e:
            logger.error(f"❌ Elasticsearch search failed: {e}")
            return []

    def delete_document(self, document_id: int) -> bool:
        """Delete a document from the index"""
        if not self.es:
            return False

        try:
            self.es.delete(index=self.index_name, id=document_id)
            logger.debug(f"🗑️ Deleted document {document_id} from Elasticsearch")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete document {document_id}: {e}")
            return False

    def delete_by_application(self, application_id: int) -> int:
        """Delete all documents for an application"""
        if not self.es:
            return 0

        try:
            query = {
                "query": {
                    "term": {"application_id": application_id}
                }
            }
            response = self.es.delete_by_query(index=self.index_name, body=query)
            deleted = response.get("deleted", 0)
            logger.info(f"🗑️ Deleted {deleted} documents for application {application_id}")
            return deleted
        except Exception as e:
            logger.error(f"❌ Failed to delete documents for application {application_id}: {e}")
            return 0

    def health_check(self) -> Dict[str, Any]:
        """Check Elasticsearch health and index stats"""
        if not self.es:
            return {"status": "disconnected", "error": "Not connected to Elasticsearch"}

        try:
            cluster_health = self.es.cluster.health()
            index_stats = self.es.indices.stats(index=self.index_name) if self.es.indices.exists(index=self.index_name) else {}

            return {
                "status": "connected",
                "cluster_status": cluster_health.get("status"),
                "index_exists": self.es.indices.exists(index=self.index_name),
                "document_count": index_stats.get("_all", {}).get("primaries", {}).get("docs", {}).get("count", 0)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Singleton instance
application_es_service = ApplicationElasticsearchService()

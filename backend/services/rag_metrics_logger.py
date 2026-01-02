"""
RAG Metrics Logger for Kibana Analytics

This service logs RAG comparison metrics to Elasticsearch for Kibana dashboards.
It captures query performance, scores, and retrieval metrics from both pgvector and Elasticsearch.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.services.elasticsearch_service import ElasticsearchService

logger = logging.getLogger(__name__)


class RAGMetricsLogger:
    """Logs RAG comparison metrics to Elasticsearch for Kibana visualization"""

    def __init__(self):
        """Initialize RAG metrics logger"""
        self.es_service = ElasticsearchService()
        self.index_name = "cv_rag_logs"
        self._ensure_index_exists()

    def _ensure_index_exists(self):
        """Create the cv_rag_logs index with proper mapping if it doesn't exist"""
        try:
            if not self.es_service.client.indices.exists(index=self.index_name):
                logger.info(f"Creating Elasticsearch index: {self.index_name}")

                # Define mapping for RAG metrics
                mapping = {
                    "mappings": {
                        "properties": {
                            "timestamp": {"type": "date"},
                            "query_text": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},

                            # pgvector metrics
                            "pgvector": {
                                "properties": {
                                    "score": {"type": "float"},
                                    "retrieval_time_ms": {"type": "float"},
                                    "top_scores": {"type": "float"},
                                    "chunk_count": {"type": "integer"},
                                    "chunk_ids": {"type": "keyword"},
                                    "answer_length": {"type": "integer"}
                                }
                            },

                            # Elasticsearch metrics
                            "elasticsearch": {
                                "properties": {
                                    "score": {"type": "float"},
                                    "retrieval_time_ms": {"type": "float"},
                                    "top_scores": {"type": "float"},
                                    "chunk_count": {"type": "integer"},
                                    "chunk_ids": {"type": "keyword"},
                                    "answer_length": {"type": "integer"}
                                }
                            },

                            # Evaluation results
                            "evaluation": {
                                "properties": {
                                    "winner": {"type": "keyword"},
                                    "reasoning": {"type": "text"},
                                    "pgvector_score": {"type": "float"},
                                    "elasticsearch_score": {"type": "float"},
                                    "score_difference": {"type": "float"}
                                }
                            },

                            # Metadata
                            "llm_provider": {"type": "keyword"},
                            "user_id": {"type": "keyword"}
                        }
                    }
                }

                self.es_service.client.indices.create(index=self.index_name, body=mapping)
                logger.info(f"✅ Created index '{self.index_name}' for RAG metrics logging")

        except Exception as e:
            logger.error(f"Failed to create RAG metrics index: {e}")

    def log_comparison(
        self,
        query_text: str,
        pgvector_result: Dict[str, Any],
        elasticsearch_result: Dict[str, Any],
        evaluation: Dict[str, Any],
        llm_provider: str,
        user_id: str
    ) -> bool:
        """
        Log a RAG comparison to Elasticsearch for Kibana analytics.

        Args:
            query_text: The question that was asked
            pgvector_result: Results from pgvector database
            elasticsearch_result: Results from Elasticsearch database
            evaluation: LLM evaluation results
            llm_provider: LLM provider used ("local", "grok", "anthropic")
            user_id: User ID who ran the comparison

        Returns:
            True if logging succeeded, False otherwise
        """
        try:
            # Extract chunk scores for both systems
            pgvector_chunks = pgvector_result.get('chunks', [])
            es_chunks = elasticsearch_result.get('chunks', [])

            # Build log document
            log_doc = {
                "timestamp": datetime.utcnow().isoformat(),
                "query_text": query_text,

                # pgvector metrics
                "pgvector": {
                    "score": evaluation.get("pgvector_score", 0),
                    "retrieval_time_ms": pgvector_result.get("retrieval_time_ms", 0),
                    "top_scores": [chunk.get("score", 0) for chunk in pgvector_chunks[:3]],
                    "chunk_count": len(pgvector_chunks),
                    "chunk_ids": [f"pgv_{i}" for i in range(len(pgvector_chunks))],
                    "answer_length": len(pgvector_result.get("answer", ""))
                },

                # Elasticsearch metrics
                "elasticsearch": {
                    "score": evaluation.get("elasticsearch_score", 0),
                    "retrieval_time_ms": elasticsearch_result.get("retrieval_time_ms", 0),
                    "top_scores": [chunk.get("score", 0) for chunk in es_chunks[:3]],
                    "chunk_count": len(es_chunks),
                    "chunk_ids": [f"es_{i}" for i in range(len(es_chunks))],
                    "answer_length": len(elasticsearch_result.get("answer", ""))
                },

                # Evaluation results
                "evaluation": {
                    "winner": evaluation.get("winner", "tie"),
                    "reasoning": evaluation.get("reasoning", ""),
                    "pgvector_score": evaluation.get("pgvector_score", 0),
                    "elasticsearch_score": evaluation.get("elasticsearch_score", 0),
                    "score_difference": abs(
                        evaluation.get("elasticsearch_score", 0) - evaluation.get("pgvector_score", 0)
                    )
                },

                # Metadata
                "llm_provider": llm_provider,
                "user_id": user_id
            }

            # Index document to Elasticsearch
            self.es_service.client.index(
                index=self.index_name,
                body=log_doc
            )

            logger.info(f"✅ Logged RAG comparison for query: '{query_text[:50]}...'")
            return True

        except Exception as e:
            logger.error(f"Failed to log RAG comparison: {e}")
            return False

    def get_aggregations(self) -> Dict[str, Any]:
        """
        Get aggregated statistics for Kibana dashboards.

        Returns:
            Dictionary with aggregated metrics
        """
        try:
            # Refresh index to get latest data
            self.es_service.client.indices.refresh(index=self.index_name)

            # Build aggregation query
            aggs_query = {
                "size": 0,
                "aggs": {
                    "avg_pgvector_score": {
                        "avg": {"field": "evaluation.pgvector_score"}
                    },
                    "avg_elasticsearch_score": {
                        "avg": {"field": "evaluation.elasticsearch_score"}
                    },
                    "winner_distribution": {
                        "terms": {"field": "evaluation.winner"}
                    },
                    "avg_pgvector_latency": {
                        "avg": {"field": "pgvector.retrieval_time_ms"}
                    },
                    "avg_elasticsearch_latency": {
                        "avg": {"field": "elasticsearch.retrieval_time_ms"}
                    },
                    "score_trends": {
                        "date_histogram": {
                            "field": "timestamp",
                            "calendar_interval": "hour"
                        },
                        "aggs": {
                            "avg_pgvector": {
                                "avg": {"field": "evaluation.pgvector_score"}
                            },
                            "avg_elasticsearch": {
                                "avg": {"field": "evaluation.elasticsearch_score"}
                            }
                        }
                    }
                }
            }

            result = self.es_service.client.search(
                index=self.index_name,
                body=aggs_query
            )

            aggs = result.get("aggregations", {})

            return {
                "avg_pgvector_score": aggs.get("avg_pgvector_score", {}).get("value", 0),
                "avg_elasticsearch_score": aggs.get("avg_elasticsearch_score", {}).get("value", 0),
                "winner_distribution": [
                    {"key": bucket["key"], "count": bucket["doc_count"]}
                    for bucket in aggs.get("winner_distribution", {}).get("buckets", [])
                ],
                "avg_pgvector_latency": aggs.get("avg_pgvector_latency", {}).get("value", 0),
                "avg_elasticsearch_latency": aggs.get("avg_elasticsearch_latency", {}).get("value", 0),
                "score_trends": [
                    {
                        "timestamp": bucket["key_as_string"],
                        "pgvector_score": bucket["avg_pgvector"]["value"],
                        "elasticsearch_score": bucket["avg_elasticsearch"]["value"]
                    }
                    for bucket in aggs.get("score_trends", {}).get("buckets", [])
                ]
            }

        except Exception as e:
            logger.error(f"Failed to get aggregations: {e}")
            return {}


# Global instance
_rag_metrics_logger = None


def get_rag_metrics_logger() -> RAGMetricsLogger:
    """Get or create RAG metrics logger singleton"""
    global _rag_metrics_logger
    if _rag_metrics_logger is None:
        _rag_metrics_logger = RAGMetricsLogger()
    return _rag_metrics_logger

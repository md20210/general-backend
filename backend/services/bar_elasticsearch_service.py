"""
Elasticsearch Service for Bar Ca l'Elena RAG Chatbot
Handles vector indexing and semantic search for bar information
"""
from typing import List, Dict, Any, Optional
from elasticsearch import Elasticsearch
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


class BarElasticsearchService:
    """Service for Elasticsearch operations specific to Bar Ca l'Elena"""

    def __init__(self):
        """Initialize Elasticsearch client"""
        self.es = None
        self.index_name = "bar_ca_elena"
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
                logger.info(f"✅ Connected to Elasticsearch at {es_url}")
            else:
                logger.warning(f"⚠️ Elasticsearch ping failed at {es_url}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Elasticsearch: {e}")
            self.es = None

    def create_index(self):
        """Create index for bar data with multilingual support"""
        if not self.es:
            logger.error("Elasticsearch not connected")
            return False

        # Index mapping with multilingual fields
        mapping = {
            "mappings": {
                "properties": {
                    "type": {"type": "keyword"},  # bar_info, menu, news, etc.
                    "title": {
                        "type": "text",
                        "fields": {
                            "ca": {"type": "text", "analyzer": "catalan"},
                            "es": {"type": "text", "analyzer": "spanish"},
                            "en": {"type": "text", "analyzer": "english"},
                            "de": {"type": "text", "analyzer": "german"},
                            "fr": {"type": "text", "analyzer": "french"}
                        }
                    },
                    "content": {
                        "type": "text",
                        "fields": {
                            "ca": {"type": "text", "analyzer": "catalan"},
                            "es": {"type": "text", "analyzer": "spanish"},
                            "en": {"type": "text", "analyzer": "english"},
                            "de": {"type": "text", "analyzer": "german"},
                            "fr": {"type": "text", "analyzer": "french"}
                        }
                    },
                    "language": {"type": "keyword"},
                    "metadata": {"type": "object", "enabled": True},
                    "timestamp": {"type": "date"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "catalan": {
                            "type": "standard",
                            "stopwords": "_catalan_"
                        },
                        "spanish": {
                            "type": "standard",
                            "stopwords": "_spanish_"
                        },
                        "english": {
                            "type": "standard",
                            "stopwords": "_english_"
                        },
                        "german": {
                            "type": "standard",
                            "stopwords": "_german_"
                        },
                        "french": {
                            "type": "standard",
                            "stopwords": "_french_"
                        }
                    }
                }
            }
        }

        try:
            # Delete if exists
            if self.es.indices.exists(index=self.index_name):
                self.es.indices.delete(index=self.index_name)
                logger.info(f"🗑️ Deleted existing index: {self.index_name}")

            # Create new index
            self.es.indices.create(index=self.index_name, body=mapping)
            logger.info(f"✅ Created index: {self.index_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error creating index: {e}")
            return False

    def index_bar_info(self, bar_info: Dict[str, Any]):
        """Index bar general information in all languages"""
        if not self.es:
            return False

        languages = ["ca", "es", "en", "de", "fr"]
        indexed_count = 0

        try:
            # Index description in all languages
            if isinstance(bar_info.get("description"), dict):
                for lang in languages:
                    if lang in bar_info["description"]:
                        doc = {
                            "type": "bar_info",
                            "language": lang,
                            "title": f"Bar Ca l'Elena - {lang.upper()}",
                            "content": bar_info["description"][lang],
                            "metadata": {
                                "address": bar_info.get("address"),
                                "phone": bar_info.get("phone"),
                                "cuisine": bar_info.get("cuisine"),
                                "price_range": bar_info.get("price_range"),
                                "rating": bar_info.get("rating"),
                                "location_lat": bar_info.get("location_lat"),
                                "location_lng": bar_info.get("location_lng")
                            },
                            "timestamp": "2026-01-10T00:00:00"
                        }
                        self.es.index(index=self.index_name, document=doc)
                        indexed_count += 1

            # Index opening hours
            if bar_info.get("opening_hours"):
                for lang in languages:
                    content_parts = []
                    for day, hours in bar_info["opening_hours"].items():
                        content_parts.append(f"{day}: {hours}")

                    doc = {
                        "type": "opening_hours",
                        "language": lang,
                        "title": f"Opening Hours - {lang.upper()}",
                        "content": " | ".join(content_parts),
                        "metadata": bar_info.get("opening_hours"),
                        "timestamp": "2026-01-10T00:00:00"
                    }
                    self.es.index(index=self.index_name, document=doc)
                    indexed_count += 1

            # Index featured items
            if bar_info.get("featured_items"):
                for item in bar_info["featured_items"]:
                    if isinstance(item.get("description"), dict):
                        for lang in languages:
                            if lang in item["description"]:
                                doc = {
                                    "type": "featured_item",
                                    "language": lang,
                                    "title": item.get("name"),
                                    "content": item["description"][lang],
                                    "metadata": {"item_name": item.get("name")},
                                    "timestamp": "2026-01-10T00:00:00"
                                }
                                self.es.index(index=self.index_name, document=doc)
                                indexed_count += 1

            # Index reviews
            if bar_info.get("reviews"):
                for review in bar_info["reviews"]:
                    # Reviews are typically in one language, index for all
                    for lang in languages:
                        doc = {
                            "type": "review",
                            "language": lang,
                            "title": f"Review by {review.get('author')}",
                            "content": review.get("text", ""),
                            "metadata": {
                                "author": review.get("author"),
                                "rating": review.get("rating")
                            },
                            "timestamp": "2026-01-10T00:00:00"
                        }
                        self.es.index(index=self.index_name, document=doc)
                        indexed_count += 1

            self.es.indices.refresh(index=self.index_name)
            logger.info(f"✅ Indexed {indexed_count} documents for bar info")
            return True

        except Exception as e:
            logger.error(f"❌ Error indexing bar info: {e}")
            return False

    def search(self, query: str, language: str = "en", limit: int = 5) -> List[Dict[str, Any]]:
        """Search bar information in specific language"""
        if not self.es:
            return []

        try:
            # Build multilingual search query
            search_body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": [
                                        f"title.{language}^3",
                                        f"content.{language}^2",
                                        "title^1.5",
                                        "content"
                                    ],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO"
                                }
                            }
                        ],
                        "should": [
                            {"term": {"language": language}}  # Boost matching language
                        ]
                    }
                },
                "size": limit,
                "_source": ["type", "title", "content", "language", "metadata"]
            }

            response = self.es.search(index=self.index_name, body=search_body)
            results = []

            for hit in response["hits"]["hits"]:
                results.append({
                    "score": hit["_score"],
                    "type": hit["_source"].get("type"),
                    "title": hit["_source"].get("title"),
                    "content": hit["_source"].get("content"),
                    "language": hit["_source"].get("language"),
                    "metadata": hit["_source"].get("metadata", {})
                })

            return results

        except Exception as e:
            logger.error(f"❌ Error searching: {e}")
            return []

    def get_context_for_rag(self, query: str, language: str = "en", limit: int = 3) -> str:
        """Get formatted context for RAG chatbot"""
        results = self.search(query, language, limit)

        if not results:
            return ""

        context_parts = []
        for result in results:
            context_parts.append(f"[{result['type'].upper()}] {result['title']}")
            context_parts.append(result['content'])
            context_parts.append("")

        return "\n".join(context_parts)

    def index_team_member(self, team_member: Dict[str, Any]):
        """Index a single team member in all languages"""
        if not self.es:
            return False

        languages = ["ca", "es", "en", "de", "fr"]
        indexed_count = 0

        try:
            # Only index if published
            if not team_member.get("is_published"):
                logger.info(f"⏭️ Skipping unpublished team member: {team_member.get('name')}")
                return True

            # Delete existing documents for this team member
            self._delete_team_member_documents(team_member.get("id"))

            # Index description in all languages
            if isinstance(team_member.get("description"), dict):
                for lang in languages:
                    if lang in team_member["description"]:
                        doc = {
                            "type": "team_member",
                            "language": lang,
                            "title": f"Team: {team_member.get('name')}",
                            "content": team_member["description"][lang],
                            "metadata": {
                                "team_member_id": team_member.get("id"),
                                "name": team_member.get("name"),
                                "display_order": team_member.get("display_order")
                            },
                            "timestamp": team_member.get("created_at", "2026-01-11T00:00:00")
                        }
                        self.es.index(index=self.index_name, document=doc)
                        indexed_count += 1

            self.es.indices.refresh(index=self.index_name)
            logger.info(f"✅ Indexed {indexed_count} documents for team member: {team_member.get('name')}")
            return True

        except Exception as e:
            logger.error(f"❌ Error indexing team member: {e}")
            return False

    def _delete_team_member_documents(self, team_member_id: int):
        """Delete all Elasticsearch documents for a specific team member"""
        if not self.es or not team_member_id:
            return

        try:
            delete_query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"type": "team_member"}},
                            {"term": {"metadata.team_member_id": team_member_id}}
                        ]
                    }
                }
            }
            self.es.delete_by_query(index=self.index_name, body=delete_query)
            logger.info(f"🗑️ Deleted team member documents for ID: {team_member_id}")
        except Exception as e:
            logger.error(f"❌ Error deleting team member documents: {e}")

    def index_all_team_members(self, team_members: List[Dict[str, Any]]):
        """Index all team members (bulk operation)"""
        if not self.es:
            return False

        try:
            total_indexed = 0
            for member in team_members:
                if self.index_team_member(member):
                    total_indexed += 1

            logger.info(f"✅ Indexed {total_indexed} team members total")
            return True

        except Exception as e:
            logger.error(f"❌ Error bulk indexing team members: {e}")
            return False

    def delete_team_member(self, team_member_id: int):
        """Delete a team member from Elasticsearch"""
        self._delete_team_member_documents(team_member_id)

    def index_menu(self, menu: Dict[str, Any]):
        """Index a single menu in all languages"""
        if not self.es:
            return False

        languages = ["ca", "es", "en", "de", "fr"]
        indexed_count = 0

        try:
            # Only index if active
            if not menu.get("is_active"):
                logger.info(f"⏭️ Skipping inactive menu: ID {menu.get('id')}")
                return True

            # Delete existing documents for this menu
            self._delete_menu_documents(menu.get("id"))

            # Index content in all languages
            if isinstance(menu.get("content_translations"), dict):
                for lang in languages:
                    if lang in menu["content_translations"]:
                        doc = {
                            "type": "menu",
                            "language": lang,
                            "title": f"{menu.get('menu_type', 'Menu').title()} Menu",
                            "content": menu["content_translations"][lang],
                            "metadata": {
                                "menu_id": menu.get("id"),
                                "menu_type": menu.get("menu_type"),
                                "display_order": menu.get("display_order")
                            },
                            "timestamp": menu.get("created_at", "2026-01-11T00:00:00")
                        }
                        self.es.index(index=self.index_name, document=doc)
                        indexed_count += 1

            self.es.indices.refresh(index=self.index_name)
            logger.info(f"✅ Indexed {indexed_count} documents for menu ID: {menu.get('id')}")
            return True

        except Exception as e:
            logger.error(f"❌ Error indexing menu: {e}")
            return False

    def _delete_menu_documents(self, menu_id: int):
        """Delete all Elasticsearch documents for a specific menu"""
        if not self.es or not menu_id:
            return

        try:
            delete_query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"type": "menu"}},
                            {"term": {"metadata.menu_id": menu_id}}
                        ]
                    }
                }
            }
            self.es.delete_by_query(index=self.index_name, body=delete_query)
            logger.info(f"🗑️ Deleted menu documents for ID: {menu_id}")
        except Exception as e:
            logger.error(f"❌ Error deleting menu documents: {e}")

    def delete_menu(self, menu_id: int):
        """Delete a menu from Elasticsearch"""
        self._delete_menu_documents(menu_id)


# Global instance
bar_es_service = BarElasticsearchService()

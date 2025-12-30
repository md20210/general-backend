"""Demo Data Generator - Generate 100 variations of user's analysis."""
import random
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)


class DemoDataGenerator:
    """Generate demo data variations for impressive visualizations."""

    # Skill pools for variations
    PROGRAMMING_LANGUAGES = [
        "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust",
        "C++", "C#", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "Elixir"
    ]

    FRAMEWORKS = [
        "React", "Angular", "Vue", "Django", "Flask", "FastAPI", "Spring Boot",
        "Node.js", "Express", "Next.js", "Nuxt", "Laravel", "Rails", "Phoenix",
        "ASP.NET", "Svelte", "Solid.js", "Remix"
    ]

    DATABASES = [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
        "Cassandra", "DynamoDB", "Oracle", "SQL Server", "MariaDB",
        "Neo4j", "CouchDB", "InfluxDB", "TimescaleDB"
    ]

    CLOUD_DEVOPS = [
        "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform",
        "Ansible", "Jenkins", "GitLab CI", "GitHub Actions", "ArgoCD",
        "Pulumi", "CloudFormation", "Helm", "Istio", "Prometheus"
    ]

    AI_ML = [
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "TensorFlow", "PyTorch", "Scikit-learn", "Keras", "Hugging Face",
        "LangChain", "OpenAI", "Anthropic Claude", "Stable Diffusion"
    ]

    COMPANIES = [
        "Google", "Amazon", "Microsoft", "Apple", "Meta", "Netflix",
        "Spotify", "Uber", "Airbnb", "Stripe", "Shopify", "Slack",
        "Datadog", "Elastic", "MongoDB", "Redis Labs", "Confluent",
        "HashiCorp", "GitLab", "GitHub", "Docker", "Kubernetes Inc",
        "Snowflake", "Databricks", "Palantir", "Cloudflare"
    ]

    LOCATIONS = [
        "San Francisco", "New York", "Seattle", "Austin", "Boston",
        "London", "Berlin", "Amsterdam", "Paris", "Barcelona",
        "Munich", "Zurich", "Stockholm", "Copenhagen", "Dublin",
        "Remote", "Hybrid - San Francisco", "Remote - Europe"
    ]

    JOB_TITLES = [
        "Senior Software Engineer", "Staff Engineer", "Principal Engineer",
        "Lead Developer", "Software Architect", "Backend Engineer",
        "Frontend Engineer", "Full Stack Developer", "DevOps Engineer",
        "Platform Engineer", "Data Engineer", "ML Engineer",
        "Engineering Manager", "Tech Lead", "Senior Backend Developer"
    ]

    SENIORITY_LEVELS = ["Junior", "Mid-Level", "Senior", "Staff", "Principal", "Lead"]
    EDUCATION_LEVELS = ["Bachelor", "Master", "PhD", "Diploma", "Self-taught"]
    REMOTE_POLICIES = ["remote", "hybrid", "on-site"]

    def generate_variations(
        self,
        base_analysis: Dict[str, Any],
        count: int = 100,
        user_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Generate variations of a base analysis.

        Args:
            base_analysis: The original analysis to vary
            count: Number of variations to generate
            user_id: User ID for the variations

        Returns:
            List of varied analyses
        """
        variations = []

        for i in range(count):
            variation = self._create_variation(base_analysis, i, user_id)
            variations.append(variation)

        logger.info(f"Generated {count} analysis variations")
        return variations

    def _create_variation(
        self,
        base: Dict[str, Any],
        index: int,
        user_id: str
    ) -> Dict[str, Any]:
        """Create a single variation of the base analysis."""

        # Vary job details
        job_analysis = base.get("job_analysis", {})
        varied_job = {
            "company": random.choice(self.COMPANIES),
            "role": random.choice(self.JOB_TITLES),
            "location": random.choice(self.LOCATIONS),
            "remote_policy": random.choice(self.REMOTE_POLICIES),
            "seniority": random.choice(self.SENIORITY_LEVELS),
            "salary_range": self._generate_salary_range(),
            "requirements": self._generate_requirements(),
            "responsibilities": job_analysis.get("responsibilities", [])[:3],
            "keywords": self._generate_random_skills(5),
            "red_flags": random.sample(
                ["Long hours", "Unclear role", "Micromanagement", "Legacy tech"],
                k=random.randint(0, 2)
            ),
            "green_flags": random.sample(
                ["Good work-life balance", "Modern tech stack", "Great culture", "Learning opportunities"],
                k=random.randint(1, 3)
            )
        }

        # Vary fit score
        base_score = base.get("fit_score", {}).get("total", 70)
        score_variation = random.randint(-20, 20)
        total_score = max(0, min(100, base_score + score_variation))

        fit_score = {
            "total": total_score,
            "breakdown": {
                "experience_match": random.randint(60, 100),
                "skills_match": random.randint(50, 100),
                "education_match": random.randint(70, 100),
                "location_match": random.randint(40, 100),
                "salary_match": random.randint(60, 100),
                "culture_match": random.randint(50, 90),
                "role_type_match": random.randint(60, 95)
            },
            "matched_skills": self._generate_random_skills(random.randint(5, 15)),
            "missing_skills": self._generate_random_skills(random.randint(0, 5))
        }

        # Vary success probability
        probability = max(0, min(100, total_score + random.randint(-15, 15)))
        success_probability = {
            "probability": probability,
            "factors": self._generate_factors(probability),
            "recommendation": self._generate_recommendation(probability)
        }

        # Vary search performance
        chromadb_time = random.uniform(50, 200)
        es_time = random.uniform(5, 30)

        # Create variation
        variation = {
            "user_id": user_id or str(uuid.uuid4()),
            "job_description": f"{varied_job['role']} at {varied_job['company']}",
            "job_url": f"https://example.com/jobs/{uuid.uuid4().hex[:8]}",

            # ChromaDB results
            "chromadb_results": {"items": [{"score": random.uniform(0.6, 0.9)}]},
            "chromadb_search_time_ms": chromadb_time,
            "chromadb_matches_count": random.randint(1, 10),
            "chromadb_relevance_score": random.uniform(0.6, 0.95),

            # Elasticsearch results
            "elasticsearch_results": {"items": [{"score": random.uniform(5, 15)}]},
            "elasticsearch_search_time_ms": es_time,
            "elasticsearch_matches_count": random.randint(1, 20),
            "elasticsearch_relevance_score": random.uniform(8, 15),

            # Advanced features
            "fuzzy_matches": self._generate_fuzzy_matches(),
            "synonym_matches": self._generate_synonym_matches(),
            "skill_clusters": self._generate_skill_clusters(),

            # Performance comparison
            "performance_comparison": {
                "chromadb_time_ms": chromadb_time,
                "elasticsearch_time_ms": es_time,
                "speedup_factor": round(chromadb_time / es_time, 2),
                "faster_system": "Elasticsearch",
                "time_saved_ms": chromadb_time - es_time,
                "percentage_difference": round((chromadb_time - es_time) / chromadb_time * 100, 2)
            },

            # Feature comparison
            "feature_comparison": {
                "chromadb": {
                    "features": ["Vector embeddings", "Semantic search"],
                    "strengths": ["Simple API", "Lightweight"],
                    "limitations": ["No fuzzy matching", "No synonyms"]
                },
                "elasticsearch": {
                    "features": ["Fuzzy", "Synonyms", "Aggregations"],
                    "strengths": ["Production-ready", "Scalable"],
                    "limitations": ["More complex"]
                }
            },

            # LLM analysis
            "job_analysis": varied_job,
            "fit_score": fit_score,
            "success_probability": success_probability,
            "provider": random.choice(["grok", "claude", "openai"]),

            # Metadata
            "created_at": datetime.utcnow() - timedelta(hours=random.randint(0, 720))
        }

        return variation

    def _generate_salary_range(self) -> Dict[str, Any]:
        """Generate realistic salary range."""
        base = random.choice([80000, 100000, 120000, 150000, 180000, 200000])
        return {
            "min": base,
            "max": base + random.randint(20000, 50000),
            "currency": random.choice(["USD", "EUR", "GBP"])
        }

    def _generate_requirements(self) -> Dict[str, Any]:
        """Generate job requirements."""
        return {
            "must_have": self._generate_random_skills(random.randint(5, 10)),
            "nice_to_have": self._generate_random_skills(random.randint(3, 7)),
            "years_experience": {
                "min": random.randint(2, 5),
                "max": random.randint(8, 15)
            },
            "education": random.choice(self.EDUCATION_LEVELS),
            "languages": random.sample(["English", "German", "Spanish", "French"], k=random.randint(1, 2)),
            "certifications": random.sample(
                ["AWS Certified", "Kubernetes Certified", "Google Cloud Certified"],
                k=random.randint(0, 2)
            )
        }

    def _generate_random_skills(self, count: int) -> List[str]:
        """Generate random skills from all categories."""
        all_skills = (
            self.PROGRAMMING_LANGUAGES +
            self.FRAMEWORKS +
            self.DATABASES +
            self.CLOUD_DEVOPS +
            self.AI_ML
        )
        return random.sample(all_skills, min(count, len(all_skills)))

    def _generate_fuzzy_matches(self) -> List[Dict[str, Any]]:
        """Generate fuzzy match examples."""
        examples = [
            {"searched": "Pythn", "matched": "Python", "score": random.uniform(8, 12)},
            {"searched": "Reactjs", "matched": "React", "score": random.uniform(9, 13)},
            {"searched": "Kubernetis", "matched": "Kubernetes", "score": random.uniform(7, 11)}
        ]
        return random.sample(examples, k=random.randint(1, 3))

    def _generate_synonym_matches(self) -> List[Dict[str, Any]]:
        """Generate synonym match examples."""
        examples = [
            {"searched": "ML", "matched": "Machine Learning", "score": random.uniform(10, 15)},
            {"searched": "JS", "matched": "JavaScript", "score": random.uniform(9, 14)},
            {"searched": "K8s", "matched": "Kubernetes", "score": random.uniform(8, 13)}
        ]
        return random.sample(examples, k=random.randint(1, 3))

    def _generate_skill_clusters(self) -> Dict[str, Any]:
        """Generate skill cluster data for visualizations."""
        return {
            "programming_languages": random.sample(self.PROGRAMMING_LANGUAGES, k=random.randint(3, 6)),
            "frameworks": random.sample(self.FRAMEWORKS, k=random.randint(2, 5)),
            "databases": random.sample(self.DATABASES, k=random.randint(2, 4)),
            "cloud_devops": random.sample(self.CLOUD_DEVOPS, k=random.randint(2, 5)),
            "ai_ml": random.sample(self.AI_ML, k=random.randint(0, 3))
        }

    def _generate_factors(self, probability: int) -> List[str]:
        """Generate factors affecting success probability."""
        positive_factors = [
            "Strong skill match",
            "Relevant experience",
            "Matching education level",
            "Good cultural fit",
            "Salary expectations aligned"
        ]
        negative_factors = [
            "Some skills missing",
            "Location mismatch",
            "Seniority gap",
            "Limited domain experience"
        ]

        if probability >= 70:
            return random.sample(positive_factors, k=random.randint(3, 5))
        elif probability >= 40:
            return random.sample(positive_factors + negative_factors, k=random.randint(2, 4))
        else:
            return random.sample(negative_factors, k=random.randint(2, 4))

    def _generate_recommendation(self, probability: int) -> str:
        """Generate recommendation based on probability."""
        if probability >= 80:
            return random.choice([
                "Excellent match! Apply immediately.",
                "Strong candidate - highly recommended to apply.",
                "Perfect fit! This role aligns very well with your profile."
            ])
        elif probability >= 60:
            return random.choice([
                "Good match. Consider applying.",
                "Solid fit - worth pursuing this opportunity.",
                "Recommended. You meet most requirements."
            ])
        elif probability >= 40:
            return random.choice([
                "Moderate match. Apply if interested in learning.",
                "Partial fit - consider upskilling in missing areas.",
                "Worth exploring, but some gaps exist."
            ])
        else:
            return random.choice([
                "Weak match. Focus on building missing skills first.",
                "Not recommended unless willing to learn extensively.",
                "Significant gaps - consider other opportunities."
            ])

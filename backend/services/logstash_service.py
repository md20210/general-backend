"""Logstash Integration Service - CV & Job Parsing Pipelines."""
import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class LogstashService:
    """
    Simulates Logstash pipelines for CV and Job parsing.

    When real Logstash is deployed, this service will send data to Logstash HTTP inputs.
    For now, it implements the same parsing logic in Python.
    """

    # Skill patterns (same as Logstash Grok patterns)
    PROGRAMMING_LANGUAGES = [
        "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust",
        "C++", "C#", "Ruby", "PHP", "Swift", "Kotlin", "Scala"
    ]

    FRAMEWORKS = [
        "React", "Angular", "Vue", "Django", "Flask", "FastAPI", "Spring",
        "Node.js", "Express", "Next.js", "Nuxt", "Laravel", "Rails"
    ]

    DATABASES = [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
        "Cassandra", "DynamoDB", "Oracle", "SQL Server"
    ]

    CLOUD_DEVOPS = [
        "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform",
        "Ansible", "Jenkins", "GitLab", "GitHub Actions", "ArgoCD"
    ]

    AI_ML = [
        "Machine Learning", "AI", "Deep Learning", "NLP", "Computer Vision",
        "TensorFlow", "PyTorch", "Scikit-learn", "Keras", "Hugging Face"
    ]

    METHODOLOGIES = [
        "Agile", "Scrum", "Kanban", "TOGAF", "Enterprise Architecture",
        "Microservices", "SOA", "Event-Driven", "CQRS"
    ]

    # Skill synonyms (same as Logstash translate filter)
    SYNONYMS = {
        "ml": "Machine Learning",
        "ai": "Artificial Intelligence",
        "dl": "Deep Learning",
        "nlp": "Natural Language Processing",
        "cv": "Computer Vision",
        "k8s": "Kubernetes",
        "tf": "Terraform",
        "js": "JavaScript",
        "ts": "TypeScript",
        "py": "Python",
        "pg": "PostgreSQL",
        "es": "Elasticsearch",
        "aws": "Amazon Web Services",
        "gcp": "Google Cloud Platform",
    }

    def __init__(self, logstash_url: Optional[str] = None):
        """
        Initialize Logstash service.

        Args:
            logstash_url: URL of Logstash service (if deployed)
        """
        self.logstash_url = logstash_url
        self.is_logstash_available = logstash_url is not None
        logger.info(f"LogstashService initialized (Logstash deployed: {self.is_logstash_available})")

    def parse_cv(self, cv_text: str, user_id: str) -> Dict[str, Any]:
        """
        Parse CV text to extract skills, experience, education.

        Implements same logic as logstash/cv-parsing.conf

        Args:
            cv_text: Raw CV text
            user_id: User ID

        Returns:
            Parsed CV data with extracted fields
        """
        result = {
            "user_id": user_id,
            "cv_text": cv_text,
            "skills_extracted": [],
            "experience_years": None,
            "education_level": None,
            "job_titles": [],
            "pipeline": "cv-parsing",
            "enriched": {}
        }

        # Extract skills
        all_skills = (
            self.PROGRAMMING_LANGUAGES +
            self.FRAMEWORKS +
            self.DATABASES +
            self.CLOUD_DEVOPS +
            self.AI_ML +
            self.METHODOLOGIES
        )

        text_lower = cv_text.lower()
        for skill in all_skills:
            if skill.lower() in text_lower:
                result["skills_extracted"].append(skill)

        # Deduplicate skills
        result["skills_extracted"] = list(set(result["skills_extracted"]))

        # Extract years of experience
        experience_patterns = [
            r"(\d+)\+?\s*(years?|jahre)\s*(of\s*)?experience",
            r"(\d+)\s*(years?|jahre)\s*in\s*(software|development|programming)",
        ]

        for pattern in experience_patterns:
            match = re.search(pattern, cv_text, re.IGNORECASE)
            if match:
                result["experience_years"] = int(match.group(1))
                break

        # Extract education level
        education_patterns = {
            "PhD": r"(?i)(phd|doctorate|doktor|dr\.)",
            "Master": r"(?i)(master|m\.sc\.|m\.a\.|mba|m\.eng)",
            "Bachelor": r"(?i)(bachelor|b\.sc\.|b\.a\.|b\.eng)",
            "Diploma": r"(?i)(diplom|diploma)",
        }

        for level, pattern in education_patterns.items():
            if re.search(pattern, cv_text):
                result["education_level"] = level
                break

        # Extract job titles (simple patterns)
        title_patterns = [
            r"(?i)(senior|lead|principal|staff|chief)\s+(software\s+)?(engineer|developer|architect)",
            r"(?i)(software|backend|frontend|fullstack)\s+(engineer|developer)",
            r"(?i)(data|ml|ai)\s+(scientist|engineer)",
            r"(?i)(devops|platform|infrastructure)\s+engineer",
        ]

        for pattern in title_patterns:
            matches = re.findall(pattern, cv_text)
            for match in matches:
                title = " ".join(filter(None, match))
                result["job_titles"].append(title.strip())

        result["job_titles"] = list(set(result["job_titles"]))[:5]  # Max 5 titles

        # Enrich skills with categories
        result["enriched"] = self._enrich_skills(result["skills_extracted"])

        logger.info(f"CV parsed for user {user_id}: {len(result['skills_extracted'])} skills, {result['experience_years']} years")

        return result

    def parse_job(self, job_description: str, job_id: str) -> Dict[str, Any]:
        """
        Parse job description to extract requirements, company info.

        Implements same logic as logstash/job-parsing.conf

        Args:
            job_description: Raw job description text
            job_id: Job ID

        Returns:
            Parsed job data with extracted fields
        """
        result = {
            "job_id": job_id,
            "job_description": job_description,
            "company": None,
            "location": None,
            "remote_policy": None,
            "required_skills": [],
            "years_required": None,
            "salary_range": {},
            "must_have": [],
            "nice_to_have": [],
            "pipeline": "job-parsing",
            "enriched": {}
        }

        # Extract company name
        company_patterns = [
            r"(?i)(?:company|organization|firma):\s*([A-Za-z0-9\s&\.-]+)",
            r"(?i)(?:at|@)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        ]

        for pattern in company_patterns:
            match = re.search(pattern, job_description)
            if match:
                result["company"] = match.group(1).strip()
                break

        # Extract location
        location_patterns = [
            r"(?i)(?:location|standort|office):\s*([A-Za-z\s,]+)",
            r"(?i)(?:based in|located in)\s+([A-Za-z\s,]+)",
        ]

        for pattern in location_patterns:
            match = re.search(pattern, job_description)
            if match:
                result["location"] = match.group(1).strip()
                break

        # Extract remote policy
        if re.search(r"(?i)\b(remote|fully\s*remote)\b", job_description):
            result["remote_policy"] = "remote"
        elif re.search(r"(?i)\bhybrid\b", job_description):
            result["remote_policy"] = "hybrid"
        elif re.search(r"(?i)(on-site|onsite|vor\s*ort)", job_description):
            result["remote_policy"] = "on-site"

        # Extract required skills
        all_skills = (
            self.PROGRAMMING_LANGUAGES +
            self.FRAMEWORKS +
            self.DATABASES +
            self.CLOUD_DEVOPS +
            self.AI_ML
        )

        text_lower = job_description.lower()
        for skill in all_skills:
            if skill.lower() in text_lower:
                result["required_skills"].append(skill)

        result["required_skills"] = list(set(result["required_skills"]))

        # Extract years of experience required
        years_pattern = r"(\d+)\+?\s*(?:years?|jahre)\s*(?:of\s*)?experience"
        match = re.search(years_pattern, job_description, re.IGNORECASE)
        if match:
            result["years_required"] = int(match.group(1))

        # Extract salary range
        salary_patterns = [
            r"(\d{1,3}(?:,\d{3})*)\s*[-–]\s*(\d{1,3}(?:,\d{3})*)\s*(EUR|USD|€|\$|CHF)",
            r"(€|\$)\s*(\d{1,3}(?:,\d{3})*)\s*[-–]\s*(\d{1,3}(?:,\d{3})*)",
        ]

        for pattern in salary_patterns:
            match = re.search(pattern, job_description)
            if match:
                result["salary_range"] = {
                    "min": int(re.sub(r"\D", "", match.group(1) if "$" not in match.group(1) else match.group(2))),
                    "max": int(re.sub(r"\D", "", match.group(2) if "$" not in match.group(1) else match.group(3))),
                    "currency": match.group(3) if "$" not in match.group(1) else match.group(1),
                }
                break

        # Enrich skills
        result["enriched"] = self._enrich_skills(result["required_skills"])

        logger.info(f"Job parsed: {result['company']} in {result['location']}, {len(result['required_skills'])} skills")

        return result

    def _enrich_skills(self, skills: List[str]) -> Dict[str, Any]:
        """
        Enrich skills with synonyms and categorization.

        Implements same logic as logstash/enrichment.conf

        Args:
            skills: List of skill names

        Returns:
            Enriched data with categories and synonyms
        """
        enriched = {
            "categories": {},
            "synonyms": {},
            "by_category": {
                "programming_language": [],
                "framework": [],
                "database": [],
                "cloud_devops": [],
                "ai_ml": [],
                "methodology": [],
                "other": []
            }
        }

        for skill in skills:
            skill_lower = skill.lower()

            # Add synonyms
            if skill_lower in self.SYNONYMS:
                enriched["synonyms"][skill] = self.SYNONYMS[skill_lower]

            # Categorize
            if skill in self.PROGRAMMING_LANGUAGES:
                category = "programming_language"
            elif skill in self.FRAMEWORKS:
                category = "framework"
            elif skill in self.DATABASES:
                category = "database"
            elif skill in self.CLOUD_DEVOPS:
                category = "cloud_devops"
            elif skill in self.AI_ML:
                category = "ai_ml"
            elif skill in self.METHODOLOGIES:
                category = "methodology"
            else:
                category = "other"

            enriched["by_category"][category].append(skill)
            enriched["categories"][skill] = category

        return enriched

    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get status of all Logstash pipelines.

        Returns:
            Pipeline status information
        """
        return {
            "pipelines": {
                "cv-parsing": {
                    "status": "active",
                    "endpoint": f"{self.logstash_url}:8080" if self.logstash_url else "simulated",
                    "workers": 2,
                },
                "job-parsing": {
                    "status": "active",
                    "endpoint": f"{self.logstash_url}:8081" if self.logstash_url else "simulated",
                    "workers": 2,
                },
                "enrichment": {
                    "status": "active",
                    "endpoint": f"{self.logstash_url}:8082" if self.logstash_url else "simulated",
                    "workers": 1,
                }
            },
            "logstash_deployed": self.is_logstash_available,
            "mode": "production" if self.is_logstash_available else "simulated"
        }

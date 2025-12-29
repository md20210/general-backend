"""Job Assistant Service - Job Analysis, Fit Calculation, and Document Generation."""
import json
import logging
import re
from typing import Dict, Any, List, Optional
from backend.services.llm_gateway import LLMGateway
from backend.schemas.jobassistant import (
    JobAnalysisResult,
    FitScore,
    FitScoreBreakdown,
    SuccessProbability,
    ProbabilityFactor,
    UserProfileResponse,
    Requirements,
    RoleType,
    CompanyInfo,
)


class JobAssistantService:
    """Service for job analysis and application assistance."""

    def __init__(self):
        """Initialize the service."""
        self.llm = LLMGateway()

    async def analyze_job(
        self,
        job_description: str,
        additional_context: Optional[str] = None,
        provider: str = "anthropic",
        model: Optional[str] = None,
    ) -> JobAnalysisResult:
        """
        Analyze a job description using LLM.

        Args:
            job_description: The job posting text
            additional_context: Optional additional context or notes for analysis
            provider: LLM provider (anthropic, grok, ollama)
            model: Specific model to use

        Returns:
            Structured job analysis
        """
        context_section = f"\n\nAdditional Context:\n{additional_context}\n" if additional_context else ""

        prompt = f"""Analyze this job description and extract structured data.

Job Description:
{job_description}{context_section}

Extract the following as valid JSON only (no markdown, no explanations):
{{
  "company": "Company name",
  "role": "Job title",
  "location": "Location",
  "remote_policy": "Remote/Hybrid/Office",
  "seniority": "Junior/Mid/Senior/Lead/Director",
  "salary_range": {{"min": null, "max": null, "currency": "EUR"}},

  "requirements": {{
    "must_have": ["List of must-have requirements"],
    "nice_to_have": ["List of nice-to-have requirements"],
    "years_experience": {{"min": 0, "max": 0}},
    "education": "Education requirement",
    "languages": ["Required languages"],
    "certifications": ["Required certifications"]
  }},

  "responsibilities": ["List of main responsibilities"],

  "role_type": {{
    "is_sales": true/false,
    "is_delivery": true/false,
    "is_technical": true/false,
    "is_management": true/false,
    "is_consulting": true/false,
    "requires_coding": true/false,
    "is_client_facing": true/false,
    "requires_quota": true/false
  }},

  "keywords": ["Important keywords for CV optimization"],

  "company_info": {{
    "size": "Startup/SMB/Enterprise",
    "industry": "Industry",
    "culture_hints": ["Cultural hints from description"]
  }},

  "red_flags": ["Potential warning signs"],
  "green_flags": ["Positive aspects"]
}}

Return ONLY valid JSON, nothing else."""

        result = self.llm.generate(
            prompt=prompt,
            provider=provider,
            model=model,
            temperature=0.1,
            max_tokens=3000,
        )

        # Parse JSON from response
        response_text = result.get("response", "")

        # Extract JSON from markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)

        # Clean and parse
        response_text = response_text.strip()
        analysis_data = json.loads(response_text)

        # Convert to Pydantic models
        return JobAnalysisResult(
            company=analysis_data.get("company", "Unknown"),
            role=analysis_data.get("role", "Unknown"),
            location=analysis_data.get("location", "Unknown"),
            remote_policy=analysis_data.get("remote_policy", "Unknown"),
            seniority=analysis_data.get("seniority", "Unknown"),
            salary_range=analysis_data.get("salary_range", {}),
            requirements=Requirements(**analysis_data.get("requirements", {})),
            responsibilities=analysis_data.get("responsibilities", []),
            role_type=RoleType(**analysis_data.get("role_type", {})),
            keywords=analysis_data.get("keywords", []),
            company_info=CompanyInfo(**analysis_data.get("company_info", {})),
            red_flags=analysis_data.get("red_flags", []),
            green_flags=analysis_data.get("green_flags", []),
        )

    async def calculate_fit_score_with_llm(
        self,
        job_analysis: JobAnalysisResult,
        profile: UserProfileResponse,
        cv_text: Optional[str] = None,
        provider: str = "grok"
    ) -> FitScore:
        """
        Calculate fit score using LLM intelligence for nuanced analysis.

        This method leverages LLM reasoning to:
        - Intelligently match skills (understanding synonyms and related experience)
        - Provide contextual comparisons
        - Avoid redundant missing skills
        - Generate human-readable explanations

        Args:
            job_analysis: Analyzed job data
            profile: Candidate profile
            cv_text: Optional CV text for richer analysis
            provider: LLM provider for analysis

        Returns:
            Fit score with LLM-generated insights
        """
        from backend.schemas.jobassistant import FitScoreDetail

        # Safe value extraction with None handling
        candidate_min_salary = profile.preferences.get('min_salary_eur') or 0
        candidate_years_exp = profile.summary.get('years_experience') or 0
        job_min_salary = job_analysis.salary_range.get('min') or 0
        job_max_salary = job_analysis.salary_range.get('max') or 0
        job_min_exp = job_analysis.requirements.years_experience.get('min') or 0

        # Prepare candidate summary
        candidate_summary = f"""
CANDIDATE PROFILE:
Experience: {candidate_years_exp} years
Education: {profile.education.get('degree', 'Not specified')}
Location: {profile.personal.get('location', 'Not specified')}
Expected Salary: €{candidate_min_salary:,}
Key Skills: {', '.join(self._flatten_skills(profile.skills)[:15])}
Ideal Roles: {', '.join(profile.preferences.get('ideal_roles', []))}
"""

        # Prepare job requirements
        job_requirements = f"""
JOB REQUIREMENTS:
Company: {job_analysis.company}
Role: {job_analysis.role}
Location: {job_analysis.location} ({job_analysis.remote_policy})
Seniority: {job_analysis.seniority}
Salary Range: €{job_min_salary:,} - €{job_max_salary:,}
Required Experience: {job_min_exp}+ years
Education: {job_analysis.requirements.education}
Must-Have Skills: {', '.join(job_analysis.requirements.must_have[:10])}
Nice-to-Have: {', '.join(job_analysis.requirements.nice_to_have[:5])}
Role Type: {'Technical' if job_analysis.role_type.is_technical else ''} {'Management' if job_analysis.role_type.is_management else ''} {'Sales' if job_analysis.role_type.is_sales else ''}
"""

        prompt = f"""{candidate_summary}

{job_requirements}

Analyze the fit between this candidate and job. Be intelligent and contextual:
- Recognize that "Program Management" covers "Project Management"
- Understand that 20 years experience exceeds 5+ years requirement
- Consider location flexibility and remote policy
- Match skills semantically, not just by exact string match

IMPORTANT: "comparison" must be ONE CONCISE GERMAN SENTENCE (max 15 words) explaining WHY!

Examples of GOOD comparisons:
- "20+ Jahre Erfahrung übertrifft geforderte 5+ Jahre deutlich"
- "15 von 20 Kernkompetenzen vorhanden, wichtigste Skills passen"
- "Master-Abschluss erfüllt Bachelor-Anforderung vollständig"
- "Barcelona-Madrid Distanz durch Remote-Option überbrückbar"
- "Gehaltsvorstellung passt zum Angebot perfekt"

Return JSON with this structure:
{{
  "experience_match": {{"score": 0-100, "candidate": "20+ Jahre", "required": "10+ Jahre", "comparison": "Prägnanter deutscher Satz WARUM"}},
  "skills_match": {{"score": 0-100, "candidate": "15 matched", "required": "20 total", "comparison": "Prägnanter deutscher Satz WARUM"}},
  "education_match": {{"score": 0-100, "candidate": "Master", "required": "Bachelor", "comparison": "Prägnanter deutscher Satz WARUM"}},
  "location_match": {{"score": 0-100, "candidate": "Barcelona", "required": "Madrid", "comparison": "Prägnanter deutscher Satz WARUM"}},
  "salary_match": {{"score": 0-100, "candidate": "€100k", "required": "€80-120k", "comparison": "Prägnanter deutscher Satz WARUM"}},
  "culture_match": {{"score": 0-100, "candidate": "Flexible", "required": "Startup", "comparison": "Prägnanter deutscher Satz WARUM"}},
  "role_type_match": {{"score": 0-100, "candidate": "Program Mgmt", "required": "Tech+Mgmt", "comparison": "Prägnanter deutscher Satz WARUM"}},
  "matched_skills": ["Skills - no duplicates"],
  "missing_skills": ["Only truly missing skills"]
}}

Return ONLY the JSON, no other text."""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                provider=provider,
                temperature=0.3,
                max_tokens=2000
            )

            # Parse LLM response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in LLM response")

            llm_analysis = json.loads(json_match.group())

            # Build FitScoreDetail objects
            experience_detail = FitScoreDetail(**llm_analysis['experience_match'])
            skills_detail = FitScoreDetail(**llm_analysis['skills_match'])
            education_detail = FitScoreDetail(**llm_analysis['education_match'])
            location_detail = FitScoreDetail(**llm_analysis['location_match'])
            salary_detail = FitScoreDetail(**llm_analysis['salary_match'])
            culture_detail = FitScoreDetail(**llm_analysis['culture_match'])
            role_type_detail = FitScoreDetail(**llm_analysis['role_type_match'])

            # Calculate weighted total
            scores = {
                'experience_match': experience_detail.score,
                'skills_match': skills_detail.score,
                'education_match': education_detail.score,
                'location_match': location_detail.score,
                'salary_match': salary_detail.score,
                'culture_match': culture_detail.score,
                'role_type_match': role_type_detail.score,
            }

            weights = {
                "experience_match": 0.20,
                "skills_match": 0.25,
                "education_match": 0.10,
                "location_match": 0.15,
                "salary_match": 0.10,
                "culture_match": 0.05,
                "role_type_match": 0.15,
            }

            total_score = sum(scores[key] * weights[key] for key in scores)

            breakdown = FitScoreBreakdown(
                **scores,
                experience_detail=experience_detail,
                skills_detail=skills_detail,
                education_detail=education_detail,
                location_detail=location_detail,
                salary_detail=salary_detail,
                culture_detail=culture_detail,
                role_type_detail=role_type_detail,
            )

            return FitScore(
                total=int(total_score),
                breakdown=breakdown,
                matched_skills=llm_analysis.get('matched_skills', [])[:20],
                missing_skills=llm_analysis.get('missing_skills', [])[:10],
            )

        except Exception as e:
            # Fallback to algorithmic method if LLM fails
            print(f"LLM fit score calculation failed: {e}, falling back to algorithmic method")
            return self.calculate_fit_score(job_analysis, profile, cv_text)

    def _flatten_skills(self, skills_dict: Dict[str, Any]) -> List[str]:
        """Helper to flatten skills dictionary."""
        flat_skills = []
        for category in skills_dict.values():
            if isinstance(category, list):
                flat_skills.extend(category)
            elif isinstance(category, dict):
                flat_skills.extend(category.keys())
        return flat_skills

    def calculate_fit_score(
        self,
        job_analysis: JobAnalysisResult,
        profile: UserProfileResponse,
        cv_text: Optional[str] = None
    ) -> FitScore:
        """
        Calculate how well the candidate fits the job.

        Args:
            job_analysis: Analyzed job data
            profile: Candidate profile
            cv_text: Optional CV text to use instead of profile data

        Returns:
            Fit score with breakdown

        Note:
            If cv_text is provided, it's available for future enhanced matching.
            Currently uses profile data for scoring.
        """
        scores = {
            "experience_match": 0,
            "skills_match": 0,
            "education_match": 0,
            "location_match": 0,
            "salary_match": 0,
            "culture_match": 0,
            "role_type_match": 0,
        }

        # Experience Match
        required_years = job_analysis.requirements.years_experience.get("min", 0)
        candidate_years = profile.summary.get("years_experience", 0)
        if candidate_years >= required_years:
            scores["experience_match"] = 100
        elif required_years > 0:
            scores["experience_match"] = int((candidate_years / required_years) * 100)

        # Skills Match - combine all required skills
        required_skills = (
            job_analysis.requirements.must_have
            + job_analysis.keywords
            + job_analysis.requirements.nice_to_have
        )

        # Flatten all candidate skills
        candidate_skills = []
        skills_dict = profile.skills
        for skill_category in skills_dict.values():
            if isinstance(skill_category, list):
                candidate_skills.extend(skill_category)
            elif isinstance(skill_category, dict):
                candidate_skills.extend(skill_category.keys())

        # Count matches (case-insensitive, partial match)
        matched_skills = []
        for req_skill in required_skills:
            for cand_skill in candidate_skills:
                if (
                    req_skill.lower() in cand_skill.lower()
                    or cand_skill.lower() in req_skill.lower()
                ):
                    matched_skills.append(req_skill)
                    break

        if required_skills:
            scores["skills_match"] = int((len(matched_skills) / len(required_skills)) * 100)

        # Education Match
        candidate_education = profile.education.get("degree", "").lower()
        required_education = job_analysis.requirements.education.lower()
        if "master" in candidate_education or "diplom" in candidate_education:
            scores["education_match"] = 100
        elif "bachelor" in candidate_education:
            scores["education_match"] = 80
        else:
            scores["education_match"] = 60

        # Location Match
        candidate_location = profile.personal.get("location", "").lower()
        job_location = job_analysis.location.lower()
        available_for = [loc.lower() for loc in profile.personal.get("available_for", [])]

        if (
            candidate_location in job_location
            or any(loc in job_location for loc in available_for)
            or job_analysis.remote_policy.lower() == "remote"
        ):
            scores["location_match"] = 100
        else:
            scores["location_match"] = 50

        # Salary Match
        job_salary_max = job_analysis.salary_range.get("max")
        candidate_min_salary = profile.preferences.get("min_salary_eur", 0)
        if job_salary_max and candidate_min_salary:
            if job_salary_max >= candidate_min_salary:
                scores["salary_match"] = 100
            else:
                scores["salary_match"] = int((job_salary_max / candidate_min_salary) * 100)
        else:
            scores["salary_match"] = 75  # Unknown

        # Culture Match (simple heuristic)
        scores["culture_match"] = 70  # Default

        # Role Type Match
        role_type = job_analysis.role_type
        preferences = profile.preferences
        avoid_roles = [r.lower() for r in preferences.get("avoid_roles", [])]
        ideal_roles = [r.lower() for r in preferences.get("ideal_roles", [])]

        role_match = 50  # Base score

        # Negative factors
        if role_type.is_sales and role_type.requires_quota:
            if any("sales" in avoid for avoid in avoid_roles):
                role_match -= 40

        if role_type.requires_coding:
            if any("developer" in avoid for avoid in avoid_roles):
                role_match -= 40

        # Positive factors
        if role_type.is_delivery or role_type.is_management:
            if any("program" in ideal or "delivery" in ideal for ideal in ideal_roles):
                role_match += 50

        if role_type.is_consulting:
            if any("consult" in ideal for ideal in ideal_roles):
                role_match += 30

        scores["role_type_match"] = max(0, min(100, role_match))

        # Calculate weighted total
        weights = {
            "experience_match": 0.20,
            "skills_match": 0.25,
            "education_match": 0.10,
            "location_match": 0.15,
            "salary_match": 0.10,
            "culture_match": 0.05,
            "role_type_match": 0.15,
        }

        total_score = sum(scores[key] * weights[key] for key in scores)

        # Find missing skills with better matching
        # Extract core skill terms from matched skills for better comparison
        matched_core_terms = set()
        for matched in matched_skills:
            # Extract key terms (words longer than 3 chars, excluding common words)
            words = matched.lower().split()
            for word in words:
                if len(word) > 3 and word not in ['years', 'experience', 'with', 'from', 'more', 'than', 'least']:
                    matched_core_terms.add(word)

        missing_skills = []
        for skill in required_skills:
            if skill in matched_skills:
                continue  # Already matched exactly

            # Check if core terms of this skill are already in matched skills
            skill_words = skill.lower().split()
            skill_core_terms = [w for w in skill_words if len(w) > 3 and w not in ['years', 'experience', 'with', 'from', 'more', 'than', 'least']]

            # If any core term is already matched, skip this requirement
            if any(term in matched_core_terms for term in skill_core_terms):
                continue

            missing_skills.append(skill)

        # Create detailed comparisons
        from backend.schemas.jobassistant import FitScoreDetail

        # Experience Detail
        experience_detail = FitScoreDetail(
            score=scores["experience_match"],
            candidate_value=f"{candidate_years}+ years",
            required_value=f"{required_years}+ years",
            comparison=f"{candidate_years}+ years vs. {required_years}+ years required"
        )

        # Skills Detail
        skills_detail = FitScoreDetail(
            score=scores["skills_match"],
            candidate_value=f"{len(matched_skills)} matched",
            required_value=f"{len(required_skills)} required",
            comparison=f"{len(matched_skills)}/{len(required_skills)} skills matched"
        )

        # Education Detail
        education_detail = FitScoreDetail(
            score=scores["education_match"],
            candidate_value=profile.education.get("degree", "Not specified"),
            required_value=job_analysis.requirements.education,
            comparison=f"{profile.education.get('degree', 'Not specified')} vs. {job_analysis.requirements.education}"
        )

        # Location Detail
        location_detail = FitScoreDetail(
            score=scores["location_match"],
            candidate_value=profile.personal.get("location", "Not specified"),
            required_value=f"{job_analysis.location} ({job_analysis.remote_policy})",
            comparison=f"{profile.personal.get('location', 'Not specified')} vs. {job_analysis.location}"
        )

        # Salary Detail
        job_salary_max = job_analysis.salary_range.get("max") or 0
        candidate_min_salary = profile.preferences.get("min_salary_eur") or 0
        salary_detail = FitScoreDetail(
            score=scores["salary_match"],
            candidate_value=f"€{candidate_min_salary:,}" if candidate_min_salary else "Not specified",
            required_value=f"€{job_salary_max:,}" if job_salary_max else "Not specified",
            comparison=f"Expected €{candidate_min_salary:,} vs. Offered €{job_salary_max:,}" if job_salary_max and candidate_min_salary else "Salary not disclosed"
        )

        # Culture Detail
        culture_hints = ", ".join(job_analysis.company_info.culture_hints[:3]) if job_analysis.company_info.culture_hints else "Not specified"
        culture_detail = FitScoreDetail(
            score=scores["culture_match"],
            candidate_value="Open to various cultures",
            required_value=culture_hints,
            comparison=f"Company culture: {culture_hints}"
        )

        # Role Type Detail
        role_types = []
        if role_type.is_technical: role_types.append("Technical")
        if role_type.is_management: role_types.append("Management")
        if role_type.is_sales: role_types.append("Sales")
        if role_type.is_consulting: role_types.append("Consulting")
        if role_type.is_delivery: role_types.append("Delivery")

        role_type_detail = FitScoreDetail(
            score=scores["role_type_match"],
            candidate_value=", ".join(ideal_roles) if ideal_roles else "Flexible",
            required_value=", ".join(role_types) if role_types else "General",
            comparison=f"Preference: {', '.join(ideal_roles) if ideal_roles else 'Flexible'} | Role: {', '.join(role_types) if role_types else 'General'}"
        )

        # Update breakdown with details
        breakdown_dict = {
            **scores,
            "experience_detail": experience_detail,
            "skills_detail": skills_detail,
            "education_detail": education_detail,
            "location_detail": location_detail,
            "salary_detail": salary_detail,
            "culture_detail": culture_detail,
            "role_type_detail": role_type_detail,
        }

        return FitScore(
            total=int(total_score),
            breakdown=FitScoreBreakdown(**breakdown_dict),
            matched_skills=matched_skills[:20],  # Limit to first 20
            missing_skills=missing_skills[:10],  # Limit to first 10
        )

    def calculate_probability(
        self,
        fit_score: FitScore,
        job_analysis: JobAnalysisResult,
        profile: UserProfileResponse,
    ) -> SuccessProbability:
        """
        Calculate success probability based on fit score and other factors.

        Args:
            fit_score: Calculated fit score
            job_analysis: Job analysis
            profile: Candidate profile

        Returns:
            Success probability with factors
        """
        base_probability = fit_score.total / 100.0  # 0.0 - 1.0
        factors = []

        # Competition Factor (based on company size)
        competition_factors = {
            "Enterprise": 0.7,
            "SMB": 0.9,
            "Startup": 0.85,
        }
        competition_factor = competition_factors.get(
            job_analysis.company_info.size, 0.8
        )
        base_probability *= competition_factor
        factors.append(
            ProbabilityFactor(
                factor=f"Competition ({job_analysis.company_info.size})",
                impact=competition_factor,
            )
        )

        # Overqualification
        required_max = job_analysis.requirements.years_experience.get("max", 999)
        candidate_years = profile.summary.get("years_experience", 0)
        years_over = candidate_years - required_max
        if years_over > 5:
            overqual_factor = 0.85
            base_probability *= overqual_factor
            factors.append(
                ProbabilityFactor(factor="Slightly overqualified", impact=overqual_factor)
            )

        # Location Bonus
        candidate_location = profile.personal.get("location", "").lower()
        job_location = job_analysis.location.lower()
        if (
            candidate_location in job_location
            or job_analysis.remote_policy.lower() == "remote"
        ):
            location_boost = 1.1
            base_probability *= location_boost
            factors.append(
                ProbabilityFactor(factor="Location Match", impact=location_boost)
            )

        # German Native Advantage
        unique_angles = profile.unique_angles
        required_languages = [
            lang.lower() for lang in job_analysis.requirements.languages
        ]
        if unique_angles.get("german_native") and "german" in required_languages:
            german_boost = 1.15
            base_probability *= german_boost
            factors.append(
                ProbabilityFactor(factor="German Native Advantage", impact=german_boost)
            )

        # KIT Alumni Connection (for specific companies)
        if unique_angles.get("kit_alumni"):
            # Companies with strong KIT connections
            kit_companies = ["giesecke+devrient", "sap", "siemens", "bosch"]
            if any(comp in job_analysis.company.lower() for comp in kit_companies):
                kit_boost = 1.3
                base_probability *= kit_boost
                factors.append(
                    ProbabilityFactor(
                        factor="KIT Alumni Connection", impact=kit_boost
                    )
                )

        # AI/Tech Bonus
        if unique_angles.get("ai_hands_on"):
            keywords_lower = [kw.lower() for kw in job_analysis.keywords]
            if any(ai_term in kw for kw in keywords_lower for ai_term in ["ai", "llm", "machine learning", "ml"]):
                ai_boost = 1.2
                base_probability *= ai_boost
                factors.append(
                    ProbabilityFactor(factor="AI Hands-on Experience", impact=ai_boost)
                )

        # Role Type Penalties
        if job_analysis.role_type.is_sales and job_analysis.role_type.requires_quota:
            sales_penalty = 0.6
            base_probability *= sales_penalty
            factors.append(
                ProbabilityFactor(
                    factor="Sales Role (no track record)", impact=sales_penalty
                )
            )

        if job_analysis.role_type.requires_coding:
            coding_penalty = 0.3
            base_probability *= coding_penalty
            factors.append(
                ProbabilityFactor(
                    factor="Coding Required (not primary skill)", impact=coding_penalty
                )
            )

        # Cap probability at reasonable bounds
        base_probability = min(base_probability, 0.45)  # Max 45%
        base_probability = max(base_probability, 0.05)  # Min 5%

        # Generate recommendation
        recommendation = self._get_probability_recommendation(base_probability)

        return SuccessProbability(
            probability=int(base_probability * 100),
            factors=factors,
            recommendation=recommendation,
        )

    def _get_probability_recommendation(self, prob: float) -> str:
        """Get recommendation based on probability."""
        if prob >= 0.35:
            return "🔥 Hohe Priorität - Unbedingt bewerben!"
        if prob >= 0.25:
            return "✅ Gute Chance - Bewerben empfohlen"
        if prob >= 0.15:
            return "⚠️ Moderate Chance - Bewerben wenn interessiert"
        if prob >= 0.10:
            return "🤔 Geringe Chance - Nur wenn sehr interessiert"
        return "❌ Sehr geringe Chance - Besser andere Stellen priorisieren"

    async def generate_cover_letter(
        self,
        job_analysis: JobAnalysisResult,
        profile: UserProfileResponse,
        fit_score: FitScore,
        existing_cover_letter: Optional[str] = None,
        provider: str = "anthropic",
        model: Optional[str] = None,
    ) -> str:
        """
        Generate a tailored cover letter.

        Args:
            job_analysis: Job analysis
            profile: Candidate profile
            fit_score: Fit score
            existing_cover_letter: Optional existing cover letter to use as reference/template
            provider: LLM provider
            model: Specific model

        Returns:
            Cover letter text
        """
        # Build context
        profile_summary = f"""
Name: {profile.personal.get('name')}
Title: {profile.personal.get('title')}
Location: {profile.personal.get('location')}
Experience: {profile.summary.get('years_experience')} years
Core Identity: {profile.summary.get('core_identity')}
Unique Value: {profile.summary.get('unique_value')}
"""

        # Get relevant experience highlights
        experience_highlights = []
        for exp in profile.experience[:3]:  # Top 3 experiences
            experience_highlights.append(
                f"- {exp.get('title')} at {exp.get('company')} ({exp.get('period')}): {', '.join(exp.get('highlights', [])[:2])}"
            )

        # Add existing cover letter section if provided
        existing_cl_section = ""
        if existing_cover_letter:
            existing_cl_section = f"""

EXISTING COVER LETTER (for reference - adapt style/tone):
{existing_cover_letter[:1000]}
"""

        prompt = f"""Write a professional, concise cover letter in English.

CANDIDATE:
{profile_summary}

Key Experience:
{chr(10).join(experience_highlights)}

JOB:
Company: {job_analysis.company}
Role: {job_analysis.role}
Location: {job_analysis.location}
Key Requirements: {', '.join(job_analysis.requirements.must_have[:5])}

FIT ANALYSIS:
- Matched Skills: {', '.join(fit_score.matched_skills[:8])}
- Missing Skills: {', '.join(fit_score.missing_skills[:3])}{existing_cl_section}

RULES:
1. Maximum 4-5 short paragraphs
2. No exaggerated claims
3. Concrete examples from experience
4. Include keywords from job description
5. Personal connection if applicable (e.g., KIT Alumni for German companies)
6. NEVER mention specific team sizes (not "380 employees")
7. Use "several hundred" instead of concrete numbers for large teams
8. Mention location if relevant (Barcelona-based for remote/hybrid)

STRUCTURE:
- Greeting (personalized if recruiter known, otherwise "Dear Hiring Manager")
- Opening Hook (why this role/company)
- Main Experience Match (2-3 relevant points)
- Unique Value Proposition
- Closing + Call to Action

Return ONLY the cover letter text, no explanations or metadata."""

        result = self.llm.generate(
            prompt=prompt,
            provider=provider,
            model=model,
            temperature=0.7,
            max_tokens=1500,
        )

        return result.get("response", "").strip()

    async def customize_cv(
        self,
        job_analysis: JobAnalysisResult,
        profile: Optional[UserProfileResponse],
        fit_score: FitScore,
        cv_text: Optional[str] = None,
        provider: str = "anthropic",
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Customize CV for specific job.

        Args:
            job_analysis: Job analysis
            profile: Candidate profile (optional - if None, returns basic recommendations)
            fit_score: Fit score
            cv_text: Optional CV text to use as base instead of profile
            provider: LLM provider
            model: Specific model

        Returns:
            CV customization instructions
        """
        # If no profile provided, return basic customization recommendations
        if profile is None:
            return {
                "headline": f"{job_analysis.role}",
                "summary": "Emphasize relevant experience and skills matching the job requirements",
                "skills_to_emphasize": fit_score.matched_skills[:5],
                "keywords_to_include": job_analysis.keywords[:8],
                "sections_to_include": ["experience", "education", "skills"],
                "note": "No profile available - using CV-only analysis"
            }

        prompt = f"""Customize the CV for this specific job.

CANDIDATE PROFILE:
Name: {profile.personal.get('name')}
Current Title: {profile.personal.get('title')}
Experience: {profile.summary.get('years_experience')} years

JOB:
Company: {job_analysis.company}
Role: {job_analysis.role}
Key Requirements: {', '.join(job_analysis.requirements.must_have[:8])}
Keywords: {', '.join(job_analysis.keywords[:10])}

RULES:
1. Adjust headline to match the role
2. Prioritize relevant experience
3. Incorporate keywords from job description
4. Shorten irrelevant details
5. Highlight matching certifications
6. NEVER mention specific team sizes
7. Mention AI experience only if relevant for the role
8. For PM roles: prioritize Cognizant experience
9. For Sales roles: prioritize Google Account Manager role
10. For Tech roles: emphasize technical skills

OUTPUT FORMAT (valid JSON only):
{{
  "headline": "Adjusted headline",
  "summary": "Adjusted summary (2-3 sentences)",
  "experience_order": ["company1", "company2", "company3"],
  "experience_highlights": {{
    "Cognizant": ["Adjusted bullet point 1", "Adjusted bullet point 2"],
    "Freelance": ["Adjusted bullet point 1"]
  }},
  "skills_to_emphasize": ["skill1", "skill2", "skill3"],
  "certifications_to_highlight": ["cert1", "cert2"],
  "sections_to_include": ["experience", "education", "certifications", "languages"],
  "sections_to_exclude": []
}}

Return ONLY valid JSON, nothing else."""

        result = self.llm.generate(
            prompt=prompt,
            provider=provider,
            model=model,
            temperature=0.3,
            max_tokens=2000,
        )

        # Parse JSON response
        response_text = result.get("response", "")

        # Extract JSON from markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)

        response_text = response_text.strip()
        return json.loads(response_text)

    # ========================================================================
    # CV-ONLY METHODS (without stored profile)
    # ========================================================================

    async def calculate_fit_score_from_cv(
        self,
        job_analysis: JobAnalysisResult,
        cv_text: str,
        provider: str = "grok"
    ) -> FitScore:
        """
        Calculate fit score using LLM intelligence with uploaded CV text.

        Uses LLM to intelligently analyze fit, avoiding algorithmic limitations.

        Args:
            job_analysis: Analyzed job data
            cv_text: Candidate's CV text
            provider: LLM provider for analysis

        Returns:
            Fit score with LLM-generated insights
        """
        if not cv_text or not cv_text.strip():
            # Return minimal score if no CV provided
            return FitScore(
                total=30,
                breakdown=FitScoreBreakdown(
                    experience_match=30,
                    skills_match=30,
                    education_match=30,
                    location_match=50,
                    salary_match=50,
                    culture_match=50,
                    role_type_match=30,
                ),
                matched_skills=[],
                missing_skills=job_analysis.requirements.must_have[:5],
            )

        # Use LLM intelligence instead of simple algorithms!
        from backend.schemas.jobassistant import FitScoreDetail

        # Safe value extraction with None handling
        min_salary = job_analysis.salary_range.get('min') or 0
        max_salary = job_analysis.salary_range.get('max') or 0
        min_exp = job_analysis.requirements.years_experience.get('min') or 0

        prompt = f"""Analyze the fit between this CV and job requirements. Use your intelligence - don't just match strings!

CV TEXT:
{cv_text[:4000]}

JOB REQUIREMENTS:
Company: {job_analysis.company}
Role: {job_analysis.role}
Location: {job_analysis.location} ({job_analysis.remote_policy})
Required Experience: {min_exp}+ years
Education: {job_analysis.requirements.education}
Must-Have Skills: {', '.join(job_analysis.requirements.must_have[:15])}
Nice-to-Have: {', '.join(job_analysis.requirements.nice_to_have[:10])}
Salary Range: €{min_salary:,} - €{max_salary:,}

BE SMART:
- If CV shows "Program Management", that covers "Project Management"
- If CV has "20 years", that exceeds "5+ years required"
- Match skills semantically (React developer = Frontend development)
- Don't list redundant missing skills (if "Project Management" matched, don't list "5+ years project management" as missing)

IMPORTANT - The "comparison" field must be ONE CONCISE SENTENCE explaining WHY!

Rules for comparison sentences:
- Maximum 15 words per sentence
- Be specific and direct
- Explain the reason for the score
- No lists, just a clear statement

Examples of GOOD comparisons (short and clear):
- experience_match: "20+ Jahre Erfahrung übertrifft die geforderten 5+ Jahre deutlich"
- skills_match: "7 von 10 Kernkompetenzen vorhanden, wichtigste Skills passen"
- education_match: "Master-Abschluss erfüllt Bachelor-Anforderung vollständig"
- location_match: "Barcelona-Madrid Distanz durch Remote-Option überbrückbar"
- salary_match: "Gehaltsvorstellung €100-120k passt zum Angebot €110-130k"
- culture_match: "Enterprise-Hintergrund passt zur professionellen Unternehmenskultur"
- role_type_match: "Technische und Management-Erfahrung deckt hybride Rolle ab"

Return JSON:
{{
  "experience_match": {{"score": 0-100, "candidate": "20+ Jahre", "required": "5+ Jahre", "comparison": "Eine prägnante deutsche Erklärung WARUM dieser Score"}},
  "skills_match": {{"score": 0-100, "candidate": "7 matched", "required": "10 total", "comparison": "Eine prägnante deutsche Erklärung WARUM dieser Score"}},
  "education_match": {{"score": 0-100, "candidate": "Master", "required": "Bachelor", "comparison": "Eine prägnante deutsche Erklärung WARUM dieser Score"}},
  "location_match": {{"score": 0-100, "candidate": "Barcelona", "required": "Madrid", "comparison": "Eine prägnante deutsche Erklärung WARUM dieser Score"}},
  "salary_match": {{"score": 0-100, "candidate": "€100-120k", "required": "€110-130k", "comparison": "Eine prägnante deutsche Erklärung WARUM dieser Score"}},
  "culture_match": {{"score": 0-100, "candidate": "Enterprise", "required": "Startup", "comparison": "Eine prägnante deutsche Erklärung WARUM dieser Score"}},
  "role_type_match": {{"score": 0-100, "candidate": "Technical", "required": "Management", "comparison": "Eine prägnante deutsche Erklärung WARUM dieser Score"}},
  "matched_skills": ["Python", "React", "Project Management", "etc"],
  "missing_skills": ["TypeScript", "GraphQL", "etc"]
}}

Return ONLY JSON."""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                provider=provider,
                temperature=0.3,
                max_tokens=2000
            )

            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON in LLM response")

            llm_data = json.loads(json_match.group())

            # Build detailed fit score from LLM analysis
            breakdown = FitScoreBreakdown(
                experience_match=llm_data['experience_match']['score'],
                skills_match=llm_data['skills_match']['score'],
                education_match=llm_data['education_match']['score'],
                location_match=llm_data['location_match']['score'],
                salary_match=llm_data['salary_match']['score'],
                culture_match=llm_data['culture_match']['score'],
                role_type_match=llm_data['role_type_match']['score'],
                experience_detail=FitScoreDetail(**llm_data['experience_match']),
                skills_detail=FitScoreDetail(**llm_data['skills_match']),
                education_detail=FitScoreDetail(**llm_data['education_match']),
                location_detail=FitScoreDetail(**llm_data['location_match']),
                salary_detail=FitScoreDetail(**llm_data['salary_match']),
                culture_detail=FitScoreDetail(**llm_data['culture_match']),
                role_type_detail=FitScoreDetail(**llm_data['role_type_match']),
            )

            weights = {
                "experience_match": 0.20,
                "skills_match": 0.25,
                "education_match": 0.10,
                "location_match": 0.15,
                "salary_match": 0.10,
                "culture_match": 0.05,
                "role_type_match": 0.15,
            }

            total = sum(llm_data[key]['score'] * weights[key] for key in weights)

            return FitScore(
                total=int(total),
                breakdown=breakdown,
                matched_skills=llm_data.get('matched_skills', [])[:20],
                missing_skills=llm_data.get('missing_skills', [])[:10],
            )

        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"LLM fit score failed: {e}, using fallback")
            # Fallback to basic scoring if LLM fails
            return FitScore(
                total=60,
                breakdown=FitScoreBreakdown(
                    experience_match=60, skills_match=60, education_match=60,
                    location_match=70, salary_match=70, culture_match=70,
                    role_type_match=60,
                ),
                matched_skills=[],
                missing_skills=job_analysis.requirements.must_have[:5],
            )

    def calculate_probability_simple(
        self,
        fit_score: FitScore,
        job_analysis: JobAnalysisResult,
    ) -> SuccessProbability:
        """
        Calculate success probability based on fit score only (no profile).

        Args:
            fit_score: Calculated fit score
            job_analysis: Job analysis data

        Returns:
            Success probability with factors
        """
        base_prob = fit_score.total / 100.0

        factors = []

        # Factor: Overall Fit
        if fit_score.total >= 80:
            factors.append(ProbabilityFactor(factor="Excellent overall fit", impact=1.3))
        elif fit_score.total >= 60:
            factors.append(ProbabilityFactor(factor="Good overall fit", impact=1.1))
        else:
            factors.append(ProbabilityFactor(factor="Below average fit", impact=0.8))

        # Factor: Skills Match
        if fit_score.breakdown.skills_match >= 80:
            factors.append(ProbabilityFactor(factor="Strong skills match", impact=1.2))
        elif fit_score.breakdown.skills_match < 50:
            factors.append(ProbabilityFactor(factor="Weak skills match", impact=0.7))

        # Calculate final probability
        probability = base_prob
        for factor in factors:
            probability *= factor.impact

        probability = min(max(probability * 100, 5), 95)

        recommendation = self._get_probability_recommendation(probability / 100)

        return SuccessProbability(
            probability=int(probability),
            factors=factors,
            recommendation=recommendation,
        )

    async def generate_cover_letter_from_cv(
        self,
        job_analysis: JobAnalysisResult,
        cv_text: str,
        fit_score: FitScore,
        existing_cover_letter: Optional[str] = None,
        provider: str = "anthropic",
        model: Optional[str] = None,
    ) -> str:
        """
        Generate cover letter using ONLY uploaded CV text (no stored profile).

        Args:
            job_analysis: Job analysis
            cv_text: Candidate's CV text
            fit_score: Fit score
            existing_cover_letter: Optional existing cover letter for reference
            provider: LLM provider
            model: Specific model

        Returns:
            Cover letter text
        """
        if not cv_text or not cv_text.strip():
            return "Please provide your CV text to generate a cover letter."

        # Add existing cover letter section if provided
        existing_cl_section = ""
        if existing_cover_letter:
            existing_cl_section = f"""

EXISTING COVER LETTER (for reference - adapt style/tone):
{existing_cover_letter[:1000]}
"""

        prompt = f"""Write a professional, concise cover letter in English.

CANDIDATE CV:
{cv_text[:3000]}

JOB:
Company: {job_analysis.company}
Role: {job_analysis.role}
Location: {job_analysis.location}
Key Requirements: {', '.join(job_analysis.requirements.must_have[:5])}

FIT ANALYSIS:
- Matched Skills: {', '.join(fit_score.matched_skills[:8])}
- Missing Skills: {', '.join(fit_score.missing_skills[:3])}{existing_cl_section}

RULES:
1. Maximum 4-5 short paragraphs
2. No exaggerated claims
3. Concrete examples from CV
4. Include keywords from job description
5. Professional and authentic tone

STRUCTURE:
- Greeting (personalized if recruiter known, otherwise "Dear Hiring Manager")
- Opening Hook (why this role/company)
- Main Experience Match (2-3 relevant points from CV)
- Unique Value Proposition
- Closing + Call to Action

Return ONLY the cover letter text, no explanations or metadata."""

        result = self.llm.generate(
            prompt=prompt,
            provider=provider,
            model=model,
            temperature=0.7,
            max_tokens=1500,
        )

        return result.get("response", "").strip()

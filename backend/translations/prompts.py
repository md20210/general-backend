"""
LLM Prompt Templates
Multi-language prompts for AI interactions
"""
from typing import Dict, Literal

Language = Literal["de", "en", "es"]

LLM_PROMPTS: Dict[str, Dict[Language, str]] = {
        "match_analysis": {
            "de": """Du bist ein erfahrener HR-Analyst. Analysiere gründlich die Übereinstimmung zwischen dieser Stellenbeschreibung und dem Bewerber-CV.

STELLENBESCHREIBUNG:
{job_description}

LEBENSLAUF:
{cv_text}

ANALYSIERE FOLGENDE ASPEKTE DETAILLIERT:

1. **Fachliche Qualifikationen**: Vergleiche jede Anforderung mit den Skills/Erfahrungen im CV
2. **Berufserfahrung**: Jahre, Branchen, Verantwortungsbereiche, Führungserfahrung
3. **Technische Skills**: Programmiersprachen, Frameworks, Tools, Zertifizierungen
4. **Soft Skills**: Teamfähigkeit, Kommunikation, Problemlösung (aus Projekten ableitbar)
5. **Kulturelle Passung**: Branchenerfahrung, Unternehmenstypen (Startup vs. Konzern)
6. **Entwicklungspotenzial**: Lernbereitschaft, Weiterbildungen, Karriereprogression

BEWERTUNGS-RICHTLINIEN:
- **overallScore**: 0-100%, basierend auf gewichteter Übereinstimmung aller Anforderungen
- **strengths**: Mindestens 5 konkrete Stärken mit Belegen aus dem CV
- **gaps**: Mindestens 3 identifizierte Lücken oder fehlende Qualifikationen
- **recommendations**: 3-5 konkrete, umsetzbare Empfehlungen (Weiterbildung, Training, Erfahrung sammeln)
- **detailedAnalysis**: 3-5 Absätze mit tiefgehender Analyse (Warum der Score? Welche Faktoren? Zukunftspotenzial?)
- **comparison**: ALLE Hauptanforderungen einzeln bewerten (mindestens 8 Items!)
  - requirement: Exakte Anforderung aus Stellenbeschreibung
  - applicant_match: Konkrete Qualifikation/Erfahrung aus CV
  - details: Detaillierte Begründung der Bewertung (1-2 Sätze!)
  - match_level: "full" (100% erfüllt), "partial" (teilweise), "missing" (nicht vorhanden)
  - confidence: 0-100% wie sicher die Bewertung ist

ANALYSIERE NUR DIE TATSÄCHLICHEN DATEN AUS DEN DOKUMENTEN OBEN!
ERFINDE KEINE INFORMATIONEN! NUR WAS WIRKLICH IM CV UND DER STELLENBESCHREIBUNG STEHT!

GIB NUR DIESES JSON-FORMAT ZURÜCK (mit echten Daten aus den Dokumenten):
{{
  "overallScore": [Zahl 0-100 basierend auf echter Übereinstimmung],
  "strengths": [
    "[Echte Stärke aus CV mit konkreten Jahren/Projekten]",
    "[Weitere echte Stärke...]",
    "[Mindestens 5 Stärken aus dem echten CV]"
  ],
  "gaps": [
    "[Echte Lücke basierend auf Stellenbeschreibung]",
    "[Weitere echte Lücke...]",
    "[Mindestens 3 Lücken]"
  ],
  "recommendations": [
    "[Konkrete Empfehlung basierend auf identifizierten Lücken]",
    "[Weitere Empfehlung...]",
    "[3-5 Empfehlungen]"
  ],
  "detailedAnalysis": "[3-5 Absätze mit Analyse der ECHTEN Qualifikationen, ECHTEN Jahre Erfahrung, ECHTEN Unternehmen aus dem CV. Mindestens 300 Wörter. NUR FAKTEN AUS DEN DOKUMENTEN!]",
  "comparison": [
    {{
      "requirement": "[Exakte Anforderung aus Stellenbeschreibung]",
      "applicant_match": "[Was WIRKLICH im CV steht - exakte Jahre, Unternehmen, Skills]",
      "details": "[Begründung basierend auf echten Daten - 1-2 Sätze]",
      "match_level": "[full/partial/missing]",
      "confidence": [0-100]
    }}
  ]
}}

WICHTIG:
- match_level NUR: "full", "partial" oder "missing"
- Mindestens 8 comparison items (ALLE Hauptanforderungen einzeln!)
- detailedAnalysis mindestens 300 Wörter
- Alle Texte auf Deutsch
- NUR JSON zurückgeben, kein zusätzlicher Text

JSON:""",
            "en": """You are an experienced HR analyst. Thoroughly analyze the match between this job description and the applicant's CV.

JOB DESCRIPTION:
{job_description}

CURRICULUM VITAE:
{cv_text}

ANALYZE THE FOLLOWING ASPECTS IN DETAIL:

1. **Professional Qualifications**: Compare each requirement with skills/experience in CV
2. **Work Experience**: Years, industries, areas of responsibility, leadership experience
3. **Technical Skills**: Programming languages, frameworks, tools, certifications
4. **Soft Skills**: Teamwork, communication, problem-solving (derivable from projects)
5. **Cultural Fit**: Industry experience, company types (startup vs. corporation)
6. **Development Potential**: Learning willingness, continuing education, career progression

EVALUATION GUIDELINES:
- **overallScore**: 0-100%, based on weighted match of all requirements
- **strengths**: At least 5 concrete strengths with evidence from CV
- **gaps**: At least 3 identified gaps or missing qualifications
- **recommendations**: 3-5 concrete, actionable recommendations (training, education, gaining experience)
- **detailedAnalysis**: 3-5 paragraphs with in-depth analysis (Why this score? Which factors? Future potential?)
- **comparison**: Evaluate ALL main requirements individually (at least 8 items!)
  - requirement: Exact requirement from job description
  - applicant_match: Concrete qualification/experience from CV
  - details: Detailed justification of evaluation (1-2 sentences!)
  - match_level: "full" (100% met), "partial" (partially met), "missing" (not present)
  - confidence: 0-100% how certain the evaluation is

ANALYZE ONLY THE ACTUAL DATA FROM THE DOCUMENTS ABOVE!
DO NOT INVENT INFORMATION! ONLY WHAT IS REALLY IN THE CV AND JOB DESCRIPTION!

RETURN ONLY THIS JSON FORMAT (with real data from the documents):
{{
  "overallScore": [Number 0-100 based on actual match],
  "strengths": [
    "[Real strength from CV with concrete years/projects]",
    "[Another real strength...]",
    "[At least 5 strengths from the actual CV]"
  ],
  "gaps": [
    "[Real gap based on job description]",
    "[Another real gap...]",
    "[At least 3 gaps]"
  ],
  "recommendations": [
    "[Concrete recommendation based on identified gaps]",
    "[Another recommendation...]",
    "[3-5 recommendations]"
  ],
  "detailedAnalysis": "[3-5 paragraphs analyzing REAL qualifications, REAL years of experience, REAL companies from CV. At least 300 words. ONLY FACTS FROM THE DOCUMENTS!]",
  "comparison": [
    {{
      "requirement": "[Exact requirement from job description]",
      "applicant_match": "[What is REALLY in the CV - exact years, companies, skills]",
      "details": "[Justification based on real data - 1-2 sentences]",
      "match_level": "[full/partial/missing]",
      "confidence": [0-100]
    }}
  ]
}}

IMPORTANT:
- match_level ONLY: "full", "partial" or "missing"
- At least 8 comparison items (ALL main requirements individually!)
- detailedAnalysis at least 300 words
- All texts in English
- ONLY return JSON, no additional text

JSON:""",
            "es": """Eres un analista de RRHH experimentado. Analiza a fondo la coincidencia entre esta descripción del puesto y el CV del candidato.

DESCRIPCIÓN DEL PUESTO:
{job_description}

CURRICULUM VITAE:
{cv_text}

ANALIZA LOS SIGUIENTES ASPECTOS EN DETALLE:

1. **Cualificaciones Profesionales**: Compara cada requisito con las habilidades/experiencia en el CV
2. **Experiencia Laboral**: Años, industrias, áreas de responsabilidad, experiencia de liderazgo
3. **Habilidades Técnicas**: Lenguajes de programación, frameworks, herramientas, certificaciones
4. **Habilidades Blandas**: Trabajo en equipo, comunicación, resolución de problemas (derivable de proyectos)
5. **Ajuste Cultural**: Experiencia en la industria, tipos de empresas (startup vs. corporación)
6. **Potencial de Desarrollo**: Voluntad de aprender, formación continua, progresión profesional

DIRECTRICES DE EVALUACIÓN:
- **overallScore**: 0-100%, basado en coincidencia ponderada de todos los requisitos
- **strengths**: Al menos 5 fortalezas concretas con evidencia del CV
- **gaps**: Al menos 3 brechas identificadas o cualificaciones faltantes
- **recommendations**: 3-5 recomendaciones concretas y accionables (capacitación, educación, ganar experiencia)
- **detailedAnalysis**: 3-5 párrafos con análisis profundo (¿Por qué esta puntuación? ¿Qué factores? ¿Potencial futuro?)
- **comparison**: Evaluar TODOS los requisitos principales individualmente (¡al menos 8 elementos!)
  - requirement: Requisito exacto de la descripción del puesto
  - applicant_match: Cualificación/experiencia concreta del CV
  - details: Justificación detallada de la evaluación (¡1-2 frases!)
  - match_level: "full" (100% cumplido), "partial" (parcialmente cumplido), "missing" (no presente)
  - confidence: 0-100% qué tan segura es la evaluación

¡ANALIZA SOLO LOS DATOS REALES DE LOS DOCUMENTOS ANTERIORES!
¡NO INVENTES INFORMACIÓN! ¡SOLO LO QUE REALMENTE ESTÁ EN EL CV Y LA DESCRIPCIÓN DEL PUESTO!

DEVUELVE SOLO ESTE FORMATO JSON (con datos reales de los documentos):
{{
  "overallScore": [Número 0-100 basado en coincidencia real],
  "strengths": [
    "[Fortaleza real del CV con años/proyectos concretos]",
    "[Otra fortaleza real...]",
    "[Al menos 5 fortalezas del CV real]"
  ],
  "gaps": [
    "[Brecha real basada en descripción del puesto]",
    "[Otra brecha real...]",
    "[Al menos 3 brechas]"
  ],
  "recommendations": [
    "[Recomendación concreta basada en brechas identificadas]",
    "[Otra recomendación...]",
    "[3-5 recomendaciones]"
  ],
  "detailedAnalysis": "[3-5 párrafos analizando cualificaciones REALES, años REALES de experiencia, empresas REALES del CV. Al menos 300 palabras. ¡SOLO HECHOS DE LOS DOCUMENTOS!]",
  "comparison": [
    {{
      "requirement": "[Requisito exacto de la descripción del puesto]",
      "applicant_match": "[Lo que REALMENTE está en el CV - años exactos, empresas, habilidades]",
      "details": "[Justificación basada en datos reales - 1-2 frases]",
      "match_level": "[full/partial/missing]",
      "confidence": [0-100]
    }}
  ]
}}

IMPORTANTE:
- match_level SOLO: "full", "partial" o "missing"
- Al menos 8 elementos de comparación (¡TODOS los requisitos principales individualmente!)
- detailedAnalysis al menos 300 palabras
- Todos los textos en español
- SOLO devuelve JSON, sin texto adicional

JSON:"""
        },
        "chat_rag_prompt": {
            "de": """System-Kontext:
{system_context}

Relevante Dokumente:
{context}

Benutzerfrage: {message}

Beantworte die Frage auf Deutsch basierend auf dem System-Kontext und den relevanten Dokumenten.""",
            "en": """System Context:
{system_context}

Relevant Documents:
{context}

User Question: {message}

Answer the question in English based on the system context and relevant documents.""",
            "es": """Contexto del Sistema:
{system_context}

Documentos Relevantes:
{context}

Pregunta del Usuario: {message}

Responde la pregunta en español basándote en el contexto del sistema y los documentos relevantes."""
        },

        # PrivateGxT Translations
        "app_title": {
            "de": "PrivateGxT",
            "en": "PrivateGxT",
            "es": "PrivateGxT"
        },
        "app_subtitle": {
            "de": "RAG-gestützte Dokumenten-Unterhaltung mit Multi-LLM-Gateway",
            "en": "RAG-powered Document Chat with Multi-LLM Gateway",
            "es": "Chat de Documentos con RAG y Gateway Multi-LLM"
        },
        "upload_title": {
            "de": "Dokument hochladen",
            "en": "Upload Document",
            "es": "Subir Documento"
        },
        "upload_drag_drop": {
            "de": "Datei hierher ziehen oder klicken zum Auswählen",
            "en": "Drag & drop file here or click to select",
            "es": "Arrastra y suelta el archivo aquí o haz clic para seleccionar"
        },
        "upload_supported_formats": {
            "de": "PDF, DOCX, TXT (max. 10 MB)",
            "en": "PDF, DOCX, TXT (max 10 MB)",
            "es": "PDF, DOCX, TXT (máx. 10 MB)"
        },
        "uploading": {
            "de": "Wird hochgeladen...",
            "en": "Uploading...",
            "es": "Subiendo..."
        },
        "upload_error_type": {
            "de": "Ungültiger Dateityp. Nur PDF, DOCX und TXT erlaubt.",
            "en": "Invalid file type. Only PDF, DOCX, and TXT allowed.",
            "es": "Tipo de archivo no válido. Solo se permiten PDF, DOCX y TXT."
        },
        "upload_error_size": {
            "de": "Datei zu groß. Maximale Größe: 10 MB.",
            "en": "File too large. Maximum size: 10 MB.",
            "es": "Archivo demasiado grande. Tamaño máximo: 10 MB."
        },
        "upload_error_generic": {
            "de": "Fehler beim Hochladen. Bitte versuchen Sie es erneut.",
            "en": "Upload failed. Please try again.",
            "es": "Error al subir. Por favor, inténtalo de nuevo."
        },
        "documents_title": {
            "de": "Dokumente",
            "en": "Documents",
            "es": "Documentos"
        },
        "no_documents": {
            "de": "Noch keine Dokumente hochgeladen",
            "en": "No documents uploaded yet",
            "es": "Aún no se han subido documentos"
        },
        "chunks": {
            "de": "Abschnitte",
            "en": "chunks",
            "es": "fragmentos"
        },
        "delete_document": {
            "de": "Dokument löschen",
            "en": "Delete document",
            "es": "Eliminar documento"
        },
        "clear_all": {
            "de": "Alle löschen",
            "en": "Clear All",
            "es": "Borrar Todo"
        },
        "confirm_delete": {
            "de": "Möchten Sie dieses Dokument wirklich löschen?",
            "en": "Are you sure you want to delete this document?",
            "es": "¿Estás seguro de que quieres eliminar este documento?"
        },
        "confirm_clear_all": {
            "de": "Möchten Sie wirklich alle Dokumente und den Chat-Verlauf löschen?",
            "en": "Are you sure you want to clear all documents and chat history?",
            "es": "¿Estás seguro de que quieres borrar todos los documentos y el historial de chat?"
        },
        "delete_error": {
            "de": "Fehler beim Löschen des Dokuments",
            "en": "Failed to delete document",
            "es": "Error al eliminar el documento"
        },
        "clear_error": {
            "de": "Fehler beim Löschen aller Daten",
            "en": "Failed to clear all data",
            "es": "Error al borrar todos los datos"
        },
        "chat_title": {
            "de": "Chat mit Ihren Dokumenten",
            "en": "Chat with Your Documents",
            "es": "Chatea con Tus Documentos"
        },
        "chat_empty": {
            "de": "Noch keine Nachrichten",
            "en": "No messages yet",
            "es": "Aún no hay mensajes"
        },
        "chat_ask_question": {
            "de": "Stellen Sie eine Frage zu Ihren Dokumenten",
            "en": "Ask a question about your documents",
            "es": "Haz una pregunta sobre tus documentos"
        },
        "chat_upload_first": {
            "de": "Laden Sie zuerst ein Dokument hoch",
            "en": "Upload a document first",
            "es": "Sube primero un documento"
        },
        "chat_input_placeholder": {
            "de": "Stellen Sie eine Frage...",
            "en": "Ask a question...",
            "es": "Haz una pregunta..."
        },
        "chat_error": {
            "de": "Fehler beim Senden der Nachricht",
            "en": "Failed to send message",
            "es": "Error al enviar el mensaje"
        },
        "sources": {
            "de": "Quellen",
            "en": "Sources",
            "es": "Fuentes"
        },
        "chunk": {
            "de": "Abschnitt",
            "en": "Chunk",
            "es": "Fragmento"
        },
        "stats_documents": {
            "de": "Dokumente",
            "en": "Documents",
            "es": "Documentos"
        },
        "stats_chunks": {
            "de": "Abschnitte",
            "en": "Chunks",
            "es": "Fragmentos"
        },
        "stats_messages": {
            "de": "Nachrichten",
            "en": "Messages",
            "es": "Mensajes"
        },
        "footer_powered_by": {
            "de": "Powered by",
            "en": "Powered by",
            "es": "Desarrollado con"
        }
    }

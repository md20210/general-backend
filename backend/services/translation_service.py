"""
Translation Service for CV Matcher
Provides multi-language support for UI and LLM prompts
"""
from typing import Dict, Optional, Literal
from enum import Enum

Language = Literal["de", "en", "es"]


class TranslationService:
    """
    Centralized translation service for CV Matcher application.

    Features:
    - Static UI translations (DE/EN/ES)
    - LLM prompt templates in multiple languages
    - Fallback to English if translation missing
    """

    # UI Translations
    UI_TRANSLATIONS: Dict[str, Dict[Language, str]] = {
        # Header
        "app_title": {
            "de": "CV Matcher",
            "en": "CV Matcher",
            "es": "CV Matcher"
        },
        "llm_toggle_local": {
            "de": "🏠 Lokal (DSGVO)",
            "en": "🏠 Local (GDPR)",
            "es": "🏠 Local (RGPD)"
        },
        "llm_toggle_grok": {
            "de": "⚡ GROK (nicht DSGVO)",
            "en": "⚡ GROK (non-GDPR)",
            "es": "⚡ GROK (no RGPD)"
        },

        # Document Section
        "employer_section_title": {
            "de": "Arbeitgeber Dokumente",
            "en": "Employer Documents",
            "es": "Documentos del Empleador"
        },
        "applicant_section_title": {
            "de": "Bewerber Dokumente",
            "en": "Applicant Documents",
            "es": "Documentos del Candidato"
        },
        "upload_button": {
            "de": "Dokument hochladen",
            "en": "Upload Document",
            "es": "Subir Documento"
        },
        "drag_drop_text": {
            "de": "Datei hierher ziehen oder klicken",
            "en": "Drag file here or click",
            "es": "Arrastra el archivo aquí o haz clic"
        },
        "delete_button": {
            "de": "Löschen",
            "en": "Delete",
            "es": "Eliminar"
        },

        # Document Section - Tabs
        "doc_tab_upload": {
            "de": "Hochladen",
            "en": "Upload",
            "es": "Subir"
        },
        "doc_tab_url": {
            "de": "URL",
            "en": "URL",
            "es": "URL"
        },
        "doc_tab_text": {
            "de": "Text",
            "en": "Text",
            "es": "Texto"
        },

        # Document Section - Upload
        "doc_drop_file": {
            "de": "Datei hier ablegen oder",
            "en": "Drop file here or",
            "es": "Arrastra el archivo aquí o"
        },
        "doc_select_file": {
            "de": "Datei auswählen",
            "en": "Select File",
            "es": "Seleccionar Archivo"
        },
        "doc_loading": {
            "de": "Lädt...",
            "en": "Loading...",
            "es": "Cargando..."
        },

        # Document Section - URL
        "doc_url_placeholder": {
            "de": "https://example.com/stellenanzeige",
            "en": "https://example.com/job-posting",
            "es": "https://example.com/oferta-empleo"
        },
        "doc_add_url": {
            "de": "URL hinzufügen",
            "en": "Add URL",
            "es": "Agregar URL"
        },

        # Document Section - Text
        "doc_text_placeholder": {
            "de": "Text hier eingeben...",
            "en": "Enter text here...",
            "es": "Ingresa texto aquí..."
        },
        "doc_add_text": {
            "de": "Text hinzufügen",
            "en": "Add Text",
            "es": "Agregar Texto"
        },

        # Document Section - List
        "doc_no_documents": {
            "de": "Keine Dokumente hinzugefügt",
            "en": "No documents added",
            "es": "No se agregaron documentos"
        },
        "doc_preview": {
            "de": "Vorschau",
            "en": "Preview",
            "es": "Vista previa"
        },
        "doc_delete": {
            "de": "Löschen",
            "en": "Delete",
            "es": "Eliminar"
        },

        # Document Section - Preview Modal
        "doc_type_file": {
            "de": "Datei",
            "en": "File",
            "es": "Archivo"
        },
        "doc_type_url": {
            "de": "URL",
            "en": "URL",
            "es": "URL"
        },
        "doc_type_text": {
            "de": "Text",
            "en": "Text",
            "es": "Texto"
        },
        "doc_content_length": {
            "de": "Inhaltslänge",
            "en": "Content length",
            "es": "Longitud del contenido"
        },
        "doc_characters": {
            "de": "Zeichen",
            "en": "characters",
            "es": "caracteres"
        },
        "doc_close": {
            "de": "Schließen",
            "en": "Close",
            "es": "Cerrar"
        },
        "doc_summary_button": {
            "de": "📊 Zusammenfassung",
            "en": "📊 Summary",
            "es": "📊 Resumen"
        },
        "doc_summary_title": {
            "de": "Zusammenfassung",
            "en": "Summary",
            "es": "Resumen"
        },
        "doc_summary_loading": {
            "de": "Generiere Zusammenfassung...",
            "en": "Generating summary...",
            "es": "Generando resumen..."
        },
        "doc_summary_total_docs": {
            "de": "Dokumente gesamt",
            "en": "Total documents",
            "es": "Documentos totales"
        },
        "doc_summary_total_content": {
            "de": "Gesamtinhalt",
            "en": "Total content",
            "es": "Contenido total"
        },
        "doc_summary_words": {
            "de": "Wörter",
            "en": "words",
            "es": "palabras"
        },
        "doc_summary_details": {
            "de": "Dokumente Details",
            "en": "Document Details",
            "es": "Detalles de Documentos"
        },

        # Job Description Input
        "job_desc_title": {
            "de": "Stellenbeschreibung eingeben",
            "en": "Enter Job Description",
            "es": "Ingresar Descripción del Puesto"
        },
        "job_desc_subtitle": {
            "de": "Fügen Sie die Stellenbeschreibung ein, um sie mit dem Lebenslauf zu vergleichen",
            "en": "Paste the job description to compare it with the resume",
            "es": "Pegue la descripción del puesto para compararla con el currículum"
        },
        "job_title_label": {
            "de": "Stellentitel (optional)",
            "en": "Job Title (optional)",
            "es": "Título del Puesto (opcional)"
        },
        "job_title_placeholder": {
            "de": "z.B. Senior Software Engineer",
            "en": "e.g. Senior Software Engineer",
            "es": "ej. Ingeniero de Software Senior"
        },
        "company_name_label": {
            "de": "Unternehmen (optional)",
            "en": "Company (optional)",
            "es": "Empresa (opcional)"
        },
        "company_name_placeholder": {
            "de": "z.B. Tech Company GmbH",
            "en": "e.g. Tech Company Inc.",
            "es": "ej. Tech Company SA"
        },
        "job_description_label": {
            "de": "Stellenbeschreibung *",
            "en": "Job Description *",
            "es": "Descripción del Puesto *"
        },
        "characters": {
            "de": "Zeichen",
            "en": "characters",
            "es": "caracteres"
        },
        "job_description_placeholder": {
            "de": "Fügen Sie hier die vollständige Stellenbeschreibung ein...\n\nBeispiel:\nWir suchen einen erfahrenen Software Engineer für unser Team...\n\nAnforderungen:\n- 5+ Jahre Erfahrung in der Softwareentwicklung\n- Kenntnisse in React, TypeScript, Node.js\n- Erfahrung mit Cloud-Technologien (AWS, Azure)\n...",
            "en": "Paste the complete job description here...\n\nExample:\nWe are looking for an experienced Software Engineer for our team...\n\nRequirements:\n- 5+ years of software development experience\n- Knowledge of React, TypeScript, Node.js\n- Experience with cloud technologies (AWS, Azure)\n...",
            "es": "Pegue la descripción completa del puesto aquí...\n\nEjemplo:\nBuscamos un Ingeniero de Software experimentado para nuestro equipo...\n\nRequisitos:\n- 5+ años de experiencia en desarrollo de software\n- Conocimiento de React, TypeScript, Node.js\n- Experiencia con tecnologías en la nube (AWS, Azure)\n..."
        },
        "job_desc_min_required": {
            "de": "Mindestens {count} Zeichen erforderlich",
            "en": "At least {count} characters required",
            "es": "Al menos {count} caracteres requeridos"
        },
        "job_desc_chars_remaining": {
            "de": "Noch {count} Zeichen erforderlich",
            "en": "Still {count} characters required",
            "es": "Aún se requieren {count} caracteres"
        },
        "job_desc_ready": {
            "de": "Stellenbeschreibung ist bereit für die Analyse",
            "en": "Job description is ready for analysis",
            "es": "La descripción del puesto está lista para el análisis"
        },
        "analyze_match": {
            "de": "Match analysieren",
            "en": "Analyze Match",
            "es": "Analizar Coincidencia"
        },
        "reset": {
            "de": "Zurücksetzen",
            "en": "Reset",
            "es": "Restablecer"
        },
        "job_desc_error_empty": {
            "de": "Bitte geben Sie eine Stellenbeschreibung ein",
            "en": "Please enter a job description",
            "es": "Por favor ingrese una descripción del puesto"
        },
        "job_desc_error_min_chars": {
            "de": "Die Stellenbeschreibung muss mindestens {count} Zeichen enthalten",
            "en": "The job description must contain at least {count} characters",
            "es": "La descripción del puesto debe contener al menos {count} caracteres"
        },

        # Matching View
        "match_button": {
            "de": "Match Starten",
            "en": "Start Match",
            "es": "Iniciar Match"
        },
        "analyzing": {
            "de": "Analysiere...",
            "en": "Analyzing...",
            "es": "Analizando..."
        },
        "progress_loading_docs": {
            "de": "Dokumente werden geladen...",
            "en": "Loading documents...",
            "es": "Cargando documentos..."
        },
        "progress_analyzing_employer": {
            "de": "Arbeitgeber-Anforderungen werden analysiert...",
            "en": "Analyzing employer requirements...",
            "es": "Analizando requisitos del empleador..."
        },
        "progress_analyzing_applicant": {
            "de": "Bewerber-Profil wird analysiert...",
            "en": "Analyzing applicant profile...",
            "es": "Analizando perfil del candidato..."
        },
        "progress_llm_running": {
            "de": "LLM-Analyse läuft...",
            "en": "LLM analysis running...",
            "es": "Análisis LLM en progreso..."
        },
        "progress_generating_results": {
            "de": "Ergebnisse werden generiert...",
            "en": "Generating results...",
            "es": "Generando resultados..."
        },
        "progress_finalizing": {
            "de": "Finalisierung...",
            "en": "Finalizing...",
            "es": "Finalizando..."
        },
        "progress_completed": {
            "de": "Abgeschlossen!",
            "en": "Completed!",
            "es": "¡Completado!"
        },

        # Results
        "match_high": {
            "de": "Sehr gute Übereinstimmung",
            "en": "Excellent Match",
            "es": "Excelente Coincidencia"
        },
        "match_medium": {
            "de": "Mittlere Übereinstimmung",
            "en": "Moderate Match",
            "es": "Coincidencia Moderada"
        },
        "match_low": {
            "de": "Geringe Übereinstimmung",
            "en": "Low Match",
            "es": "Baja Coincidencia"
        },
        "strengths_title": {
            "de": "Stärken",
            "en": "Strengths",
            "es": "Fortalezas"
        },
        "gaps_title": {
            "de": "Lücken",
            "en": "Gaps",
            "es": "Brechas"
        },
        "recommendations_title": {
            "de": "Empfehlungen",
            "en": "Recommendations",
            "es": "Recomendaciones"
        },
        "detailed_analysis_title": {
            "de": "Detaillierte Analyse",
            "en": "Detailed Analysis",
            "es": "Análisis Detallado"
        },
        "comparison_title": {
            "de": "Detaillierter Vergleich",
            "en": "Detailed Comparison",
            "es": "Comparación Detallada"
        },
        "comparison_requirement": {
            "de": "Anforderung",
            "en": "Requirement",
            "es": "Requisito"
        },
        "comparison_applicant_match": {
            "de": "Bewerber Match",
            "en": "Applicant Match",
            "es": "Coincidencia del Candidato"
        },
        "comparison_details": {
            "de": "Einzelheiten",
            "en": "Details",
            "es": "Detalles"
        },
        "comparison_level": {
            "de": "Stufe",
            "en": "Level",
            "es": "Nivel"
        },
        "comparison_confidence": {
            "de": "Sicherheit",
            "en": "Confidence",
            "es": "Confianza"
        },
        "match_level_full": {
            "de": "Vollständig",
            "en": "Full",
            "es": "Completo"
        },
        "match_level_partial": {
            "de": "Teilweise",
            "en": "Partial",
            "es": "Parcial"
        },
        "match_level_missing": {
            "de": "Fehlend",
            "en": "Missing",
            "es": "Ausente"
        },

        # PDF Download
        "pdf_download_button": {
            "de": "PDF-Report herunterladen",
            "en": "Download PDF Report",
            "es": "Descargar Informe PDF"
        },
        "pdf_generating": {
            "de": "PDF wird generiert...",
            "en": "Generating PDF...",
            "es": "Generando PDF..."
        },
        "pdf_with_chat": {
            "de": "mit {count} Chat-Nachrichten",
            "en": "with {count} chat messages",
            "es": "con {count} mensajes de chat"
        },

        # Chat
        "chat_title": {
            "de": "💬 Interaktiver Chat",
            "en": "💬 Interactive Chat",
            "es": "💬 Chat Interactivo"
        },
        "chat_clear_button": {
            "de": "Verlauf löschen",
            "en": "Clear History",
            "es": "Borrar Historial"
        },
        "chat_empty_message": {
            "de": "Stellen Sie Fragen zur Analyse oder zu den hochgeladenen Dokumenten.",
            "en": "Ask questions about the analysis or uploaded documents.",
            "es": "Haga preguntas sobre el análisis o los documentos subidos."
        },
        "chat_examples": {
            "de": "Beispiele:",
            "en": "Examples:",
            "es": "Ejemplos:"
        },
        "chat_example_1": {
            "de": "Warum ist der Match Score 75%?",
            "en": "Why is the match score 75%?",
            "es": "¿Por qué la puntuación es del 75%?"
        },
        "chat_example_2": {
            "de": "Welche Skills fehlen noch?",
            "en": "Which skills are missing?",
            "es": "¿Qué habilidades faltan?"
        },
        "chat_example_3": {
            "de": "Hat der Bewerber AWS Erfahrung?",
            "en": "Does the applicant have AWS experience?",
            "es": "¿Tiene el candidato experiencia con AWS?"
        },
        "chat_input_placeholder": {
            "de": "Frage eingeben...",
            "en": "Enter question...",
            "es": "Ingrese pregunta..."
        },
        "chat_send_button": {
            "de": "Senden",
            "en": "Send",
            "es": "Enviar"
        },
        "chat_user_label": {
            "de": "Sie",
            "en": "You",
            "es": "Usted"
        },
        "chat_assistant_label": {
            "de": "Assistent",
            "en": "Assistant",
            "es": "Asistente"
        },
        "chat_sources_label": {
            "de": "Quellen:",
            "en": "Sources:",
            "es": "Fuentes:"
        },

        # Error Messages
        "error_upload_failed": {
            "de": "Upload fehlgeschlagen: {error}",
            "en": "Upload failed: {error}",
            "es": "Error al subir: {error}"
        },
        "error_analysis_failed": {
            "de": "Fehler bei der Analyse. Bitte versuchen Sie es erneut.",
            "en": "Analysis error. Please try again.",
            "es": "Error en el análisis. Por favor, inténtelo de nuevo."
        },
        "error_need_documents": {
            "de": "Bitte fügen Sie Dokumente für beide Seiten hinzu",
            "en": "Please add documents for both sides",
            "es": "Por favor agregue documentos para ambos lados"
        },
        "error_pdf_failed": {
            "de": "PDF-Generierung fehlgeschlagen: {error}",
            "en": "PDF generation failed: {error}",
            "es": "Error al generar PDF: {error}"
        },
        "error_no_claims": {
            "de": "Bitte wählen Sie mindestens eine Qualifikation aus und geben Sie eine Begründung ein",
            "en": "Please select at least one qualification and provide a justification",
            "es": "Por favor seleccione al menos una calificación y proporcione una justificación"
        },
        "error_cv_regenerate_failed": {
            "de": "CV-Generierung fehlgeschlagen",
            "en": "CV generation failed",
            "es": "Error al generar CV"
        },

        # Gap Claims Section
        "gap_claims_title": {
            "de": "Qualifikationen nachtragen",
            "en": "Add Missing Qualifications",
            "es": "Agregar Calificaciones Faltantes"
        },
        "gap_claims_description": {
            "de": "Die Analyse hat einige Qualifikationen als fehlend markiert. Falls Sie diese Fähigkeiten tatsächlich besitzen, können Sie sie hier nachweisen. Wir erstellen dann einen aktualisierten Lebenslauf, der diese Kompetenzen hervorhebt.",
            "en": "The analysis marked some qualifications as missing. If you actually possess these skills, you can document them here. We will then create an updated resume highlighting these competencies.",
            "es": "El análisis marcó algunas calificaciones como faltantes. Si realmente posee estas habilidades, puede documentarlas aquí. Luego crearemos un currículum actualizado que destaque estas competencias."
        },
        "gap_claims_i_have_this": {
            "de": "Diese Qualifikation besitze ich",
            "en": "I have this qualification",
            "es": "Tengo esta calificación"
        },
        "gap_claims_justification": {
            "de": "Begründung / Nachweis",
            "en": "Justification / Evidence",
            "es": "Justificación / Evidencia"
        },
        "gap_claims_justification_placeholder": {
            "de": "z.B. '5 Jahre Erfahrung mit AWS in meiner aktuellen Position bei Firma XYZ...'",
            "en": "e.g., '5 years experience with AWS in my current position at Company XYZ...'",
            "es": "ej., '5 años de experiencia con AWS en mi puesto actual en la Empresa XYZ...'"
        },

        # CV Regeneration Section
        "cv_regenerate_title": {
            "de": "Neuen Lebenslauf generieren",
            "en": "Generate New Resume",
            "es": "Generar Nuevo Currículum"
        },
        "cv_regenerate_description": {
            "de": "Basierend auf Ihren Angaben erstellen wir einen aktualisierten Lebenslauf, der Ihre zusätzlichen Qualifikationen hervorhebt.",
            "en": "Based on your input, we will create an updated resume highlighting your additional qualifications.",
            "es": "Basándonos en su información, crearemos un currículum actualizado que destaque sus calificaciones adicionales."
        },
        "cv_regenerate_button": {
            "de": "Aktualisierten Lebenslauf generieren",
            "en": "Generate Updated Resume",
            "es": "Generar Currículum Actualizado"
        },
        "cv_regenerate_generating": {
            "de": "Generiere...",
            "en": "Generating...",
            "es": "Generando..."
        },
        "cv_regenerate_note": {
            "de": "Der aktualisierte Lebenslauf wird als Textdatei heruntergeladen",
            "en": "The updated resume will be downloaded as a text file",
            "es": "El currículum actualizado se descargará como archivo de texto"
        },
        "cv_regenerate_success": {
            "de": "Lebenslauf erfolgreich generiert und heruntergeladen!",
            "en": "Resume successfully generated and downloaded!",
            "es": "¡Currículum generado y descargado exitosamente!"
        },
        "cv_regenerate_prompt": {
            "de": "Du bist ein professioneller CV-Schreiber. Erstelle einen aktualisierten Lebenslauf basierend auf dem Original-CV und füge die folgenden zusätzlichen Qualifikationen ein:",
            "en": "You are a professional resume writer. Create an updated resume based on the original CV and incorporate the following additional qualifications:",
            "es": "Eres un escritor profesional de currículums. Crea un currículum actualizado basado en el CV original e incorpora las siguientes calificaciones adicionales:"
        },
        "cv_regenerate_instructions": {
            "de": "Integriere diese Qualifikationen nahtlos in den Lebenslauf. Behalte das Format und den Stil bei. Gib den vollständigen, aktualisierten Lebenslauf zurück.",
            "en": "Seamlessly integrate these qualifications into the resume. Maintain the format and style. Return the complete, updated resume.",
            "es": "Integra estas calificaciones sin problemas en el currículum. Mantén el formato y el estilo. Devuelve el currículum completo y actualizado."
        },

        # Existing error messages continue...
        "error_pdf_failed_old": {
            "de": "PDF-Download fehlgeschlagen: {error}",
            "en": "PDF download failed: {error}",
            "es": "Error al descargar PDF: {error}"
        },
        "error_chat_failed": {
            "de": "Fehler: {error}",
            "en": "Error: {error}",
            "es": "Error: {error}"
        }
    }

    # LLM Prompt Templates
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
        }
    }

    def translate(self, key: str, language: Language = "de", **kwargs) -> str:
        """
        Get translation for a key in specified language.

        Args:
            key: Translation key (e.g., "app_title")
            language: Language code (de/en/es)
            **kwargs: Variables for string formatting (e.g., {count}, {error})

        Returns:
            Translated string with variables replaced

        Example:
            >>> service.translate("pdf_with_chat", "en", count=5)
            "with 5 chat messages"
        """
        # Try to get translation
        translation = self.UI_TRANSLATIONS.get(key, {}).get(language)

        # Fallback to English
        if not translation:
            translation = self.UI_TRANSLATIONS.get(key, {}).get("en")

        # Fallback to key itself if not found
        if not translation:
            translation = key

        # Replace variables
        try:
            return translation.format(**kwargs)
        except KeyError:
            return translation

    def get_llm_prompt(self, prompt_key: str, language: Language = "de", **kwargs) -> str:
        """
        Get LLM prompt template in specified language.

        Args:
            prompt_key: Prompt template key (e.g., "match_analysis")
            language: Language code (de/en/es)
            **kwargs: Variables for prompt (e.g., cv_text, job_description)

        Returns:
            Formatted LLM prompt in specified language
        """
        template = self.LLM_PROMPTS.get(prompt_key, {}).get(language)

        # Fallback to English
        if not template:
            template = self.LLM_PROMPTS.get(prompt_key, {}).get("en")

        if not template:
            raise ValueError(f"Prompt template '{prompt_key}' not found")

        return template.format(**kwargs)

    def get_all_translations(self, language: Language = "de") -> Dict[str, str]:
        """
        Get all UI translations for a language.

        Args:
            language: Language code (de/en/es)

        Returns:
            Dictionary with all translations for the language
        """
        return {
            key: self.translate(key, language)
            for key in self.UI_TRANSLATIONS.keys()
        }


# Singleton instance
translation_service = TranslationService()

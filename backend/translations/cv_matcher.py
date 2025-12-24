"""
CV Matcher Translations
Multi-language support for CV Matcher application
"""
from typing import Dict, Literal

Language = Literal["de", "en", "es"]

CV_MATCHER_TRANSLATIONS: Dict[str, Dict[Language, str]] = {
        # Header
        "cv_matcher_app_title": {
            "de": "CV Matcher",
            "en": "CV Matcher",
            "es": "CV Matcher"
        },
        "cv_matcher_llm_toggle_local": {
            "de": "🏠 Lokal (DSGVO)",
            "en": "🏠 Local (GDPR)",
            "es": "🏠 Local (RGPD)"
        },
        "cv_matcher_llm_toggle_grok": {
            "de": "⚡ GROK (nicht DSGVO)",
            "en": "⚡ GROK (non-GDPR)",
            "es": "⚡ GROK (no RGPD)"
        },

        # Document Section
        "cv_matcher_employer_section_title": {
            "de": "Arbeitgeber Dokumente",
            "en": "Employer Documents",
            "es": "Documentos del Empleador"
        },
        "cv_matcher_applicant_section_title": {
            "de": "Bewerber Dokumente",
            "en": "Applicant Documents",
            "es": "Documentos del Candidato"
        },
        "cv_matcher_upload_button": {
            "de": "Dokument hochladen",
            "en": "Upload Document",
            "es": "Subir Documento"
        },
        "cv_matcher_drag_drop_text": {
            "de": "Datei hierher ziehen oder klicken",
            "en": "Drag file here or click",
            "es": "Arrastra el archivo aquí o haz clic"
        },
        "cv_matcher_delete_button": {
            "de": "Löschen",
            "en": "Delete",
            "es": "Eliminar"
        },

        # Document Section - Tabs
        "cv_matcher_doc_tab_upload": {
            "de": "Hochladen",
            "en": "Upload",
            "es": "Subir"
        },
        "cv_matcher_doc_tab_url": {
            "de": "URL",
            "en": "URL",
            "es": "URL"
        },
        "cv_matcher_doc_tab_text": {
            "de": "Text",
            "en": "Text",
            "es": "Texto"
        },

        # Document Section - Upload
        "cv_matcher_doc_drop_file": {
            "de": "Datei hier ablegen oder",
            "en": "Drop file here or",
            "es": "Arrastra el archivo aquí o"
        },
        "cv_matcher_doc_select_file": {
            "de": "Datei auswählen",
            "en": "Select File",
            "es": "Seleccionar Archivo"
        },
        "cv_matcher_doc_loading": {
            "de": "Lädt...",
            "en": "Loading...",
            "es": "Cargando..."
        },

        # Document Section - URL
        "cv_matcher_doc_url_placeholder": {
            "de": "https://example.com/stellenanzeige",
            "en": "https://example.com/job-posting",
            "es": "https://example.com/oferta-empleo"
        },
        "cv_matcher_doc_add_url": {
            "de": "URL hinzufügen",
            "en": "Add URL",
            "es": "Agregar URL"
        },

        # Document Section - Text
        "cv_matcher_doc_text_placeholder": {
            "de": "Text hier eingeben...",
            "en": "Enter text here...",
            "es": "Ingresa texto aquí..."
        },
        "cv_matcher_doc_add_text": {
            "de": "Text hinzufügen",
            "en": "Add Text",
            "es": "Agregar Texto"
        },

        # Document Section - List
        "cv_matcher_doc_no_documents": {
            "de": "Keine Dokumente hinzugefügt",
            "en": "No documents added",
            "es": "No se agregaron documentos"
        },
        "cv_matcher_doc_preview": {
            "de": "Vorschau",
            "en": "Preview",
            "es": "Vista previa"
        },
        "cv_matcher_doc_delete": {
            "de": "Löschen",
            "en": "Delete",
            "es": "Eliminar"
        },

        # Document Section - Preview Modal
        "cv_matcher_doc_type_file": {
            "de": "Datei",
            "en": "File",
            "es": "Archivo"
        },
        "cv_matcher_doc_type_url": {
            "de": "URL",
            "en": "URL",
            "es": "URL"
        },
        "cv_matcher_doc_type_text": {
            "de": "Text",
            "en": "Text",
            "es": "Texto"
        },
        "cv_matcher_doc_content_length": {
            "de": "Inhaltslänge",
            "en": "Content length",
            "es": "Longitud del contenido"
        },
        "cv_matcher_doc_characters": {
            "de": "Zeichen",
            "en": "characters",
            "es": "caracteres"
        },
        "cv_matcher_doc_close": {
            "de": "Schließen",
            "en": "Close",
            "es": "Cerrar"
        },
        "cv_matcher_doc_summary_button": {
            "de": "📊 Zusammenfassung",
            "en": "📊 Summary",
            "es": "📊 Resumen"
        },
        "cv_matcher_doc_summary_title": {
            "de": "Zusammenfassung",
            "en": "Summary",
            "es": "Resumen"
        },
        "cv_matcher_doc_summary_loading": {
            "de": "Generiere Zusammenfassung...",
            "en": "Generating summary...",
            "es": "Generando resumen..."
        },
        "cv_matcher_doc_summary_total_docs": {
            "de": "Dokumente gesamt",
            "en": "Total documents",
            "es": "Documentos totales"
        },
        "cv_matcher_doc_summary_total_content": {
            "de": "Gesamtinhalt",
            "en": "Total content",
            "es": "Contenido total"
        },
        "cv_matcher_doc_summary_words": {
            "de": "Wörter",
            "en": "words",
            "es": "palabras"
        },
        "cv_matcher_doc_summary_details": {
            "de": "Dokumente Details",
            "en": "Document Details",
            "es": "Detalles de Documentos"
        },

        # Job Description Input
        "cv_matcher_job_desc_title": {
            "de": "Stellenbeschreibung eingeben",
            "en": "Enter Job Description",
            "es": "Ingresar Descripción del Puesto"
        },
        "cv_matcher_job_desc_subtitle": {
            "de": "Fügen Sie die Stellenbeschreibung ein, um sie mit dem Lebenslauf zu vergleichen",
            "en": "Paste the job description to compare it with the resume",
            "es": "Pegue la descripción del puesto para compararla con el currículum"
        },
        "cv_matcher_job_title_label": {
            "de": "Stellentitel (optional)",
            "en": "Job Title (optional)",
            "es": "Título del Puesto (opcional)"
        },
        "cv_matcher_job_title_placeholder": {
            "de": "z.B. Senior Software Engineer",
            "en": "e.g. Senior Software Engineer",
            "es": "ej. Ingeniero de Software Senior"
        },
        "cv_matcher_company_name_label": {
            "de": "Unternehmen (optional)",
            "en": "Company (optional)",
            "es": "Empresa (opcional)"
        },
        "cv_matcher_company_name_placeholder": {
            "de": "z.B. Tech Company GmbH",
            "en": "e.g. Tech Company Inc.",
            "es": "ej. Tech Company SA"
        },
        "cv_matcher_job_description_label": {
            "de": "Stellenbeschreibung *",
            "en": "Job Description *",
            "es": "Descripción del Puesto *"
        },
        "cv_matcher_characters": {
            "de": "Zeichen",
            "en": "characters",
            "es": "caracteres"
        },
        "cv_matcher_job_description_placeholder": {
            "de": "Fügen Sie hier die vollständige Stellenbeschreibung ein...\n\nBeispiel:\nWir suchen einen erfahrenen Software Engineer für unser Team...\n\nAnforderungen:\n- 5+ Jahre Erfahrung in der Softwareentwicklung\n- Kenntnisse in React, TypeScript, Node.js\n- Erfahrung mit Cloud-Technologien (AWS, Azure)\n...",
            "en": "Paste the complete job description here...\n\nExample:\nWe are looking for an experienced Software Engineer for our team...\n\nRequirements:\n- 5+ years of software development experience\n- Knowledge of React, TypeScript, Node.js\n- Experience with cloud technologies (AWS, Azure)\n...",
            "es": "Pegue la descripción completa del puesto aquí...\n\nEjemplo:\nBuscamos un Ingeniero de Software experimentado para nuestro equipo...\n\nRequisitos:\n- 5+ años de experiencia en desarrollo de software\n- Conocimiento de React, TypeScript, Node.js\n- Experiencia con tecnologías en la nube (AWS, Azure)\n..."
        },
        "cv_matcher_job_desc_min_required": {
            "de": "Mindestens {count} Zeichen erforderlich",
            "en": "At least {count} characters required",
            "es": "Al menos {count} caracteres requeridos"
        },
        "cv_matcher_job_desc_chars_remaining": {
            "de": "Noch {count} Zeichen erforderlich",
            "en": "Still {count} characters required",
            "es": "Aún se requieren {count} caracteres"
        },
        "cv_matcher_job_desc_ready": {
            "de": "Stellenbeschreibung ist bereit für die Analyse",
            "en": "Job description is ready for analysis",
            "es": "La descripción del puesto está lista para el análisis"
        },
        "cv_matcher_analyze_match": {
            "de": "Match analysieren",
            "en": "Analyze Match",
            "es": "Analizar Coincidencia"
        },
        "cv_matcher_reset": {
            "de": "Zurücksetzen",
            "en": "Reset",
            "es": "Restablecer"
        },
        "cv_matcher_job_desc_error_empty": {
            "de": "Bitte geben Sie eine Stellenbeschreibung ein",
            "en": "Please enter a job description",
            "es": "Por favor ingrese una descripción del puesto"
        },
        "cv_matcher_job_desc_error_min_chars": {
            "de": "Die Stellenbeschreibung muss mindestens {count} Zeichen enthalten",
            "en": "The job description must contain at least {count} characters",
            "es": "La descripción del puesto debe contener al menos {count} caracteres"
        },

        # Matching View
        "cv_matcher_match_button": {
            "de": "Match Starten",
            "en": "Start Match",
            "es": "Iniciar Match"
        },
        "cv_matcher_analyzing": {
            "de": "Analysiere...",
            "en": "Analyzing...",
            "es": "Analizando..."
        },
        "cv_matcher_progress_loading_docs": {
            "de": "Dokumente werden geladen...",
            "en": "Loading documents...",
            "es": "Cargando documentos..."
        },
        "cv_matcher_progress_analyzing_employer": {
            "de": "Arbeitgeber-Anforderungen werden analysiert...",
            "en": "Analyzing employer requirements...",
            "es": "Analizando requisitos del empleador..."
        },
        "cv_matcher_progress_analyzing_applicant": {
            "de": "Bewerber-Profil wird analysiert...",
            "en": "Analyzing applicant profile...",
            "es": "Analizando perfil del candidato..."
        },
        "cv_matcher_progress_llm_running": {
            "de": "LLM-Analyse läuft...",
            "en": "LLM analysis running...",
            "es": "Análisis LLM en progreso..."
        },
        "cv_matcher_progress_generating_results": {
            "de": "Ergebnisse werden generiert...",
            "en": "Generating results...",
            "es": "Generando resultados..."
        },
        "cv_matcher_progress_finalizing": {
            "de": "Finalisierung...",
            "en": "Finalizing...",
            "es": "Finalizando..."
        },
        "cv_matcher_progress_completed": {
            "de": "Abgeschlossen!",
            "en": "Completed!",
            "es": "¡Completado!"
        },

        # Results
        "cv_matcher_match_high": {
            "de": "Sehr gute Übereinstimmung",
            "en": "Excellent Match",
            "es": "Excelente Coincidencia"
        },
        "cv_matcher_match_medium": {
            "de": "Mittlere Übereinstimmung",
            "en": "Moderate Match",
            "es": "Coincidencia Moderada"
        },
        "cv_matcher_match_low": {
            "de": "Geringe Übereinstimmung",
            "en": "Low Match",
            "es": "Baja Coincidencia"
        },
        "cv_matcher_strengths_title": {
            "de": "Stärken",
            "en": "Strengths",
            "es": "Fortalezas"
        },
        "cv_matcher_gaps_title": {
            "de": "Lücken",
            "en": "Gaps",
            "es": "Brechas"
        },
        "cv_matcher_recommendations_title": {
            "de": "Empfehlungen",
            "en": "Recommendations",
            "es": "Recomendaciones"
        },
        "cv_matcher_detailed_analysis_title": {
            "de": "Detaillierte Analyse",
            "en": "Detailed Analysis",
            "es": "Análisis Detallado"
        },
        "cv_matcher_comparison_title": {
            "de": "Detaillierter Vergleich",
            "en": "Detailed Comparison",
            "es": "Comparación Detallada"
        },
        "cv_matcher_comparison_requirement": {
            "de": "Anforderung",
            "en": "Requirement",
            "es": "Requisito"
        },
        "cv_matcher_comparison_applicant_match": {
            "de": "Bewerber Match",
            "en": "Applicant Match",
            "es": "Coincidencia del Candidato"
        },
        "cv_matcher_comparison_details": {
            "de": "Einzelheiten",
            "en": "Details",
            "es": "Detalles"
        },
        "cv_matcher_comparison_level": {
            "de": "Stufe",
            "en": "Level",
            "es": "Nivel"
        },
        "cv_matcher_comparison_confidence": {
            "de": "Sicherheit",
            "en": "Confidence",
            "es": "Confianza"
        },
        "cv_matcher_match_level_full": {
            "de": "Vollständig",
            "en": "Full",
            "es": "Completo"
        },
        "cv_matcher_match_level_partial": {
            "de": "Teilweise",
            "en": "Partial",
            "es": "Parcial"
        },
        "cv_matcher_match_level_missing": {
            "de": "Fehlend",
            "en": "Missing",
            "es": "Ausente"
        },

        # PDF Download
        "cv_matcher_pdf_download_button": {
            "de": "PDF-Report herunterladen",
            "en": "Download PDF Report",
            "es": "Descargar Informe PDF"
        },
        "cv_matcher_pdf_generating": {
            "de": "PDF wird generiert...",
            "en": "Generating PDF...",
            "es": "Generando PDF..."
        },
        "cv_matcher_pdf_with_chat": {
            "de": "mit {count} Chat-Nachrichten",
            "en": "with {count} chat messages",
            "es": "con {count} mensajes de chat"
        },

        # Chat
        "cv_matcher_chat_title": {
            "de": "💬 Interaktiver Chat",
            "en": "💬 Interactive Chat",
            "es": "💬 Chat Interactivo"
        },
        "cv_matcher_chat_clear_button": {
            "de": "Verlauf löschen",
            "en": "Clear History",
            "es": "Borrar Historial"
        },
        "cv_matcher_chat_empty_message": {
            "de": "Stellen Sie Fragen zur Analyse oder zu den hochgeladenen Dokumenten.",
            "en": "Ask questions about the analysis or uploaded documents.",
            "es": "Haga preguntas sobre el análisis o los documentos subidos."
        },
        "cv_matcher_chat_examples": {
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
        "cv_matcher_chat_input_placeholder": {
            "de": "Frage eingeben...",
            "en": "Enter question...",
            "es": "Ingrese pregunta..."
        },
        "cv_matcher_chat_send_button": {
            "de": "Senden",
            "en": "Send",
            "es": "Enviar"
        },
        "cv_matcher_chat_user_label": {
            "de": "Sie",
            "en": "You",
            "es": "Usted"
        },
        "cv_matcher_chat_assistant_label": {
            "de": "Assistent",
            "en": "Assistant",
            "es": "Asistente"
        },
        "cv_matcher_chat_sources_label": {
            "de": "Quellen:",
            "en": "Sources:",
            "es": "Fuentes:"
        },

        # Error Messages
        "cv_matcher_error_upload_failed": {
            "de": "Upload fehlgeschlagen: {error}",
            "en": "Upload failed: {error}",
            "es": "Error al subir: {error}"
        },
        "cv_matcher_error_analysis_failed": {
            "de": "Fehler bei der Analyse. Bitte versuchen Sie es erneut.",
            "en": "Analysis error. Please try again.",
            "es": "Error en el análisis. Por favor, inténtelo de nuevo."
        },
        "cv_matcher_error_need_documents": {
            "de": "Bitte fügen Sie Dokumente für beide Seiten hinzu",
            "en": "Please add documents for both sides",
            "es": "Por favor agregue documentos para ambos lados"
        },
        "cv_matcher_error_pdf_failed": {
            "de": "PDF-Generierung fehlgeschlagen: {error}",
            "en": "PDF generation failed: {error}",
            "es": "Error al generar PDF: {error}"
        },
        "cv_matcher_error_no_claims": {
            "de": "Bitte wählen Sie mindestens eine Qualifikation aus und geben Sie eine Begründung ein",
            "en": "Please select at least one qualification and provide a justification",
            "es": "Por favor seleccione al menos una calificación y proporcione una justificación"
        },
        "cv_matcher_error_cv_regenerate_failed": {
            "de": "CV-Generierung fehlgeschlagen",
            "en": "CV generation failed",
            "es": "Error al generar CV"
        },

        # Gap Claims Section
        "cv_matcher_gap_claims_title": {
            "de": "Qualifikationen nachtragen",
            "en": "Add Missing Qualifications",
            "es": "Agregar Calificaciones Faltantes"
        },
        "cv_matcher_gap_claims_description": {
            "de": "Die Analyse hat einige Qualifikationen als fehlend markiert. Falls Sie diese Fähigkeiten tatsächlich besitzen, können Sie sie hier nachweisen. Wir erstellen dann einen aktualisierten Lebenslauf, der diese Kompetenzen hervorhebt.",
            "en": "The analysis marked some qualifications as missing. If you actually possess these skills, you can document them here. We will then create an updated resume highlighting these competencies.",
            "es": "El análisis marcó algunas calificaciones como faltantes. Si realmente posee estas habilidades, puede documentarlas aquí. Luego crearemos un currículum actualizado que destaque estas competencias."
        },
        "cv_matcher_gap_claims_i_have_this": {
            "de": "Diese Qualifikation besitze ich",
            "en": "I have this qualification",
            "es": "Tengo esta calificación"
        },
        "cv_matcher_gap_claims_justification": {
            "de": "Begründung / Nachweis",
            "en": "Justification / Evidence",
            "es": "Justificación / Evidencia"
        },
        "cv_matcher_gap_claims_justification_placeholder": {
            "de": "z.B. '5 Jahre Erfahrung mit AWS in meiner aktuellen Position bei Firma XYZ...'",
            "en": "e.g., '5 years experience with AWS in my current position at Company XYZ...'",
            "es": "ej., '5 años de experiencia con AWS en mi puesto actual en la Empresa XYZ...'"
        },

        # CV Regeneration Section
        "cv_matcher_cv_regenerate_title": {
            "de": "Neuen Lebenslauf generieren",
            "en": "Generate New Resume",
            "es": "Generar Nuevo Currículum"
        },
        "cv_matcher_cv_regenerate_description": {
            "de": "Basierend auf Ihren Angaben erstellen wir einen aktualisierten Lebenslauf, der Ihre zusätzlichen Qualifikationen hervorhebt.",
            "en": "Based on your input, we will create an updated resume highlighting your additional qualifications.",
            "es": "Basándonos en su información, crearemos un currículum actualizado que destaque sus calificaciones adicionales."
        },
        "cv_matcher_cv_regenerate_button": {
            "de": "Aktualisierten Lebenslauf generieren",
            "en": "Generate Updated Resume",
            "es": "Generar Currículum Actualizado"
        },
        "cv_matcher_cv_regenerate_generating": {
            "de": "Generiere...",
            "en": "Generating...",
            "es": "Generando..."
        },
        "cv_matcher_cv_regenerate_note": {
            "de": "Der aktualisierte Lebenslauf wird als Textdatei heruntergeladen",
            "en": "The updated resume will be downloaded as a text file",
            "es": "El currículum actualizado se descargará como archivo de texto"
        },
        "cv_matcher_cv_regenerate_success": {
            "de": "Lebenslauf erfolgreich generiert und heruntergeladen!",
            "en": "Resume successfully generated and downloaded!",
            "es": "¡Currículum generado y descargado exitosamente!"
        },
        "cv_matcher_cv_regenerate_prompt": {
            "de": "Du bist ein professioneller CV-Schreiber. Erstelle einen aktualisierten Lebenslauf basierend auf dem Original-CV und füge die folgenden zusätzlichen Qualifikationen ein:",
            "en": "You are a professional resume writer. Create an updated resume based on the original CV and incorporate the following additional qualifications:",
            "es": "Eres un escritor profesional de currículums. Crea un currículum actualizado basado en el CV original e incorpora las siguientes calificaciones adicionales:"
        },
        "cv_matcher_cv_regenerate_instructions": {
            "de": "Integriere diese Qualifikationen nahtlos in den Lebenslauf. Behalte das Format und den Stil bei. Gib den vollständigen, aktualisierten Lebenslauf zurück.",
            "en": "Seamlessly integrate these qualifications into the resume. Maintain the format and style. Return the complete, updated resume.",
            "es": "Integra estas calificaciones sin problemas en el currículum. Mantén el formato y el estilo. Devuelve el currículum completo y actualizado."
        },

        # Existing error messages continue...
        "cv_matcher_error_pdf_failed_old": {
            "de": "PDF-Download fehlgeschlagen: {error}",
            "en": "PDF download failed: {error}",
            "es": "Error al descargar PDF: {error}"
        },
        "cv_matcher_error_chat_failed": {
            "de": "Fehler: {error}",
            "en": "Error: {error}",
            "es": "Error: {error}"
        },

}

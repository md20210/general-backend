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
    "cv_matcher_job_description_label": {
        "de": "Stellenbeschreibung",
        "en": "Job Description",
        "es": "Descripción del Puesto"
    },
    "cv_matcher_cv_label": {
        "de": "Lebenslauf",
        "en": "CV / Resume",
        "es": "Currículum Vitae"
    },
    "cv_matcher_cover_letter_label": {
        "de": "Anschreiben (optional)",
        "en": "Cover Letter (optional)",
        "es": "Carta de Presentación (opcional)"
    },

    # Document Section - Tabs
    "cv_matcher_tab_upload": {
        "de": "📎 Hochladen",
        "en": "📎 Upload",
        "es": "📎 Subir"
    },
    "cv_matcher_tab_url": {
        "de": "🔗 URL",
        "en": "🔗 URL",
        "es": "🔗 URL"
    },
    "cv_matcher_tab_text": {
        "de": "✍️ Text",
        "en": "✍️ Text",
        "es": "✍️ Texto"
    },

    # Document Section - Upload
    "cv_matcher_upload_button": {
        "de": "Datei wählen",
        "en": "Choose File",
        "es": "Elegir Archivo"
    },
    "cv_matcher_no_file_selected": {
        "de": "Keine Datei ausgewählt",
        "en": "No file selected",
        "es": "Ningún archivo seleccionado"
    },

    # Document Section - URL
    "cv_matcher_url_placeholder": {
        "de": "https://example.com/job-posting",
        "en": "https://example.com/job-posting",
        "es": "https://example.com/job-posting"
    },
    "cv_matcher_url_fetch_button": {
        "de": "URL abrufen",
        "en": "Fetch URL",
        "es": "Obtener URL"
    },

    # Document Section - Text
    "cv_matcher_text_placeholder": {
        "de": "Text hier einfügen...",
        "en": "Paste text here...",
        "es": "Pegar texto aquí..."
    },

    # Document Section - List
    "cv_matcher_document_count": {
        "de": "{count} Dokument(e)",
        "en": "{count} document(s)",
        "es": "{count} documento(s)"
    },
    "cv_matcher_uploaded_documents": {
        "de": "Hochgeladene Dokumente",
        "en": "Uploaded Documents",
        "es": "Documentos Subidos"
    },
    "cv_matcher_no_documents": {
        "de": "Noch keine Dokumente",
        "en": "No documents yet",
        "es": "Aún no hay documentos"
    },

    # Document Section - Preview Modal
    "cv_matcher_preview_title": {
        "de": "Dokument Vorschau",
        "en": "Document Preview",
        "es": "Vista Previa del Documento"
    },
    "cv_matcher_close_button": {
        "de": "Schließen",
        "en": "Close",
        "es": "Cerrar"
    },

    # Analysis Section
    "cv_matcher_analysis_title": {
        "de": "📊 Matching-Analyse",
        "en": "📊 Match Analysis",
        "es": "📊 Análisis de Coincidencia"
    },
    "cv_matcher_start_analysis_button": {
        "de": "🚀 Analyse starten",
        "en": "🚀 Start Analysis",
        "es": "🚀 Iniciar Análisis"
    },
    "cv_matcher_analyzing_status": {
        "de": "⏳ Analysiere...",
        "en": "⏳ Analyzing...",
        "es": "⏳ Analizando..."
    },
    "cv_matcher_upload_documents_first": {
        "de": "Bitte laden Sie zuerst eine Stellenbeschreibung und einen Lebenslauf hoch.",
        "en": "Please upload a job description and CV first.",
        "es": "Por favor, sube primero una descripción del puesto y un currículum."
    },
    "cv_matcher_overall_match": {
        "de": "Gesamtübereinstimmung",
        "en": "Overall Match",
        "es": "Coincidencia General"
    },
    "cv_matcher_strengths": {
        "de": "Stärken",
        "en": "Strengths",
        "es": "Fortalezas"
    },
    "cv_matcher_weaknesses": {
        "de": "Schwächen",
        "en": "Weaknesses",
        "es": "Debilidades"
    },
    "cv_matcher_missing_qualifications": {
        "de": "Fehlende Qualifikationen",
        "en": "Missing Qualifications",
        "es": "Calificaciones Faltantes"
    },
    "cv_matcher_recommendations": {
        "de": "Empfehlungen",
        "en": "Recommendations",
        "es": "Recomendaciones"
    },
    "cv_matcher_pdf_export_button": {
        "de": "📄 Als PDF exportieren",
        "en": "📄 Export as PDF",
        "es": "📄 Exportar como PDF"
    },
    "cv_matcher_generating_pdf": {
        "de": "PDF wird erstellt...",
        "en": "Generating PDF...",
        "es": "Generando PDF..."
    },

    # Chat Section
    "cv_matcher_chat_title": {
        "de": "💬 Interaktiver Chat",
        "en": "💬 Interactive Chat",
        "es": "💬 Chat Interactivo"
    },
    "cv_matcher_chat_placeholder": {
        "de": "Frage eingeben...",
        "en": "Enter question...",
        "es": "Introduce pregunta..."
    },
    "cv_matcher_chat_send_button": {
        "de": "Senden",
        "en": "Send",
        "es": "Enviar"
    },
    "cv_matcher_chat_empty_state": {
        "de": "Stellen Sie eine Frage zur Stellenbeschreibung oder zum Lebenslauf",
        "en": "Ask a question about the job description or CV",
        "es": "Haz una pregunta sobre la descripción del puesto o el currículum"
    },
    "cv_matcher_chat_upload_first": {
        "de": "Bitte laden Sie zuerst Dokumente hoch, um den Chat zu verwenden.",
        "en": "Please upload documents first to use the chat.",
        "es": "Por favor, sube documentos primero para usar el chat."
    },

    # Error Messages
    "cv_matcher_error_upload_failed": {
        "de": "Fehler beim Hochladen: {error}",
        "en": "Upload failed: {error}",
        "es": "Error al subir: {error}"
    },
    "cv_matcher_error_url_fetch_failed": {
        "de": "Fehler beim Abrufen der URL: {error}",
        "en": "Failed to fetch URL: {error}",
        "es": "Error al obtener URL: {error}"
    },
    "cv_matcher_error_analysis_failed": {
        "de": "Analyse fehlgeschlagen: {error}",
        "en": "Analysis failed: {error}",
        "es": "Análisis falló: {error}"
    },
    "cv_matcher_error_chat_failed": {
        "de": "Chat-Anfrage fehlgeschlagen: {error}",
        "en": "Chat request failed: {error}",
        "es": "Solicitud de chat falló: {error}"
    },
    "cv_matcher_error_pdf_generation_failed": {
        "de": "PDF-Erstellung fehlgeschlagen: {error}",
        "en": "PDF generation failed: {error}",
        "es": "Generación de PDF falló: {error}"
    },

    # Success Messages
    "cv_matcher_success_upload": {
        "de": "Datei erfolgreich hochgeladen",
        "en": "File uploaded successfully",
        "es": "Archivo subido exitosamente"
    },
    "cv_matcher_success_url_fetched": {
        "de": "URL erfolgreich abgerufen",
        "en": "URL fetched successfully",
        "es": "URL obtenida exitosamente"
    },
    "cv_matcher_success_analysis_complete": {
        "de": "Analyse abgeschlossen",
        "en": "Analysis complete",
        "es": "Análisis completado"
    },
    "cv_matcher_success_pdf_generated": {
        "de": "PDF erfolgreich erstellt",
        "en": "PDF generated successfully",
        "es": "PDF generado exitosamente"
    },

    # Document Types
    "cv_matcher_doc_type_pdf": {
        "de": "PDF",
        "en": "PDF",
        "es": "PDF"
    },
    "cv_matcher_doc_type_docx": {
        "de": "Word",
        "en": "Word",
        "es": "Word"
    },
    "cv_matcher_doc_type_txt": {
        "de": "Text",
        "en": "Text",
        "es": "Texto"
    },
    "cv_matcher_doc_type_url": {
        "de": "URL",
        "en": "URL",
        "es": "URL"
    },

    # Document Status
    "cv_matcher_status_processing": {
        "de": "Verarbeitung...",
        "en": "Processing...",
        "es": "Procesando..."
    },
    "cv_matcher_status_ready": {
        "de": "Bereit",
        "en": "Ready",
        "es": "Listo"
    },
    "cv_matcher_status_error": {
        "de": "Fehler",
        "en": "Error",
        "es": "Error"
    },

    # File Size
    "cv_matcher_file_size_kb": {
        "de": "{size} KB",
        "en": "{size} KB",
        "es": "{size} KB"
    },
    "cv_matcher_file_size_mb": {
        "de": "{size} MB",
        "en": "{size} MB",
        "es": "{size} MB"
    },

    # Actions
    "cv_matcher_action_view": {
        "de": "Ansehen",
        "en": "View",
        "es": "Ver"
    },
    "cv_matcher_action_delete": {
        "de": "Löschen",
        "en": "Delete",
        "es": "Eliminar"
    },
    "cv_matcher_action_download": {
        "de": "Herunterladen",
        "en": "Download",
        "es": "Descargar"
    },

    # Confirmation
    "cv_matcher_confirm_delete": {
        "de": "Möchten Sie dieses Dokument wirklich löschen?",
        "en": "Are you sure you want to delete this document?",
        "es": "¿Estás seguro de que quieres eliminar este documento?"
    },

    # Loading
    "cv_matcher_loading": {
        "de": "Lädt...",
        "en": "Loading...",
        "es": "Cargando..."
    },

    # Language Toggle
    "cv_matcher_language_de": {
        "de": "🇩🇪 Deutsch",
        "en": "🇩🇪 German",
        "es": "🇩🇪 Alemán"
    },
    "cv_matcher_language_en": {
        "de": "🇬🇧 Englisch",
        "en": "🇬🇧 English",
        "es": "🇬🇧 Inglés"
    },
    "cv_matcher_language_es": {
        "de": "🇪🇸 Spanisch",
        "en": "🇪🇸 Spanish",
        "es": "🇪🇸 Español"
    },

    # Footer
    "cv_matcher_footer_text": {
        "de": "Powered by General Backend • RAG mit pgvector • Multi-LLM Gateway",
        "en": "Powered by General Backend • RAG with pgvector • Multi-LLM Gateway",
        "es": "Desarrollado con General Backend • RAG con pgvector • Gateway Multi-LLM"
    },

    # PDF Export - Additional fields
    "cv_matcher_pdf_title": {
        "de": "CV Matching-Analyse",
        "en": "CV Match Analysis",
        "es": "Análisis de Coincidencia de CV"
    },
    "cv_matcher_pdf_generated_on": {
        "de": "Erstellt am",
        "en": "Generated on",
        "es": "Generado el"
    },
    "cv_matcher_pdf_job_description": {
        "de": "Stellenbeschreibung",
        "en": "Job Description",
        "es": "Descripción del Puesto"
    },
    "cv_matcher_pdf_candidate_cv": {
        "de": "Bewerber-CV",
        "en": "Candidate CV",
        "es": "CV del Candidato"
    },
    "cv_matcher_pdf_cover_letter": {
        "de": "Anschreiben",
        "en": "Cover Letter",
        "es": "Carta de Presentación"
    },
    "cv_matcher_pdf_match_score": {
        "de": "Match-Score",
        "en": "Match Score",
        "es": "Puntuación de Coincidencia"
    },
    "cv_matcher_pdf_with_cover_letter": {
        "de": "(mit Anschreiben)",
        "en": "(with cover letter)",
        "es": "(con carta de presentación)"
    },
    "cv_matcher_pdf_without_cover_letter": {
        "de": "(ohne Anschreiben)",
        "en": "(without cover letter)",
        "es": "(sin carta de presentación)"
    },

    # Chat context
    "cv_matcher_pdf_with_chat": {
        "de": "mit {count} Chat-Nachrichten",
        "en": "with {count} chat messages",
        "es": "con {count} mensajes de chat"
    },
    "cv_matcher_pdf_no_chat": {
        "de": "keine Chat-Nachrichten",
        "en": "no chat messages",
        "es": "sin mensajes de chat"
    },
}

"""
CV Matcher Translations
Multi-language support for CV Matcher application
"""
from typing import Dict, Literal

Language = Literal["de", "en", "es"]

CV_MATCHER_TRANSLATIONS: Dict[str, Dict[Language, str]] = {
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
    "job_description_label": {
        "de": "Stellenbeschreibung",
        "en": "Job Description",
        "es": "Descripción del Puesto"
    },
    "cv_label": {
        "de": "Lebenslauf",
        "en": "CV / Resume",
        "es": "Currículum Vitae"
    },
    "cover_letter_label": {
        "de": "Anschreiben (optional)",
        "en": "Cover Letter (optional)",
        "es": "Carta de Presentación (opcional)"
    },

    # Document Section - Tabs
    "tab_upload": {
        "de": "📎 Hochladen",
        "en": "📎 Upload",
        "es": "📎 Subir"
    },
    "tab_url": {
        "de": "🔗 URL",
        "en": "🔗 URL",
        "es": "🔗 URL"
    },
    "tab_text": {
        "de": "✍️ Text",
        "en": "✍️ Text",
        "es": "✍️ Texto"
    },

    # Document Section - Upload
    "upload_button": {
        "de": "Datei wählen",
        "en": "Choose File",
        "es": "Elegir Archivo"
    },
    "no_file_selected": {
        "de": "Keine Datei ausgewählt",
        "en": "No file selected",
        "es": "Ningún archivo seleccionado"
    },

    # Document Section - URL
    "url_placeholder": {
        "de": "https://example.com/job-posting",
        "en": "https://example.com/job-posting",
        "es": "https://example.com/job-posting"
    },
    "url_fetch_button": {
        "de": "URL abrufen",
        "en": "Fetch URL",
        "es": "Obtener URL"
    },

    # Document Section - Text
    "text_placeholder": {
        "de": "Text hier einfügen...",
        "en": "Paste text here...",
        "es": "Pegar texto aquí..."
    },

    # Document Section - List
    "document_count": {
        "de": "{count} Dokument(e)",
        "en": "{count} document(s)",
        "es": "{count} documento(s)"
    },
    "uploaded_documents": {
        "de": "Hochgeladene Dokumente",
        "en": "Uploaded Documents",
        "es": "Documentos Subidos"
    },
    "no_documents": {
        "de": "Noch keine Dokumente",
        "en": "No documents yet",
        "es": "Aún no hay documentos"
    },

    # Document Section - Preview Modal
    "preview_title": {
        "de": "Dokument Vorschau",
        "en": "Document Preview",
        "es": "Vista Previa del Documento"
    },
    "close_button": {
        "de": "Schließen",
        "en": "Close",
        "es": "Cerrar"
    },

    # Analysis Section
    "analysis_title": {
        "de": "📊 Matching-Analyse",
        "en": "📊 Match Analysis",
        "es": "📊 Análisis de Coincidencia"
    },
    "start_analysis_button": {
        "de": "🚀 Analyse starten",
        "en": "🚀 Start Analysis",
        "es": "🚀 Iniciar Análisis"
    },
    "analyzing_status": {
        "de": "⏳ Analysiere...",
        "en": "⏳ Analyzing...",
        "es": "⏳ Analizando..."
    },
    "upload_documents_first": {
        "de": "Bitte laden Sie zuerst eine Stellenbeschreibung und einen Lebenslauf hoch.",
        "en": "Please upload a job description and CV first.",
        "es": "Por favor, sube primero una descripción del puesto y un currículum."
    },
    "overall_match": {
        "de": "Gesamtübereinstimmung",
        "en": "Overall Match",
        "es": "Coincidencia General"
    },
    "strengths": {
        "de": "Stärken",
        "en": "Strengths",
        "es": "Fortalezas"
    },
    "weaknesses": {
        "de": "Schwächen",
        "en": "Weaknesses",
        "es": "Debilidades"
    },
    "missing_qualifications": {
        "de": "Fehlende Qualifikationen",
        "en": "Missing Qualifications",
        "es": "Calificaciones Faltantes"
    },
    "recommendations": {
        "de": "Empfehlungen",
        "en": "Recommendations",
        "es": "Recomendaciones"
    },
    "pdf_export_button": {
        "de": "📄 Als PDF exportieren",
        "en": "📄 Export as PDF",
        "es": "📄 Exportar como PDF"
    },
    "generating_pdf": {
        "de": "PDF wird erstellt...",
        "en": "Generating PDF...",
        "es": "Generando PDF..."
    },

    # Chat Section
    "chat_title": {
        "de": "💬 Interaktiver Chat",
        "en": "💬 Interactive Chat",
        "es": "💬 Chat Interactivo"
    },
    "chat_placeholder": {
        "de": "Frage eingeben...",
        "en": "Enter question...",
        "es": "Introduce pregunta..."
    },
    "chat_send_button": {
        "de": "Senden",
        "en": "Send",
        "es": "Enviar"
    },
    "chat_empty_state": {
        "de": "Stellen Sie eine Frage zur Stellenbeschreibung oder zum Lebenslauf",
        "en": "Ask a question about the job description or CV",
        "es": "Haz una pregunta sobre la descripción del puesto o el currículum"
    },
    "chat_upload_first": {
        "de": "Bitte laden Sie zuerst Dokumente hoch, um den Chat zu verwenden.",
        "en": "Please upload documents first to use the chat.",
        "es": "Por favor, sube documentos primero para usar el chat."
    },

    # Error Messages
    "error_upload_failed": {
        "de": "Fehler beim Hochladen: {error}",
        "en": "Upload failed: {error}",
        "es": "Error al subir: {error}"
    },
    "error_url_fetch_failed": {
        "de": "Fehler beim Abrufen der URL: {error}",
        "en": "Failed to fetch URL: {error}",
        "es": "Error al obtener URL: {error}"
    },
    "error_analysis_failed": {
        "de": "Analyse fehlgeschlagen: {error}",
        "en": "Analysis failed: {error}",
        "es": "Análisis falló: {error}"
    },
    "error_chat_failed": {
        "de": "Chat-Anfrage fehlgeschlagen: {error}",
        "en": "Chat request failed: {error}",
        "es": "Solicitud de chat falló: {error}"
    },
    "error_pdf_generation_failed": {
        "de": "PDF-Erstellung fehlgeschlagen: {error}",
        "en": "PDF generation failed: {error}",
        "es": "Generación de PDF falló: {error}"
    },

    # Success Messages
    "success_upload": {
        "de": "Datei erfolgreich hochgeladen",
        "en": "File uploaded successfully",
        "es": "Archivo subido exitosamente"
    },
    "success_url_fetched": {
        "de": "URL erfolgreich abgerufen",
        "en": "URL fetched successfully",
        "es": "URL obtenida exitosamente"
    },
    "success_analysis_complete": {
        "de": "Analyse abgeschlossen",
        "en": "Analysis complete",
        "es": "Análisis completado"
    },
    "success_pdf_generated": {
        "de": "PDF erfolgreich erstellt",
        "en": "PDF generated successfully",
        "es": "PDF generado exitosamente"
    },

    # Document Types
    "doc_type_pdf": {
        "de": "PDF",
        "en": "PDF",
        "es": "PDF"
    },
    "doc_type_docx": {
        "de": "Word",
        "en": "Word",
        "es": "Word"
    },
    "doc_type_txt": {
        "de": "Text",
        "en": "Text",
        "es": "Texto"
    },
    "doc_type_url": {
        "de": "URL",
        "en": "URL",
        "es": "URL"
    },

    # Document Status
    "status_processing": {
        "de": "Verarbeitung...",
        "en": "Processing...",
        "es": "Procesando..."
    },
    "status_ready": {
        "de": "Bereit",
        "en": "Ready",
        "es": "Listo"
    },
    "status_error": {
        "de": "Fehler",
        "en": "Error",
        "es": "Error"
    },

    # File Size
    "file_size_kb": {
        "de": "{size} KB",
        "en": "{size} KB",
        "es": "{size} KB"
    },
    "file_size_mb": {
        "de": "{size} MB",
        "en": "{size} MB",
        "es": "{size} MB"
    },

    # Actions
    "action_view": {
        "de": "Ansehen",
        "en": "View",
        "es": "Ver"
    },
    "action_delete": {
        "de": "Löschen",
        "en": "Delete",
        "es": "Eliminar"
    },
    "action_download": {
        "de": "Herunterladen",
        "en": "Download",
        "es": "Descargar"
    },

    # Confirmation
    "confirm_delete": {
        "de": "Möchten Sie dieses Dokument wirklich löschen?",
        "en": "Are you sure you want to delete this document?",
        "es": "¿Estás seguro de que quieres eliminar este documento?"
    },

    # Loading
    "loading": {
        "de": "Lädt...",
        "en": "Loading...",
        "es": "Cargando..."
    },

    # Language Toggle
    "language_de": {
        "de": "🇩🇪 Deutsch",
        "en": "🇩🇪 German",
        "es": "🇩🇪 Alemán"
    },
    "language_en": {
        "de": "🇬🇧 Englisch",
        "en": "🇬🇧 English",
        "es": "🇬🇧 Inglés"
    },
    "language_es": {
        "de": "🇪🇸 Spanisch",
        "en": "🇪🇸 Spanish",
        "es": "🇪🇸 Español"
    },

    # Footer
    "footer_text": {
        "de": "Powered by General Backend • RAG mit pgvector • Multi-LLM Gateway",
        "en": "Powered by General Backend • RAG with pgvector • Multi-LLM Gateway",
        "es": "Desarrollado con General Backend • RAG con pgvector • Gateway Multi-LLM"
    },

    # PDF Export - Additional fields
    "pdf_title": {
        "de": "CV Matching-Analyse",
        "en": "CV Match Analysis",
        "es": "Análisis de Coincidencia de CV"
    },
    "pdf_generated_on": {
        "de": "Erstellt am",
        "en": "Generated on",
        "es": "Generado el"
    },
    "pdf_job_description": {
        "de": "Stellenbeschreibung",
        "en": "Job Description",
        "es": "Descripción del Puesto"
    },
    "pdf_candidate_cv": {
        "de": "Bewerber-CV",
        "en": "Candidate CV",
        "es": "CV del Candidato"
    },
    "pdf_cover_letter": {
        "de": "Anschreiben",
        "en": "Cover Letter",
        "es": "Carta de Presentación"
    },
    "pdf_match_score": {
        "de": "Match-Score",
        "en": "Match Score",
        "es": "Puntuación de Coincidencia"
    },
    "pdf_with_cover_letter": {
        "de": "(mit Anschreiben)",
        "en": "(with cover letter)",
        "es": "(con carta de presentación)"
    },
    "pdf_without_cover_letter": {
        "de": "(ohne Anschreiben)",
        "en": "(without cover letter)",
        "es": "(sin carta de presentación)"
    },

    # Chat context
    "pdf_with_chat": {
        "de": "mit {count} Chat-Nachrichten",
        "en": "with {count} chat messages",
        "es": "con {count} mensajes de chat"
    },
    "pdf_no_chat": {
        "de": "keine Chat-Nachrichten",
        "en": "no chat messages",
        "es": "sin mensajes de chat"
    },
}

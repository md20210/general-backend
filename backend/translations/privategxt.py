"""
PrivateGxT App Translations
Multi-language support for PrivateGxT RAG application
"""
from typing import Dict, Literal

Language = Literal["de", "en", "es"]

PRIVATEGXT_TRANSLATIONS: Dict[str, Dict[Language, str]] = {
    # App Header
    "privategxt_app_title": {
        "de": "PrivateGxT",
        "en": "PrivateGxT",
        "es": "PrivateGxT"
    },
    "privategxt_app_subtitle": {
        "de": "RAG-basierte Dokumenten-Konversation",
        "en": "RAG-based Document Conversation",
        "es": "Conversación de Documentos basada en RAG"
    },

    # Stats
    "privategxt_stats_documents": {
        "de": "Dokumente",
        "en": "Documents",
        "es": "Documentos"
    },
    "privategxt_stats_chunks": {
        "de": "Text-Chunks",
        "en": "Text Chunks",
        "es": "Fragmentos de Texto"
    },
    "privategxt_stats_messages": {
        "de": "Nachrichten",
        "en": "Messages",
        "es": "Mensajes"
    },

    # Upload Section
    "privategxt_upload_title": {
        "de": "Dokument hochladen",
        "en": "Upload Document",
        "es": "Subir Documento"
    },
    "privategxt_upload_drag_drop": {
        "de": "Datei hierher ziehen oder klicken zum Auswählen",
        "en": "Drag and drop file here or click to select",
        "es": "Arrastra y suelta el archivo aquí o haz clic para seleccionar"
    },
    "privategxt_upload_supported_formats": {
        "de": "Unterstützte Formate: PDF, DOCX, TXT",
        "en": "Supported formats: PDF, DOCX, TXT",
        "es": "Formatos compatibles: PDF, DOCX, TXT"
    },
    "privategxt_uploading": {
        "de": "Wird hochgeladen...",
        "en": "Uploading...",
        "es": "Subiendo..."
    },
    "privategxt_upload_error_type": {
        "de": "Ungültiger Dateityp. Bitte nur PDF, DOCX oder TXT hochladen.",
        "en": "Invalid file type. Please upload PDF, DOCX, or TXT only.",
        "es": "Tipo de archivo no válido. Por favor sube solo PDF, DOCX o TXT."
    },
    "privategxt_upload_error_size": {
        "de": "Datei zu groß. Maximum: 10 MB",
        "en": "File too large. Maximum: 10 MB",
        "es": "Archivo demasiado grande. Máximo: 10 MB"
    },
    "privategxt_upload_error_generic": {
        "de": "Upload fehlgeschlagen. Bitte versuchen Sie es erneut.",
        "en": "Upload failed. Please try again.",
        "es": "Fallo en la subida. Por favor, inténtalo de nuevo."
    },

    # Documents Section
    "privategxt_documents_title": {
        "de": "Dokumente",
        "en": "Documents",
        "es": "Documentos"
    },
    "privategxt_no_documents": {
        "de": "Noch keine Dokumente",
        "en": "No documents yet",
        "es": "Aún no hay documentos"
    },
    "privategxt_chunk": {
        "de": "Chunk",
        "en": "Chunk",
        "es": "Fragmento"
    },
    "privategxt_chunks": {
        "de": "Chunks",
        "en": "Chunks",
        "es": "Fragmentos"
    },
    "privategxt_delete_document": {
        "de": "Dokument löschen",
        "en": "Delete document",
        "es": "Eliminar documento"
    },
    "privategxt_clear_all": {
        "de": "Alle löschen",
        "en": "Clear all",
        "es": "Borrar todo"
    },
    "privategxt_confirm_delete": {
        "de": "Möchten Sie dieses Dokument wirklich löschen?",
        "en": "Are you sure you want to delete this document?",
        "es": "¿Estás seguro de que quieres eliminar este documento?"
    },
    "privategxt_confirm_clear_all": {
        "de": "Möchten Sie wirklich alle Dokumente löschen?",
        "en": "Are you sure you want to delete all documents?",
        "es": "¿Estás seguro de que quieres eliminar todos los documentos?"
    },
    "privategxt_delete_error": {
        "de": "Fehler beim Löschen des Dokuments",
        "en": "Error deleting document",
        "es": "Error al eliminar el documento"
    },
    "privategxt_clear_error": {
        "de": "Fehler beim Löschen aller Dokumente",
        "en": "Error clearing all documents",
        "es": "Error al borrar todos los documentos"
    },

    # Chat Section
    "privategxt_chat_title": {
        "de": "💬 Interaktiver Chat",
        "en": "💬 Interactive Chat",
        "es": "💬 Chat Interactivo"
    },
    "privategxt_chat_empty": {
        "de": "Stellen Sie Fragen zu Ihren Dokumenten",
        "en": "Ask questions about your documents",
        "es": "Haz preguntas sobre tus documentos"
    },
    "privategxt_chat_upload_first": {
        "de": "Bitte laden Sie zuerst Dokumente hoch, um den Chat zu verwenden.",
        "en": "Please upload documents first to use the chat.",
        "es": "Por favor sube documentos primero para usar el chat."
    },
    "privategxt_chat_input_placeholder": {
        "de": "Ihre Frage eingeben...",
        "en": "Enter your question...",
        "es": "Escribe tu pregunta..."
    },
    "privategxt_chat_error": {
        "de": "Fehler beim Senden der Nachricht. Bitte versuchen Sie es erneut.",
        "en": "Error sending message. Please try again.",
        "es": "Error al enviar el mensaje. Por favor, inténtalo de nuevo."
    },
    "privategxt_sources": {
        "de": "Quellen",
        "en": "Sources",
        "es": "Fuentes"
    },
    "privategxt_chat_ask_question": {
        "de": "Stellen Sie eine Frage zu Ihren Dokumenten",
        "en": "Ask a question about your documents",
        "es": "Haz una pregunta sobre tus documentos"
    },

    # LLM Provider Toggles
    "privategxt_llm_local": {
        "de": "Lokal (DSGVO)",
        "en": "Local (GDPR)",
        "es": "Local (RGPD)"
    },
    "privategxt_llm_grok": {
        "de": "Grok",
        "en": "Grok",
        "es": "Grok"
    },
    "privategxt_llm_anthropic": {
        "de": "Claude",
        "en": "Claude",
        "es": "Claude"
    },

    # External API Warning
    "privategxt_warning_external_title": {
        "de": "⚠️ Externe API - Keine DSGVO-Konformität",
        "en": "⚠️ External API - No GDPR Compliance",
        "es": "⚠️ API Externa - Sin Cumplimiento RGPD"
    },
    "privategxt_warning_external_message": {
        "de": "Sie verwenden eine externe API (Grok/Claude). Ihre Dokumente werden an externe Server gesendet. Für DSGVO-konforme Verarbeitung verwenden Sie bitte das lokale Ollama-Modell.",
        "en": "You are using an external API (Grok/Claude). Your documents will be sent to external servers. For GDPR-compliant processing, please use the local Ollama model.",
        "es": "Estás usando una API externa (Grok/Claude). Tus documentos se enviarán a servidores externos. Para un procesamiento conforme al RGPD, utiliza el modelo local Ollama."
    },

    # Footer
    "privategxt_footer_powered_by": {
        "de": "Powered by",
        "en": "Powered by",
        "es": "Desarrollado por"
    }
}

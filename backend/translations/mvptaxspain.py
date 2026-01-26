"""
MVP Tax Spain Translations
Multi-language support for MVP Tax Spain H7 Form Generator (German, English, Spanish)
"""
from typing import Dict, Literal

Language = Literal["de", "en", "es"]

MVPTAXSPAIN_TRANSLATIONS: Dict[str, Dict[Language, str]] = {
    # App General
    "app_title": {
        "de": "MVP Tax Spain - Steuerfallverwaltung",
        "en": "MVP Tax Spain - Tax Case Management",
        "es": "MVP Tax Spain - Gestión de Casos Fiscales"
    },
    "app_subtitle": {
        "de": "H7 Zollformular für Sendungen auf die Kanarischen Inseln",
        "en": "H7 Customs Form for Shipments to the Canary Islands",
        "es": "Formulario Aduanero H7 para Envíos a las Islas Canarias"
    },

    # Navigation
    "nav_free": {
        "de": "Kostenloser H7-Generator",
        "en": "Free H7 Generator",
        "es": "Generador H7 Gratuito"
    },
    "nav_login": {
        "de": "Anmelden",
        "en": "Login",
        "es": "Iniciar sesión"
    },
    "nav_register": {
        "de": "Registrieren",
        "en": "Register",
        "es": "Registrarse"
    },
    "nav_logout": {
        "de": "Abmelden",
        "en": "Logout",
        "es": "Cerrar sesión"
    },
    "nav_profile": {
        "de": "Profil",
        "en": "Profile",
        "es": "Perfil"
    },

    # Authentication
    "auth_email": {
        "de": "E-Mail",
        "en": "Email",
        "es": "Correo electrónico"
    },
    "auth_password": {
        "de": "Passwort",
        "en": "Password",
        "es": "Contraseña"
    },
    "auth_login": {
        "de": "Anmelden",
        "en": "Login",
        "es": "Iniciar sesión"
    },
    "auth_register": {
        "de": "Registrieren",
        "en": "Register",
        "es": "Registrarse"
    },
    "auth_logout": {
        "de": "Abmelden",
        "en": "Logout",
        "es": "Cerrar sesión"
    },
    "auth_login_title": {
        "de": "Bei MVP Tax Spain anmelden",
        "en": "Login to MVP Tax Spain",
        "es": "Iniciar sesión en MVP Tax Spain"
    },
    "auth_register_title": {
        "de": "Bei MVP Tax Spain registrieren",
        "en": "Register with MVP Tax Spain",
        "es": "Registrarse en MVP Tax Spain"
    },

    # Free H7 Generator
    "free_title": {
        "de": "Kostenloser H7-Generator",
        "en": "Free H7 Generator",
        "es": "Generador H7 Gratuito"
    },
    "free_subtitle": {
        "de": "Erstellen Sie Ihr H7-Zollformular in 3 einfachen Schritten",
        "en": "Create your H7 customs form in 3 easy steps",
        "es": "Cree su formulario aduanero H7 en 3 sencillos pasos"
    },
    "free_upload_mode": {
        "de": "Upload-Modus",
        "en": "Upload Mode",
        "es": "Modo de Carga"
    },
    "free_manual_mode": {
        "de": "Manueller Modus",
        "en": "Manual Mode",
        "es": "Modo Manual"
    },
    "free_upload_invoice": {
        "de": "Rechnung hochladen",
        "en": "Upload Invoice",
        "es": "Subir Factura"
    },
    "free_upload_invoice_desc": {
        "de": "Laden Sie Ihre Rechnung hoch und wir extrahieren die Daten automatisch",
        "en": "Upload your invoice and we'll extract the data automatically",
        "es": "Suba su factura y extraeremos los datos automáticamente"
    },
    "free_select_file": {
        "de": "Datei auswählen",
        "en": "Select File",
        "es": "Seleccionar Archivo"
    },
    "free_processing": {
        "de": "Verarbeite...",
        "en": "Processing...",
        "es": "Procesando..."
    },
    "free_extract_data": {
        "de": "Daten extrahieren",
        "en": "Extract Data",
        "es": "Extraer Datos"
    },
    "free_fill_manually": {
        "de": "Manuell ausfüllen",
        "en": "Fill Manually",
        "es": "Rellenar Manualmente"
    },

    # Form Sections
    "section_1": {
        "de": "1. Sendungsdetails",
        "en": "1. Shipment Details",
        "es": "1. Detalles del Envío"
    },
    "section_2": {
        "de": "2. Absender",
        "en": "2. Sender",
        "es": "2. Remitente"
    },
    "section_3": {
        "de": "3. Empfänger (Kanarische Inseln)",
        "en": "3. Recipient (Canary Islands)",
        "es": "3. Destinatario (Islas Canarias)"
    },
    "section_4": {
        "de": "4. Warenpositionen",
        "en": "4. Item Positions",
        "es": "4. Posiciones de Mercancías"
    },
    "section_5": {
        "de": "5. Rechnungsinformationen (nur B2C)",
        "en": "5. Invoice Information (B2C only)",
        "es": "5. Información de Factura (solo B2C)"
    },
    "section_6": {
        "de": "6. Zusätzliche Informationen",
        "en": "6. Additional Information",
        "es": "6. Información Adicional"
    },

    # Shipment Details
    "shipment_type": {
        "de": "Art der Sendung",
        "en": "Shipment Type",
        "es": "Tipo de Envío"
    },
    "shipment_type_b2c": {
        "de": "B2C (Business to Consumer)",
        "en": "B2C (Business to Consumer)",
        "es": "B2C (Empresa a Consumidor)"
    },
    "shipment_type_c2c": {
        "de": "C2C (Consumer to Consumer)",
        "en": "C2C (Consumer to Consumer)",
        "es": "C2C (Consumidor a Consumidor)"
    },
    "total_value": {
        "de": "Warenwert gesamt",
        "en": "Total Goods Value",
        "es": "Valor Total de Mercancías"
    },
    "currency": {
        "de": "Währung",
        "en": "Currency",
        "es": "Moneda"
    },
    "shipping_costs": {
        "de": "Versandkosten",
        "en": "Shipping Costs",
        "es": "Gastos de Envío"
    },
    "insurance_costs": {
        "de": "Versicherungskosten",
        "en": "Insurance Costs",
        "es": "Gastos de Seguro"
    },
    "total_for_customs": {
        "de": "Gesamtbetrag für Zollzwecke",
        "en": "Total Amount for Customs",
        "es": "Importe Total para Aduanas"
    },
    "delivery_type": {
        "de": "Art der Lieferung",
        "en": "Delivery Type",
        "es": "Tipo de Entrega"
    },
    "delivery_type_purchase": {
        "de": "Kauf",
        "en": "Purchase",
        "es": "Compra"
    },
    "delivery_type_gift": {
        "de": "Geschenk",
        "en": "Gift",
        "es": "Regalo"
    },

    # Sender Information
    "sender_name": {
        "de": "Name/Firma",
        "en": "Name/Company",
        "es": "Nombre/Empresa"
    },
    "sender_street": {
        "de": "Straße/Hausnummer",
        "en": "Street/Number",
        "es": "Calle/Número"
    },
    "sender_zip": {
        "de": "Postleitzahl",
        "en": "Postal Code",
        "es": "Código Postal"
    },
    "sender_city": {
        "de": "Ort",
        "en": "City",
        "es": "Localidad"
    },
    "sender_country": {
        "de": "Land",
        "en": "Country",
        "es": "País"
    },
    "sender_email": {
        "de": "E-Mail",
        "en": "Email",
        "es": "Correo electrónico"
    },
    "sender_phone": {
        "de": "Telefon",
        "en": "Phone",
        "es": "Teléfono"
    },

    # Recipient Information
    "recipient_name": {
        "de": "Name",
        "en": "Name",
        "es": "Nombre"
    },
    "recipient_street": {
        "de": "Straße/Hausnummer",
        "en": "Street/Number",
        "es": "Calle/Número"
    },
    "recipient_zip": {
        "de": "Postleitzahl",
        "en": "Postal Code",
        "es": "Código Postal"
    },
    "recipient_city": {
        "de": "Ort",
        "en": "City",
        "es": "Localidad"
    },
    "recipient_island": {
        "de": "Insel",
        "en": "Island",
        "es": "Isla"
    },
    "recipient_nif": {
        "de": "NIF/NIE/CIF",
        "en": "NIF/NIE/CIF",
        "es": "NIF/NIE/CIF"
    },
    "recipient_nif_help": {
        "de": "Spanische Steuer-ID",
        "en": "Spanish Tax ID",
        "es": "Identificación Fiscal Española"
    },
    "recipient_email": {
        "de": "E-Mail",
        "en": "Email",
        "es": "Correo electrónico"
    },
    "recipient_phone": {
        "de": "Telefon",
        "en": "Phone",
        "es": "Teléfono"
    },

    # Item Positions
    "add_position": {
        "de": "Position hinzufügen",
        "en": "Add Position",
        "es": "Añadir Posición"
    },
    "remove_position": {
        "de": "Position entfernen",
        "en": "Remove Position",
        "es": "Eliminar Posición"
    },
    "position": {
        "de": "Position",
        "en": "Position",
        "es": "Posición"
    },
    "item_description": {
        "de": "Warenbeschreibung",
        "en": "Item Description",
        "es": "Descripción de Mercancía"
    },
    "quantity": {
        "de": "Anzahl",
        "en": "Quantity",
        "es": "Cantidad"
    },
    "unit_price": {
        "de": "Stückpreis",
        "en": "Unit Price",
        "es": "Precio Unitario"
    },
    "total_price": {
        "de": "Gesamtpreis",
        "en": "Total Price",
        "es": "Precio Total"
    },
    "origin_country": {
        "de": "Ursprungsland",
        "en": "Country of Origin",
        "es": "País de Origen"
    },
    "customs_tariff": {
        "de": "Zolltarifnummer",
        "en": "Customs Tariff Number",
        "es": "Número de Arancel Aduanero"
    },
    "weight": {
        "de": "Gewicht (kg)",
        "en": "Weight (kg)",
        "es": "Peso (kg)"
    },
    "condition": {
        "de": "Zustand",
        "en": "Condition",
        "es": "Estado"
    },
    "condition_new": {
        "de": "Neu",
        "en": "New",
        "es": "Nuevo"
    },
    "condition_used": {
        "de": "Gebraucht",
        "en": "Used",
        "es": "Usado"
    },

    # Invoice Information
    "invoice_number": {
        "de": "Rechnungsnummer",
        "en": "Invoice Number",
        "es": "Número de Factura"
    },
    "invoice_date": {
        "de": "Rechnungsdatum",
        "en": "Invoice Date",
        "es": "Fecha de Factura"
    },
    "vat_shown": {
        "de": "MwSt. ausgewiesen",
        "en": "VAT Shown",
        "es": "IVA Indicado"
    },
    "proof_of_payment": {
        "de": "Zahlungsnachweis",
        "en": "Proof of Payment",
        "es": "Comprobante de Pago"
    },
    "proof_of_payment_help": {
        "de": "z.B. PayPal, Kreditkarte",
        "en": "e.g. PayPal, Credit Card",
        "es": "p.ej. PayPal, Tarjeta de Crédito"
    },

    # Additional Information
    "truth_declaration": {
        "de": "Ich erkläre hiermit, dass alle Angaben wahrheitsgemäß sind",
        "en": "I hereby declare that all information is truthful",
        "es": "Declaro por la presente que toda la información es veraz"
    },
    "remarks": {
        "de": "Bemerkungen",
        "en": "Remarks",
        "es": "Observaciones"
    },
    "export_pdf": {
        "de": "PDF exportieren",
        "en": "Export PDF",
        "es": "Exportar PDF"
    },

    # Form Fields
    "required": {
        "de": "Pflichtfeld",
        "en": "Required",
        "es": "Obligatorio"
    },
    "optional": {
        "de": "Optional",
        "en": "Optional",
        "es": "Opcional"
    },

    # Debug Status
    "debug_status": {
        "de": "Debug Export-Status",
        "en": "Debug Export Status",
        "es": "Estado de Exportación de Depuración"
    },
    "truth_declaration_label": {
        "de": "Wahrheitserklärung",
        "en": "Truth Declaration",
        "es": "Declaración de Veracidad"
    },
    "email_present": {
        "de": "Email vorhanden",
        "en": "Email Present",
        "es": "Correo Electrónico Presente"
    },
    "all_fields_validated": {
        "de": "Alle Felder validiert",
        "en": "All Fields Validated",
        "es": "Todos los Campos Validados"
    },
    "yes": {
        "de": "Ja",
        "en": "Yes",
        "es": "Sí"
    },
    "no": {
        "de": "Nein",
        "en": "No",
        "es": "No"
    },
    "missing_validations": {
        "de": "Fehlende Validierungen (Hauptfelder)",
        "en": "Missing Validations (Main Fields)",
        "es": "Validaciones Faltantes (Campos Principales)"
    },
    "all_main_fields_ok": {
        "de": "Alle Hauptfelder OK",
        "en": "All Main Fields OK",
        "es": "Todos los Campos Principales OK"
    },
    "item_validation": {
        "de": "Warenpositionen-Validierung",
        "en": "Item Validation",
        "es": "Validación de Artículos"
    },
    "no_items_present": {
        "de": "Keine Warenpositionen vorhanden!",
        "en": "No items present!",
        "es": "¡No hay artículos presentes!"
    },

    # Canary Islands
    "island_tenerife": {
        "de": "Teneriffa",
        "en": "Tenerife",
        "es": "Tenerife"
    },
    "island_gran_canaria": {
        "de": "Gran Canaria",
        "en": "Gran Canaria",
        "es": "Gran Canaria"
    },
    "island_lanzarote": {
        "de": "Lanzarote",
        "en": "Lanzarote",
        "es": "Lanzarote"
    },
    "island_fuerteventura": {
        "de": "Fuerteventura",
        "en": "Fuerteventura",
        "es": "Fuerteventura"
    },
    "island_la_palma": {
        "de": "La Palma",
        "en": "La Palma",
        "es": "La Palma"
    },
    "island_la_gomera": {
        "de": "La Gomera",
        "en": "La Gomera",
        "es": "La Gomera"
    },
    "island_el_hierro": {
        "de": "El Hierro",
        "en": "El Hierro",
        "es": "El Hierro"
    },

    # Validation Messages
    "validation_please_confirm_all_fields": {
        "de": "Bitte bestätigen Sie alle Pflichtfelder!",
        "en": "Please confirm all required fields!",
        "es": "¡Por favor confirme todos los campos obligatorios!"
    },
    "validation_all_fields_must_be_confirmed": {
        "de": "Alle Felder mit * müssen ausgefüllt UND mit dem grünen Häkchen bestätigt sein, bevor Sie das H7-Formular exportieren können.",
        "en": "All fields with * must be filled AND confirmed with the green checkmark before you can export the H7 form.",
        "es": "Todos los campos con * deben estar rellenados Y confirmados con la marca verde antes de poder exportar el formulario H7."
    },
    "validation_missing_fields": {
        "de": "Fehlende Felder",
        "en": "Missing Fields",
        "es": "Campos Faltantes"
    },

    # Common Actions
    "common_loading": {
        "de": "Lade...",
        "en": "Loading...",
        "es": "Cargando..."
    },
    "common_error": {
        "de": "Fehler",
        "en": "Error",
        "es": "Error"
    },
    "common_success": {
        "de": "Erfolg",
        "en": "Success",
        "es": "Éxito"
    },
    "common_cancel": {
        "de": "Abbrechen",
        "en": "Cancel",
        "es": "Cancelar"
    },
    "common_save": {
        "de": "Speichern",
        "en": "Save",
        "es": "Guardar"
    },
    "common_delete": {
        "de": "Löschen",
        "en": "Delete",
        "es": "Eliminar"
    },
    "common_edit": {
        "de": "Bearbeiten",
        "en": "Edit",
        "es": "Editar"
    },
    "common_close": {
        "de": "Schließen",
        "en": "Close",
        "es": "Cerrar"
    },
    "common_select": {
        "de": "Bitte wählen",
        "en": "Please select",
        "es": "Por favor seleccione"
    },
    "common_upload": {
        "de": "Hochladen",
        "en": "Upload",
        "es": "Subir"
    },
    "common_download": {
        "de": "Herunterladen",
        "en": "Download",
        "es": "Descargar"
    }
}

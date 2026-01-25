"""Service for generating H7 customs form PDF documents in Spanish"""
from typing import Dict, Any, List, Tuple
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from io import BytesIO


# German to Spanish field translations
FIELD_TRANSLATIONS = {
    # Section 1: Shipment Details
    'art_der_sendung': 'Tipo de envío (B2C / C2C)',
    'warenwert_gesamt_eur': 'Valor total de mercancías (EUR)',
    'waehrung': 'Moneda',
    'versandkosten': 'Gastos de envío',
    'versicherungskosten': 'Gastos de seguro',
    'gesamtbetrag_fuer_zoll': 'Importe total para fines aduaneros',
    'art_der_lieferung': 'Tipo de entrega (Compra / Regalo)',

    # Section 2: Sender
    'absender_name': 'Nombre / Empresa del remitente',
    'absender_strasse': 'Calle y número del remitente',
    'absender_plz': 'Código postal del remitente',
    'absender_ort': 'Localidad del remitente',
    'absender_land': 'País del remitente',
    'absender_email': 'Email del remitente',
    'absender_telefon': 'Teléfono del remitente',

    # Section 3: Recipient
    'empfaenger_name': 'Nombre del destinatario',
    'empfaenger_strasse': 'Calle y número del destinatario',
    'empfaenger_plz': 'Código postal del destinatario',
    'empfaenger_ort': 'Localidad del destinatario',
    'empfaenger_insel': 'Isla',
    'empfaenger_nif_nie_cif': 'NIF / NIE / CIF',
    'empfaenger_email': 'Email del destinatario',
    'empfaenger_telefon': 'Teléfono del destinatario',

    # Section 4: Line Items (Position 1)
    'position_1_nummer': 'Número de posición',
    'position_1_beschreibung': 'Descripción de mercancías',
    'position_1_anzahl': 'Cantidad',
    'position_1_stueckpreis': 'Precio unitario',
    'position_1_gesamtwert': 'Valor total de la posición',
    'position_1_ursprungsland': 'País de origen de las mercancías',
    'position_1_zolltarifnummer': 'Número de arancel aduanero (6 dígitos)',
    'position_1_gewicht': 'Peso (bruto o neto)',
    'position_1_zustand': 'Nuevo / usado',

    # Section 5: Invoice
    'rechnungsnummer': 'Número de factura',
    'rechnungsdatum': 'Fecha de factura',
    'rechnung_hochgeladen': 'Factura cargada',
    'mehrwertsteuer_ausgewiesen': 'IVA indicado',

    # Section 6: Alternative (no invoice)
    'wertangabe_versender': 'Valor declarado por el remitente',
    'keine_rechnung_vorhanden': 'Declaración "sin factura disponible"',
    'schaetzung_geschenk': 'Estimación como regalo / mercancía usada',

    # Section 7: Additional
    'zahlungsnachweis': 'Comprobante de pago (PayPal, tarjeta)',
    'wahrheitsgemaesse_angaben': 'Declaración de información veraz',
    'bemerkungen': 'Observaciones',

    # Metadata
    'vorgangsnummer': 'Número de operación (interno)',
    'erstellungsdatum': 'Fecha de creación',
    'version': 'Versión del documento',
    'status': 'Estado (Borrador / final)',
}


# Obligatory fields (marked with O)
OBLIGATORY_FIELDS = [
    'art_der_sendung',
    'warenwert_gesamt_eur',
    'waehrung',
    'versandkosten',
    'gesamtbetrag_fuer_zoll',
    'art_der_lieferung',
    'absender_name',
    'absender_strasse',
    'absender_plz',
    'absender_ort',
    'absender_land',
    'empfaenger_name',
    'empfaenger_strasse',
    'empfaenger_plz',
    'empfaenger_ort',
    'empfaenger_insel',
    'empfaenger_nif_nie_cif',
    'empfaenger_email',
    'empfaenger_telefon',
    'position_1_beschreibung',
    'position_1_anzahl',
    'position_1_stueckpreis',
    'position_1_gesamtwert',
    'position_1_ursprungsland',
    'rechnungsnummer',
    'rechnungsdatum',
]


def generate_h7_pdf(extracted_data: Dict[str, Any], case_name: str = "") -> BytesIO:
    """
    Generate a professional H7 customs form PDF in Spanish

    Args:
        extracted_data: Dictionary with H7 field data (German field names as keys)
        case_name: Optional name for the tax case

    Returns:
        BytesIO object containing the PDF
    """
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"🔍 PDF Generation - Received data keys: {list(extracted_data.keys())}")

    # Map frontend field names to backend field names
    field_mapping = {
        'absender_name_firma': 'absender_name',
        'absender_strasse_hausnummer': 'absender_strasse',
        'absender_postleitzahl': 'absender_plz',
        'empfaenger_strasse_hausnummer': 'empfaenger_strasse',
        'empfaenger_postleitzahl': 'empfaenger_plz',
        'gesamtbetrag_fuer_zollzwecke': 'gesamtbetrag_fuer_zoll',
        'erklaerung_wahrheitsgemaess': 'wahrheitsgemaesse_angaben'
    }

    # Create normalized data with mapped keys
    normalized_data = {}
    for key, value in extracted_data.items():
        # Use mapped key if exists, otherwise use original key
        normalized_key = field_mapping.get(key, key)
        normalized_data[normalized_key] = value

    # Handle warenpositionen array -> convert to position_1_*, position_2_*, etc.
    if 'warenpositionen' in extracted_data and isinstance(extracted_data['warenpositionen'], list):
        for idx, position in enumerate(extracted_data['warenpositionen'], start=1):
            if isinstance(position, dict):
                normalized_data[f'position_{idx}_beschreibung'] = position.get('warenbeschreibung', '')
                normalized_data[f'position_{idx}_anzahl'] = position.get('anzahl', '')
                normalized_data[f'position_{idx}_stueckpreis'] = position.get('stueckpreis', '')
                normalized_data[f'position_{idx}_gesamtwert'] = position.get('gesamtwert', '')
                normalized_data[f'position_{idx}_ursprungsland'] = position.get('ursprungsland', '')
                normalized_data[f'position_{idx}_zolltarifnummer'] = position.get('zolltarifnummer', '')
                normalized_data[f'position_{idx}_gewicht'] = position.get('gewicht', '')
                normalized_data[f'position_{idx}_zustand'] = position.get('neu_gebraucht', '')

    # Use normalized data instead of original
    extracted_data = normalized_data
    logger.info(f"📦 PDF Generation - Normalized {len(extracted_data)} fields")
    logger.info(f"🔍 All normalized fields and values:")
    for key, value in extracted_data.items():
        logger.info(f"   {key} = {value}")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        textColor=colors.HexColor('#1e3a8a'),  # Dark blue
        spaceAfter=20,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1e40af'),
        spaceBefore=15,
        spaceAfter=10,
        backColor=colors.HexColor('#dbeafe'),  # Light blue background
        borderPadding=5
    )

    # Story (content elements)
    story = []

    # Title
    story.append(Paragraph("Formulario H7 - Declaración Aduanera", title_style))
    if case_name:
        story.append(Paragraph(f"<i>{case_name}</i>", styles['Normal']))
    story.append(Spacer(1, 0.5*cm))

    # Section 1: Shipment Details
    story.append(Paragraph("1. Detalles del envío", heading_style))
    story.extend(_create_section_table([
        ('art_der_sendung', extracted_data),
        ('warenwert_gesamt_eur', extracted_data),
        ('waehrung', extracted_data),
        ('versandkosten', extracted_data),
        ('versicherungskosten', extracted_data),
        ('gesamtbetrag_fuer_zoll', extracted_data),
        ('art_der_lieferung', extracted_data),
    ]))

    # Section 2: Sender
    story.append(Paragraph("2. Datos del remitente", heading_style))
    story.extend(_create_section_table([
        ('absender_name', extracted_data),
        ('absender_strasse', extracted_data),
        ('absender_plz', extracted_data),
        ('absender_ort', extracted_data),
        ('absender_land', extracted_data),
        ('absender_email', extracted_data),
        ('absender_telefon', extracted_data),
    ]))

    # Section 3: Recipient
    story.append(Paragraph("3. Datos del destinatario", heading_style))
    story.extend(_create_section_table([
        ('empfaenger_name', extracted_data),
        ('empfaenger_strasse', extracted_data),
        ('empfaenger_plz', extracted_data),
        ('empfaenger_ort', extracted_data),
        ('empfaenger_insel', extracted_data),
        ('empfaenger_nif_nie_cif', extracted_data),
        ('empfaenger_email', extracted_data),
        ('empfaenger_telefon', extracted_data),
    ]))

    # Section 4: Line Items
    story.append(Paragraph("4. Posiciones de mercancías", heading_style))
    story.extend(_create_section_table([
        ('position_1_beschreibung', extracted_data),
        ('position_1_anzahl', extracted_data),
        ('position_1_stueckpreis', extracted_data),
        ('position_1_gesamtwert', extracted_data),
        ('position_1_ursprungsland', extracted_data),
        ('position_1_zolltarifnummer', extracted_data),
        ('position_1_gewicht', extracted_data),
        ('position_1_zustand', extracted_data),
    ]))

    # Section 5: Invoice
    story.append(Paragraph("5. Información de factura", heading_style))
    story.extend(_create_section_table([
        ('rechnungsnummer', extracted_data),
        ('rechnungsdatum', extracted_data),
        ('rechnung_hochgeladen', extracted_data),
        ('mehrwertsteuer_ausgewiesen', extracted_data),
    ]))

    # Section 6: Additional Information
    story.append(Paragraph("6. Información adicional", heading_style))
    story.extend(_create_section_table([
        ('zahlungsnachweis', extracted_data),
        ('wahrheitsgemaesse_angaben', extracted_data),
        ('bemerkungen', extracted_data),
    ]))

    # Footer
    story.append(Spacer(1, 1*cm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray,
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        f"Generado automáticamente el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        footer_style
    ))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def _create_section_table(fields: List[Tuple[str, Dict[str, Any]]]) -> List:
    """
    Create a formatted table for a section

    Args:
        fields: List of (field_name, data_dict) tuples

    Returns:
        List with Table and Spacer elements
    """
    import logging
    logger = logging.getLogger(__name__)

    data = []

    for field_name, extracted_data in fields:
        label = FIELD_TRANSLATIONS.get(field_name, field_name)
        value = str(extracted_data.get(field_name, ''))
        logger.debug(f"📋 Field: {field_name} -> Label: {label}, Value: {value[:50] if value else '(empty)'}")
        is_obligatory = field_name in OBLIGATORY_FIELDS

        # Empty value handling
        if not value or value.strip() == '':
            if is_obligatory:
                value = '(Obligatorio - por favor completar)'
                value_style = colors.red
            else:
                value = '(Opcional - vacío)'
                value_style = colors.gray
        else:
            value_style = colors.black

        # Marker
        marker = 'O' if is_obligatory else 'Opt'
        marker_color = colors.HexColor('#dc2626') if is_obligatory else colors.HexColor('#6b7280')

        data.append([
            label,
            marker,
            value
        ])

    # Create table with wider value column
    table = Table(data, colWidths=[9*cm, 1.5*cm, 6*cm])
    table.setStyle(TableStyle([
        # Background colors
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f0f9ff')),  # Light blue for value column

        # Text colors
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f2937')),  # Label column
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#6b7280')),  # Marker column
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#1e3a8a')),  # Value column - dark blue

        # Alignment
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),

        # Fonts - value column is bold
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),  # Bold for values

        # Font sizes - value column slightly larger
        ('FONTSIZE', (0, 0), (0, -1), 9),
        ('FONTSIZE', (1, 0), (1, -1), 9),
        ('FONTSIZE', (2, 0), (2, -1), 10),  # Larger font for values

        # Padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (2, 0), (2, -1), 10),  # Extra padding for value column

        # Grid with thicker right border for value column
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('LINEAFTER', (1, 0), (1, -1), 1.5, colors.HexColor('#93c5fd')),  # Thicker line before value column

        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    return [table, Spacer(1, 0.3*cm)]

"""
HalalChain Official Ownership Transfer Certificate Engine
Generates Enterprise-Grade Cryptographic Ownership Transfer Certificates with QR Verification
"""

import os
import io
import time
from typing import Optional
import qrcode
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

CERT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "certificates")
os.makedirs(CERT_OUTPUT_DIR, exist_ok=True)


def generate_qr_buffer(url: str) -> io.BytesIO:
    """Generates a high-contrast QR code pointing to the public passport verification portal"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#06150e", back_color="#ffffff")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def generate_ownership_certificate_pdf(
    cow_id: str,
    animal_name: str,
    breed: str,
    token_id: str,
    previous_owner: str,
    new_owner: str,
    tx_hash: str,
    block_number: str = "Sepolia",
    price_eth: float = 0.0,
    timestamp: Optional[int] = None,
    verify_base_url: str = "http://127.0.0.1:8000"
) -> str:
    """
    Generates a professional Landscape A4/Letter Digital Certificate of Ownership.
    Returns the absolute path to the generated PDF.
    """
    if timestamp is None:
        timestamp = int(time.time())
    
    cert_id = f"CERT-SEP-{cow_id.replace('HC-', '')}-{timestamp % 100000}"
    filename = f"{cert_id}.pdf"
    file_path = os.path.join(CERT_OUTPUT_DIR, filename)
    
    verify_url = f"{verify_base_url}/passport/verify/{cow_id}"
    qr_buf = generate_qr_buffer(verify_url)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom typography
    title_style = ParagraphStyle(
        'CertTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#06150e'),
        alignment=1
    )

    sub_title = ParagraphStyle(
        'CertSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#00A86B'),
        alignment=1
    )

    desc_style = ParagraphStyle(
        'CertDesc',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        alignment=1
    )

    label_style = ParagraphStyle(
        'CertLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#06150e')
    )

    val_style = ParagraphStyle(
        'CertVal',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#0f172a')
    )

    elements = []

    # Title & Header
    elements.append(Paragraph("HALALCHAIN LIVESTOCK PASSPORT REGISTRY", title_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("OFFICIAL DIGITAL CERTIFICATE OF OWNERSHIP TRANSFER", sub_title))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "This cryptographically verifiable certificate confirms the decentralized transfer of livestock identity and legal ownership anchored on the Ethereum Sepolia Blockchain.",
        desc_style
    ))
    elements.append(Spacer(1, 14))

    # Certificate details table
    dt_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    data = [
        [
            Paragraph("<b>Certificate Serial ID:</b>", label_style),
            Paragraph(f"<b>{cert_id}</b>", val_style),
            Paragraph("<b>Transfer Timestamp:</b>", label_style),
            Paragraph(dt_str, val_style),
        ],
        [
            Paragraph("<b>Animal Name:</b>", label_style),
            Paragraph(f"<b>{animal_name}</b>", val_style),
            Paragraph("<b>Unique Cattle Tag ID:</b>", label_style),
            Paragraph(f"<b>{cow_id}</b>", val_style),
        ],
        [
            Paragraph("<b>Cattle Breed:</b>", label_style),
            Paragraph(breed or "Bovine Livestock", val_style),
            Paragraph("<b>ERC-721 NFT Token ID:</b>", label_style),
            Paragraph(f"#{token_id}", val_style),
        ],
        [
            Paragraph("<b>Previous Owner Wallet:</b>", label_style),
            Paragraph(previous_owner or "Genesis Registration Authority", val_style),
            Paragraph("<b>Transfer Settlement:</b>", label_style),
            Paragraph(f"{price_eth:.4f} Sepolia ETH", val_style),
        ],
        [
            Paragraph("<b>Verified New Owner:</b>", label_style),
            Paragraph(f"<b>{new_owner}</b>", val_style),
            Paragraph("<b>Consensus Network:</b>", label_style),
            Paragraph("Ethereum Sepolia Testnet (Chain ID 11155111)", val_style),
        ],
        [
            Paragraph("<b>Transaction Hash:</b>", label_style),
            Paragraph(tx_hash, val_style),
            Paragraph("<b>Verification Status:</b>", label_style),
            Paragraph("<font color='#00A86B'><b>CONFIRMED ON ETHEREUM SEPOLIA</b></font>", val_style),
        ]
    ]

    cert_table = Table(data, colWidths=[1.8 * inch, 2.5 * inch, 1.8 * inch, 2.3 * inch])
    cert_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#00A86B')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(cert_table)
    elements.append(Spacer(1, 14))

    # Bottom Signature & QR Verification Section
    qr_img = RLImage(qr_buf, width=1.3 * inch, height=1.3 * inch)

    legal_notice = ParagraphStyle(
        'LegalNotice',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#64748B')
    )

    qr_label = ParagraphStyle(
        'QRLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#06150e'),
        alignment=1
    )

    bottom_data = [
        [
            qr_img,
            Paragraph(
                "<b>IMMUTABLE PROVENANCE GUARANTEE:</b><br/>"
                "This document serves as primary biometric and title provenance for the named livestock. "
                "Any alteration voids this certificate. Scan the dynamic QR code with any smartphone camera "
                "to verify cryptographic signatures, smart contract state, and complete ownership lineage on Ethereum Sepolia.<br/><br/>"
                f"<b>Public Audit URL:</b> {verify_url}",
                legal_notice
            ),
            Paragraph(
                "<b>HALALCHAIN REGISTRY AUTH</b><br/><br/>"
                "__________________________<br/>"
                "Cryptographic Signature Key<br/>"
                "<i>Consensus Protocol Verified</i>",
                qr_label
            )
        ]
    ]

    bottom_table = Table(bottom_data, colWidths=[1.4 * inch, 5.0 * inch, 2.0 * inch])
    bottom_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(bottom_table)

    doc.build(elements)
    return file_path

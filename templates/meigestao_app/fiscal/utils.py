from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime

def gerar_pdf_nota_fiscal(nota_fiscal):
    """Gera um PDF da nota fiscal"""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    elements.append(Paragraph("NOTA FISCAL", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Informações da NF
    info_data = [
        ['Número:', f"{nota_fiscal.numero}/{nota_fiscal.serie}", 'Data:', nota_fiscal.data_emissao.strftime('%d/%m/%Y')],
        ['Cliente:', nota_fiscal.cliente.nome, 'Status:', nota_fiscal.get_status_display()],
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabela de valores
    values_data = [
        ['Descrição', 'Valor'],
        ['Subtotal', f"R$ {nota_fiscal.valor_subtotal:.2f}"],
        ['Desconto', f"R$ {nota_fiscal.valor_desconto:.2f}"],
        ['ICMS', f"R$ {nota_fiscal.valor_icms:.2f}"],
        ['IPI', f"R$ {nota_fiscal.valor_ipi:.2f}"],
        ['TOTAL', f"R$ {nota_fiscal.valor_total:.2f}"],
    ]
    
    values_table = Table(values_data, colWidths=[4*inch, 2*inch])
    values_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(values_table)
    
    # Observações
    if nota_fiscal.observacoes:
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("<b>Observações:</b>", styles['Normal']))
        elements.append(Paragraph(nota_fiscal.observacoes, styles['Normal']))
    
    # Rodapé
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1
    )
    elements.append(Paragraph(
        f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}", 
        footer_style
    ))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
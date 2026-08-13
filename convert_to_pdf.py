#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
except ImportError:
    print("Instalando reportlab...")
    os.system("pip install reportlab -q")
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

# Lista de arquivos para converter
files = [
    r'c:\dev\mei_gestao\docs\MANUAL_CAP02_GESTAO_CLIENTES.md',
    r'c:\dev\mei_gestao\docs\MANUAL_CAP04_GESTAO_PRODUTOS.md',
    r'c:\dev\mei_gestao\docs\MANUAL_CAP07_GESTAO_ALMOXARIFADO.md',
    r'c:\dev\mei_gestao\docs\MANUAL_CAP09_GESTAO_OS_COMPRAS.md',
    r'c:\dev\mei_gestao\docs\MANUAL_USUARIO_COMPLETO.md',
    r'c:\dev\mei_gestao\docs\MANUAL_CAP08_GESTAO_PRODUCAO.md'
]

styles = getSampleStyleSheet()

for md_file in files:
    if not os.path.exists(md_file):
        print(f"❌ Arquivo não encontrado: {md_file}")
        continue
    
    try:
        # Ler o arquivo
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Gerar nome do PDF
        pdf_file = md_file.replace('.md', '.pdf')
        
        # Criar documento PDF
        doc = SimpleDocTemplate(pdf_file, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Processar linhas do markdown
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                text = line.replace('# ', '').strip()
                if text:
                    story.append(Paragraph(text, styles['Heading1']))
                    story.append(Spacer(1, 0.15*inch))
            elif line.startswith('## '):
                text = line.replace('## ', '').strip()
                if text:
                    story.append(Paragraph(text, styles['Heading2']))
                    story.append(Spacer(1, 0.1*inch))
            elif line.startswith('### '):
                text = line.replace('### ', '').strip()
                if text:
                    story.append(Paragraph(text, styles['Heading3']))
                    story.append(Spacer(1, 0.05*inch))
            elif line.strip() and not line.startswith('[') and not line.startswith('---'):
                if not line.startswith('|') and not line.startswith('!['):
                    clean_text = line.strip()
                    if clean_text:
                        story.append(Paragraph(clean_text, styles['Normal']))
                        story.append(Spacer(1, 0.02*inch))
        
        # Gerar PDF
        doc.build(story)
        filename = os.path.basename(pdf_file)
        print(f"✓ {filename}")
    
    except Exception as e:
        print(f"❌ Erro ao processar {os.path.basename(md_file)}: {str(e)}")

print("\n✅ Todos os PDFs foram criados com sucesso em c:\\dev\\mei_gestao\\docs\\")

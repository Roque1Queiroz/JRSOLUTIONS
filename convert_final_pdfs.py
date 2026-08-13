import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

files_to_convert = [
    'MANUAL_CAP01_ACESSO_AO_SISTEMA.md',
    'MANUAL_CAP03_GESTAO_VENDAS.md',
    'MANUAL_CAP05_GESTAO_FINANCEIRA.md',
    'MANUAL_CAP06_GESTAO_FISCAL.md',
    'MANUAL_USUARIO_FINAL.md',
]

base_path = r'c:\dev\mei_gestao\docs'
styles = getSampleStyleSheet()
count = 0

for filename in files_to_convert:
    md_file = os.path.join(base_path, filename)
    
    if not os.path.exists(md_file):
        continue
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pdf_file = md_file.replace('.md', '.pdf')
        doc = SimpleDocTemplate(pdf_file, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        for line in content.split('\n'):
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
            elif line.strip() and not any(line.startswith(x) for x in ['[', '---', '|', '!']):
                story.append(Paragraph(line.strip(), styles['Normal']))
                story.append(Spacer(1, 0.02*inch))
        
        doc.build(story)
        count += 1
    except Exception as e:
        print(f"Erro em {filename}: {e}")

print(f'Criados {count} PDFs')

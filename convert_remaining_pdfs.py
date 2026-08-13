import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

files = [
    r'c:\dev\mei_gestao\docs\MANUAL_CAP01_ACESSO_AO_SISTEMA.md',
    r'c:\dev\mei_gestao\docs\MANUAL_CAP03_GESTAO_VENDAS.md',
    r'c:\dev\mei_gestao\docs\MANUAL_CAP05_GESTAO_FINANCEIRA.md',
    r'c:\dev\mei_gestao\docs\MANUAL_CAP06_GESTAO_FISCAL.md',
    r'c:\dev\mei_gestao\docs\MANUAL_USUARIO_FINAL.md',
]

styles = getSampleStyleSheet()

for md_file in files:
    if not os.path.exists(md_file):
        print(f'Arquivo não encontrado: {os.path.basename(md_file)}')
        continue
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pdf_file = md_file.replace('.md', '.pdf')
        doc = SimpleDocTemplate(pdf_file, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
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
        
        doc.build(story)
        print(f'✓ {os.path.basename(pdf_file)}')
    
    except Exception as e:
        print(f'❌ Erro: {os.path.basename(md_file)}: {str(e)}')

print('Concluído!')

import io
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={}):
    """
    Utilitário para converter templates Django em arquivos PDF usando xhtml2pdf.
    """
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    
    # Cria o PDF
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

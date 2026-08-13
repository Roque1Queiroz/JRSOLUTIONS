from django.core.exceptions import ObjectDoesNotExist
from meigestao_app.financeiro.models import ReciboReembolso
from meigestao_app.core.models import Empresa

def _get_user_empresa(user):
    try:
        return user.perfil.empresa
    except (AttributeError, ObjectDoesNotExist):
        return None

def notifications(request):
    """Context processor para notificações globais e dados da empresa."""
    context = {
        'reembolsos_pendentes_count': 0,
        'empresa_obj': None,
        'empresa_logo_url': None,
        'empresa_nome': 'SISTEMA GESTOR'
    }
    
    if request.user.is_authenticated:
        empresa = _get_user_empresa(request.user)
        if not empresa and request.user.is_staff:
            empresa = Empresa.objects.first()
            
        if empresa:
            pendentes = ReciboReembolso.objects.filter(empresa=empresa, pago=False).count()
            context['empresa_obj'] = empresa
            if empresa.logo:
                context['empresa_logo_url'] = empresa.logo.url
            context['empresa_nome'] = empresa.nome
        elif request.user.is_staff:
            pendentes = ReciboReembolso.objects.filter(pago=False).count()
        else:
            pendentes = 0
             
        context['reembolsos_pendentes_count'] = pendentes
        
    return context

from meigestao_app.core.models import Empresa

def get_empresa_do_usuario(user):
    """Retorna a empresa do perfil do usuário, ou None se não existir."""
    try:
        # Tenta pegar a empresa do perfil
        if hasattr(user, 'perfil') and user.perfil.empresa:
            return user.perfil.empresa
        
        # Fallback: Se for staff/admin e não tiver perfil, pega a primeira empresa cadastrada
        if user.is_staff or user.is_superuser:
            return Empresa.objects.first()
            
        return None
    except Exception:
        return None

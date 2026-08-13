from django.core.exceptions import ObjectDoesNotExist


def get_empresa_do_usuario(user):
    """Retorna apenas a empresa explicitamente vinculada ao perfil do usuário."""
    try:
        return user.perfil.empresa
    except (AttributeError, ObjectDoesNotExist):
        return None

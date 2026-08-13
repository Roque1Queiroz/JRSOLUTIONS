from django.core.exceptions import ImproperlyConfigured, PermissionDenied

from meigestao_app.core.utils.helpers import get_empresa_do_usuario


class EmpresaQuerysetMixin:
    """Restringe o queryset da view à empresa vinculada ao usuário."""

    empresa_lookup = "empresa"

    def get_empresa(self):
        return get_empresa_do_usuario(self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        empresa = self.get_empresa()
        if empresa is None:
            return queryset.none()
        if not self.empresa_lookup:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} deve definir empresa_lookup."
            )
        return queryset.filter(**{self.empresa_lookup: empresa})


class PerfilPermissaoMixin:
    """Exige perfil ativo com uma das funções de negócio declaradas."""

    permissoes_permitidas = ()

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return super().dispatch(request, *args, **kwargs)
            perfil = getattr(request.user, 'perfil', None)
            if (
                not perfil
                or not perfil.ativo
                or perfil.permissao not in self.permissoes_permitidas
            ):
                raise PermissionDenied('Usuário sem permissão para executar esta ação.')
        return super().dispatch(request, *args, **kwargs)


class EmpresaFormMixin:
    """Injeta a empresa do usuário em formulários tenant-aware."""

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = get_empresa_do_usuario(self.request.user)
        return kwargs

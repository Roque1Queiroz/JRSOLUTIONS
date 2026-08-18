from django.core.exceptions import ImproperlyConfigured, PermissionDenied

from meigestao_app.core.utils.helpers import get_empresa_do_usuario
from meigestao_app.core.permissoes import funcao_pode_ver_modulo, funcao_pode_alterar_modulo, funcao_pode_excluir_modulo


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
    """
    (Compatibilidade) Exige perfil ativo com uma das funções de negócio em
    `permissoes_permitidas`. Mantido para views legadas como as de estoque.
    NOTA: mantém o comportamento original, sem bypass automático de staff.
    """

    permissoes_permitidas = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
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


def funcao_do_usuario(user):
    """Retorna a função do perfil do usuário, ou None se não tiver perfil."""
    if getattr(user, "is_authenticated", False) and not user.is_authenticated:
        return None
    if user.is_superuser:
        return 'admin'
    perfil = getattr(user, 'perfil', None)
    if not perfil:
        return None
    return getattr(perfil, 'permissao', None)


class ExigeModuloPermissaoMixin:
    """
    Exige que a função do usuário possa VER o módulo desta view.

    Use quando a view pertence a um módulo e o acesso deve ser filtrado pela
    matriz central (core.permissoes). Permite leitura (ver) — para restringir
    gravação, combine com variante de escrita.
    """

    modulo = None               # nome do módulo (ex.: 'vendas'); obrigatório.
    allow_admin = True          # admin/superuser passa sempre.

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.allow_admin and (request.user.is_superuser or getattr(request.user, 'is_staff', False)):
            return super().dispatch(request, *args, **kwargs)

        if not self.modulo:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} deve definir `modulo`."
            )
        func = funcao_do_usuario(request.user)
        if not func or not funcao_pode_ver_modulo(func, self.modulo):
            raise PermissionDenied('Usuário sem permissão para acessar este módulo.')
        return super().dispatch(request, *args, **kwargs)


class ExigeEscritaModuloMixin(ExigeModuloPermissaoMixin):
    """
    Igual ao ExigeModuloPermissaoMixin, mas para ações de CRIAR/EDITAR.
    Usado em CreateView/UpdateView.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.allow_admin and (request.user.is_superuser or getattr(request.user, 'is_staff', False)):
            return super().dispatch(request, *args, **kwargs)
        if not self.modulo:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} deve definir `modulo`."
            )
        func = funcao_do_usuario(request.user)
        if not func or not funcao_pode_alterar_modulo(func, self.modulo):
            raise PermissionDenied('Usuário sem permissão para alterar neste módulo.')
        return super().dispatch(request, *args, **kwargs)


class ExigeExclusaoModuloMixin(ExigeModuloPermissaoMixin):
    """
    Igual ao ExigeModuloPermissaoMixin, mas para ações de EXCLUIR.
    Usado em DeleteView.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.allow_admin and (request.user.is_superuser or getattr(request.user, 'is_staff', False)):
            return super().dispatch(request, *args, **kwargs)
        if not self.modulo:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} deve definir `modulo`."
            )
        func = funcao_do_usuario(request.user)
        if not func or not funcao_pode_excluir_modulo(func, self.modulo):
            raise PermissionDenied('Usuário sem permissão para excluir neste módulo.')
        return super().dispatch(request, *args, **kwargs)


def exige_modulo_visualizacao(modulo):
    """Decorator para function-based views: exige VER o módulo."""
    from django.core.exceptions import PermissionDenied
    def _decorator(view_func):
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                return redirect(getattr(request, 'login_url', 'login'))
            if request.user.is_superuser or getattr(request.user, 'is_staff', False):
                return view_func(request, *args, **kwargs)
            func = funcao_do_usuario(request.user)
            if not func or not funcao_pode_ver_modulo(func, modulo):
                raise PermissionDenied('Usuário sem permissão para acessar este módulo.')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return _decorator


def exige_modulo_escrita(modulo):
    """Decorator para function-based views de CRIAR/EDITAR."""
    from django.core.exceptions import PermissionDenied
    def _decorator(view_func):
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                return redirect(getattr(request, 'login_url', 'login'))
            if request.user.is_superuser or getattr(request.user, 'is_staff', False):
                return view_func(request, *args, **kwargs)
            func = funcao_do_usuario(request.user)
            if not func or not funcao_pode_alterar_modulo(func, modulo):
                raise PermissionDenied('Usuário sem permissão para alterar neste módulo.')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return _decorator


class EmpresaFormMixin:
    """Injeta a empresa do usuário em formulários tenant-aware."""

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = get_empresa_do_usuario(self.request.user)
        return kwargs

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve, Resolver404

class SaaSPlanRestrictionMiddleware:
    """
    Middleware para impor limites e restrições de acesso a módulos
    de acordo com o plano contratado pela Empresa do usuário.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Usuário não autenticado não é verificado por este middleware
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Superusuários e administradores do sistema têm acesso livre
        if request.user.is_superuser or request.user.is_staff:
            return self.get_response(request)

        # Localiza o perfil e a empresa do usuário logado
        try:
            empresa = request.user.perfil.empresa
        except AttributeError:
            return self.get_response(request)

        if not empresa:
            return self.get_response(request)

        plano = getattr(empresa, 'plano', 'basico')

        # Tenta resolver a rota atual para obter namespaces e nomes de views
        try:
            resolver_match = resolve(request.path_info)
            namespace = resolver_match.namespace
            app_name = resolver_match.app_name
            url_name = resolver_match.url_name
        except Resolver404:
            namespace = None
            app_name = None
            url_name = None

        path = request.path_info.strip('/')

        # ─── TESTE GRÁTIS ENCERRADO (30 dias de acesso total) ───
        # Empresa que recebeu teste (Enterprise) e já ultrapassou a data limite é
        # BLOQUEADA do sistema até escolher/pagar um plano. Só a página de escolha
        # de plano, o logout e o admin permanecem acessíveis.
        if getattr(empresa, 'teste_expirado', False):
            if url_name not in ('escolher_plano', 'logout') and namespace != 'admin':
                messages.warning(
                    request,
                    'Seu teste grátis de 30 dias terminou. Escolha um plano para continuar usando.',
                )
                return redirect('core:escolher_plano')

        # ─── RESTRIÇÕES DO PLANO BÁSICO ───
        if plano == 'basico':
            # Módulos não autorizados no Plano Básico
            namespaces_bloqueados = ['fiscal', 'almoxarifado', 'compras', 'servicos', 'producao', 'relatorios']
            is_blocked = False

            if namespace in namespaces_bloqueados or app_name in namespaces_bloqueados:
                is_blocked = True
            else:
                # Fallback usando prefixo da rota caso namespace não tenha sido setado
                for ns in namespaces_bloqueados:
                    if path.startswith(ns):
                        is_blocked = True
                        break

            # Bloqueio de White Label (Setup Empresa) no Plano Básico
            if url_name == 'setup_whitelabel' or path.startswith('core/setup-empresa'):
                is_blocked = True

            if is_blocked:
                messages.warning(request, "Este módulo/recurso não faz parte do seu Plano Básico. Faça um upgrade para liberá-lo!")
                return redirect('core:dashboard')

        # ─── RESTRIÇÕES DO PLANO PROFISSIONAL ───
        # Ambos Básico e Profissional não possuem acesso a APIs customizadas (somente Enterprise)
        if plano in ['basico', 'profissional']:
            if path.startswith('api/custom') or url_name == 'custom_api':
                messages.warning(request, "APIs customizadas estão disponíveis apenas no Plano Enterprise (Indústria).")
                return redirect('core:dashboard')

        return self.get_response(request)

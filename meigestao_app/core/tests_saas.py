from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from meigestao_app.core.models import Empresa
from meigestao_app.usuarios.models import Perfil
import datetime


class SaaSPlanLimitesTestCase(TestCase):
    """Valida as regras de limite de usuários por plano."""

    def setUp(self):
        self.empresa_basica = Empresa.objects.create(
            nome="Empresa Básica Ltda",
            cnpj="00.000.000/0001-00",
            plano="basico"
        )
        self.empresa_profissional = Empresa.objects.create(
            nome="Empresa Pro Ltda",
            cnpj="11.111.111/0001-11",
            plano="profissional"
        )
        self.user1 = User.objects.create_user(username="user1", password="pass1")
        self.user2 = User.objects.create_user(username="user2", password="pass1")
        self.user3 = User.objects.create_user(username="user3", password="pass1")

    def _criar_perfil(self, user, empresa):
        return Perfil.objects.create(
            usuario=user,
            empresa=empresa,
            permissao="operador",
            data_admissao=datetime.date.today()
        )

    def test_limite_usuarios_basico_bloqueado(self):
        """Plano básico: 3º usuário deve ser barrado com ValidationError."""
        self._criar_perfil(self.user1, self.empresa_basica)
        self._criar_perfil(self.user2, self.empresa_basica)

        with self.assertRaises(ValidationError):
            p = Perfil(
                usuario=self.user3,
                empresa=self.empresa_basica,
                permissao="operador",
                data_admissao=datetime.date.today()
            )
            p.save()

    def test_limite_usuarios_profissional_permitido(self):
        """Plano profissional: 3 usuários devem ser criados sem erro."""
        for user in [self.user1, self.user2, self.user3]:
            self._criar_perfil(user, self.empresa_profissional)
        self.assertEqual(self.empresa_profissional.usuarios.count(), 3)

    def test_propriedades_basico(self):
        """Plano básico: IA, whitelabel e APIs devem ser False."""
        e = self.empresa_basica
        self.assertFalse(e.tem_ia)
        self.assertFalse(e.tem_whitelabel)
        self.assertFalse(e.tem_apis_customizadas)
        self.assertEqual(e.limite_usuarios, 2)

    def test_propriedades_profissional(self):
        """Plano profissional: IA e whitelabel True, APIs False."""
        e = self.empresa_profissional
        self.assertTrue(e.tem_ia)
        self.assertTrue(e.tem_whitelabel)
        self.assertFalse(e.tem_apis_customizadas)
        self.assertEqual(e.limite_usuarios, 5)

    def test_propriedades_enterprise(self):
        """Plano enterprise: todas as propriedades True, limite 20."""
        empresa = Empresa.objects.create(
            nome="Enterprise SA", cnpj="22.222.222/0001-22", plano="enterprise"
        )
        self.assertTrue(empresa.tem_ia)
        self.assertTrue(empresa.tem_whitelabel)
        self.assertTrue(empresa.tem_apis_customizadas)
        self.assertEqual(empresa.limite_usuarios, 20)


class SaaSMiddlewareTestCase(TestCase):
    """Valida que o middleware redireciona conforme o plano."""

    def setUp(self):
        self.empresa_basica = Empresa.objects.create(
            nome="Básica Teste", cnpj="33.333.333/0001-33", plano="basico"
        )
        self.empresa_pro = Empresa.objects.create(
            nome="Pro Teste", cnpj="44.444.444/0001-44", plano="profissional"
        )

        # Usuário do plano básico
        self.user_basico = User.objects.create_user(username="basicuser", password="pass")
        Perfil.objects.create(
            usuario=self.user_basico,
            empresa=self.empresa_basica,
            permissao="operador",
            data_admissao=datetime.date.today()
        )

        # Usuário do plano profissional
        self.user_pro = User.objects.create_user(username="prouser", password="pass")
        Perfil.objects.create(
            usuario=self.user_pro,
            empresa=self.empresa_pro,
            permissao="admin",
            data_admissao=datetime.date.today()
        )

    def test_basico_bloqueado_em_whitelabel(self):
        """Usuário básico tentando acessar setup_whitelabel deve ser redirecionado para dashboard."""
        self.client.login(username="basicuser", password="pass")
        response = self.client.get(reverse('core:setup_whitelabel'))
        # Deve redirecionar para o dashboard (middleware bloqueia antes de chegar na view)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/core/', response['Location'])

    def test_basico_dashboard_acessivel(self):
        """Usuário básico deve acessar o dashboard normalmente."""
        self.client.login(username="basicuser", password="pass")
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_pro_acessa_whitelabel(self):
        """Usuário profissional deve acessar setup_whitelabel sem redirecionamento do middleware."""
        self.client.login(username="prouser", password="pass")
        response = self.client.get(reverse('core:setup_whitelabel'))
        # Pode ser 200 (acessou) ou 302 para o login de admin — mas NÃO deve ir para o dashboard
        if response.status_code == 302:
            self.assertNotIn('/core/', response.get('Location', ''))

    def test_plano_detail_acessivel(self):
        """A página de planos deve ser acessível para qualquer usuário autenticado."""
        self.client.login(username="basicuser", password="pass")
        response = self.client.get(reverse('core:plano_detail'))
        self.assertEqual(response.status_code, 200)

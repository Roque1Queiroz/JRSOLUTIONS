# -*- coding: utf-8 -*-
"""Testes do proxy Django /chatbot-api/ -> servico do bot (on-premise).

Garante que:
- O proxy encaminha para CHATBOT_INTERNAL_URL (rede Docker interna).
- O retorno do bot chega ao frontend sem expor a porta 8003.
- Quando CHATBOT_INTERNAL_URL nao esta configurada, devolve 503 (sem 8003).
"""
from unittest.mock import patch, MagicMock

import pytest
from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse

from meigestao_app.core.models import Empresa
from meigestao_app.usuarios.models import Perfil


def _empresa_usuario(username='bot_proxy', empresa_nome='BotProxy'):
    empresa = Empresa.objects.create(nome=empresa_nome, cnpj='95.000.000/0001-95', plano='enterprise')
    user = User.objects.create_user(username=username, password='senha-forte-de-teste-123')
    Perfil.objects.create(usuario=user, empresa=empresa, permissao='admin', data_admissao='2026-10-21')
    return empresa, user


@pytest.mark.django_db
def test_chatbot_chat_encaminha_para_url_interna_e_nao_devolve_8003(client):
    """CA2: /chatbot-api/chat encaminha para CHATBOT_INTERNAL_URL e a
    resposta nunca traz o texto '8003' (so a URL interna do Docker e usada)."""
    _, user = _empresa_usuario()
    client.force_login(user)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'answer': 'Ola! Como posso ajudar?'}
    mock_response.content = b'{"answer":"Ola! Como posso ajudar?"}'
    mock_response.headers = {'Content-Type': 'application/json'}

    with override_settings(CHATBOT_INTERNAL_URL='http://chatbot:8003'):
        with patch('meigestao_app.core.views.requests.post', return_value=mock_response) as mock_post:
            response = client.post(
                reverse('core:chatbot_proxy'),
                data={'session_id': 's1', 'message': 'oi'},
                content_type='application/json',
            )

    assert response.status_code == 200
    assert response.json()['answer'] == 'Ola! Como posso ajudar?'
    # Garantiu que chamou a URL interna do Docker (chatbot:8003), NAO localhost:8003
    assert mock_post.call_args.args[0] == 'http://chatbot:8003/chat'
    # Resposta nao vaza a porta 8003 no payload que volta pro frontend
    assert b'8003' not in response.content
    assert b'8003' not in response.json().get('answer', '').encode()


@pytest.mark.django_db
def test_chatbot_chat_sem_url_interna_retorna_503_amigavel(client):
    """Se CHATBOT_INTERNAL_URL nao esta configurada (ex.: banco de
    desenvolvimento local sem bot), devolve 503 com mensagem amigavel
    que NAO menciona '8003' nem a frase original de erro de conexao."""
    _, user = _empresa_usuario(username='bot_proxy_503')
    client.force_login(user)

    with override_settings(CHATBOT_INTERNAL_URL=''):
        response = client.post(
            reverse('core:chatbot_proxy'),
            data={'session_id': 's2', 'message': 'oi'},
            content_type='application/json',
        )

    assert response.status_code == 503
    body = response.json()
    # Mensagem em portugues, sem expor detalhes tecnicos como a porta
    assert 'assistente' in body.get('detail', '').lower() or 'configurado' in body.get('detail', '').lower()
    assert '8003' not in body.get('detail', '')

# -*- coding: utf-8 -*-
"""Aplica as 2 mudancas de frontend no base.html da VM (idempotente).
1) Buscar empresaDados via endpoint seguro Django.
2) Enviar empresa_dados no body do POST /chat.
Preserva o API_URL original da VM (que pode ser '/chatbot-api')."""
p = "/home/ubuntu/Sistema_Gestor/templates/base.html"
s = open(p, encoding="utf-8").read()

# --- 1) inserir bloco de fetch apos a definicao do API_URL ---
if "bot/contexto" not in s:
    api_anchor = "const API_URL"
    i = s.find(api_anchor)
    assert i != -1, "API_URL apos string nao encontrado"
    # encontra o fim da linha da definicao do API_URL
    fim_linha = s.find("\n", i)
    bloco_fetch = '''

        // Dados agregados e SEGUROS da empresa autenticada (via Django), que o
        // assistente pode usar como contexto alem do manual. Endpoint @login_required.
        let empresaDados = null;
        fetch(`${window.location.origin}/core/bot/contexto/`)
            .then(r => r.ok ? r.json() : null)
            .then(d => { empresaDados = d; })
            .catch(() => { empresaDados = null; });
'''
    s = s[:fim_linha] + bloco_fetch + s[fim_linha+1:]
    print("OK: fetch empresaDados inserido")
else:
    print("SKIP: fetch empresaDados ja presente")

# --- 2) incluir empresa_dados no body de envio (se ainda nao tiver) ---
if "empresa_dados" not in s:
    old_body = "body: JSON.stringify({ session_id: sessionId, message: message })"
    new_body = "body: JSON.stringify({ session_id: sessionId, message: message, empresa_dados: empresaDados })"
    assert old_body in s, "body de envio nao encontrado"
    s = s.replace(old_body, new_body, 1)
    print("OK: empresa_dados incluido no body")
else:
    print("SKIP: empresa_dados ja presente")

open(p, "w", encoding="utf-8").write(s)
print("FEITO")

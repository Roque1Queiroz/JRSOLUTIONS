# Spec — Bot no pacote on-premise

| Campo | Valor |
|---|---|
| **Versão** | 1.0 |
| **Status** | implementado em 2026-10-22 — 4/4 CA verdes (proxy 2/2 + zip 4/4 + fonte 3/3, slice 1-4); testes em `meigestao_app/core/test_chatbot_proxy.py`, `test_chatbot_onpremise_zip.py`, `test_chatbot_onpremise_fonte.py`. Ver `docs/chatbot_gestor_ref/servico/README.md` para origem de cada arquivo. |
| **Autor** | José Roque / Hermes |
| **Data** | 2026-10-10 |
| **Módulos afetados** | core (proxy), deploy-cliente, serviço do chatbot |
| **Plano** | todos (o chat já é de todos os planos) |

DECISÃO (José, 2026-10-09 21h): o bot entra na fila para funcionar no modelo on-premise. Não é um produto novo. É o mesmo assistente da nuvem, dentro do pacote que o cliente instala.

---

## 1. Objetivo

No pacote on-premise o botão do assistente chama `/chatbot-api` e não acha ninguém. Na nuvem o nginx manda isso para o bot na porta 8003. No cliente não tem nginx nem o serviço. O chat tem que responder depois de instalar o zip, sem abrir a porta 8003 no Windows.

## 2. Contexto atual

- O navegador, em `templates/base.html`, chama `${window.location.origin}/chatbot-api/chat`. Não chama a porta 8003.
- O pacote `deploy-cliente/docker-compose.yml` sobe Postgres, Redis, web, worker e beat. Não sobe bot. Não publica proxy de `/chatbot-api`.
- A cópia de referência em `docs/chatbot_gestor_ref/` tem `main.py` e `rag.py`, e não tem `database.py`, `models.py`, Dockerfile nem requirements. O diretório `/home/ubuntu/chatbot_gestor` não está nesta máquina.
- O bot de referência usa Groq + Chroma e não tem login próprio. O contexto da empresa vem de `GET /core/bot/contexto/`, que já exige login.
- Sem internet e sem `GROQ_API_KEY`, o Groq não responde. Isso não vira bot offline nesta leva.

## 3. Escopo

- **Incluído:**
  - Serviço do bot na rede interna do Docker do cliente. Sem porta publicada no Windows.
  - O Django atende `/chatbot-api/` e encaminha para o bot interno, para o endereço que o navegador já usa continuar valendo.
  - Na primeira subida, indexar `docs/MANUAL_EMBED_BOT.md` se o índice ainda não existir.
  - `GROQ_API_KEY` no `.env` do cliente. O `.env.example` ganha a chave em branco e um comentário. Nunca gravar a chave real no zip.
  - O pacote zip passa a incluir o serviço.
- **Excluído:**
  - Reescrever o bot como microserviço agnóstico.
  - Login novo no bot, se o encaminhamento continuar saindo só do Django já logado. O `/upload` do bot não pode ficar aberto na rede do cliente.
  - Bot que funcione sem internet e sem chave Groq.
  - Inventar o código do bot se a fonte real não for encontrada. Nesse caso, parar este item, dizer onde faltou, e não fingir que o chat responde.

## 4. Requisitos Funcionais

- RF1 — Com o compose no ar e a chave Groq preenchida, o chat da tela responde pelo mesmo endereço `/chatbot-api/chat`.
- RF2 — A porta 8003 não aparece no `docker compose` publicada para o Windows.
- RF3 — Sem a chave, a tela diz que o assistente não está configurado. Não mostra "porta 8003".
- RF4 — O manual do sistema entra no índice na primeira subida, sem comando manual, se o índice estiver vazio.

## 5. Requisitos Não-Funcionais

- O zip não leva `.env` real nem chave.
- O bot só é alcançado pela rede Docker e pelo encaminhamento do Django.

## 6. Dados / Modelo

Nenhum modelo novo no ERP. O histórico do bot continua no serviço dele.

Variável nova no `.env.example`: `GROQ_API_KEY=` e `CHATBOT_INTERNAL_URL=http://chatbot:8003`.

## 7. Fluxo

1. Cliente instala ou atualiza o zip.
2. Coloca a chave Groq no `.env` dele, sem apagar o resto.
3. Sobe o compose.
4. Abre o sistema e usa o chat.

## 8. Segurança

- Não publicar 8003.
- Não aceitar upload de manual por uma URL pública.
- A chave fica só no `.env` do cliente.

## 9. Critérios de Aceite

- CA1 — O compose do pacote declara o serviço do bot sem `ports` no host.
- CA2 — Um teste do Django mostra que `/chatbot-api/chat` encaminha para a URL interna, e não devolve a frase da porta 8003.
- CA3 — O empacotador não coloca arquivo `.env` real no zip.
- CA4 — Se a fonte completa do bot não existir, o item fica bloqueado com o caminho que faltou, e o restante da leva não é cancelado por isso.

## 10. Riscos

- A fonte viva do bot pode estar só na VM antiga e não neste disco. Procurar antes de reescrever.
- Groq é serviço externo. O cliente on-premise precisa de internet na hora do chat.

Implementar nesta leva das 22h, depois dos itens 1 a 3, se a fonte aparecer. Se não aparecer, registrar o bloqueio e seguir o zip com o que estiver pronto, deixando este item visível como não feito.

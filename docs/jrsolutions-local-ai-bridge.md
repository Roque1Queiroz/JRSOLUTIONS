
---
name: jrsolutions-local-ai-bridge
description: Diretrizes e Implementação para conectar a interface com modelos de IA locais (Ollama/Llama) no MEI Gestão (Django).
---

# Integração IA Local (Ollama/Llama) no MEI Gestão (Django + JS)

Este documento define as diretrizes para implementar um assistente de IA local para fornecer suporte aos usuários do sistema **MEI Gestão**, utilizando a stack de tecnologia nativa do projeto (Django no Backend e HTML/JS no Frontend).

## 1. Comunicação
- **Backend (Python/Django):** Criar uma `view` dedicada para fazer a ponte entre o seu frontend e a API local do Ollama (`http://localhost:11434/api/generate`). Pode-se utilizar a biblioteca `requests` (para chamadas síncronas simples) ou `aiohttp`/Django Async (se quiser verdadeiro assincronismo no servidor).
- **Frontend (JavaScript):** As chamadas da interface de usuário (HTML) para a sua view do Django devem utilizar a função `fetch()` (AJAX) de forma assíncrona (`async`/`await`). Isso garante que a página não recarregue e a interface não trave enquanto a IA "pensa".

## 2. Contexto de Suporte (Prompt System)
- A lógica de Prompt deve ficar protegida no **Backend**.
- Sempre concatenar um "System Prompt" antes da pergunta do usuário, definindo que a IA é o "Suporte do SISTEMA GESTOR" (MEI Gestão).
- Restringir respostas a apenas funcionalidades do software (ex: Vendas, Estoque, Financeiro, Fiscal, Relatórios e BI).

## 3. Interface (UI - HTML/CSS)
- Usar um elemento conteiner (como uma `div`) com CSS `overflow-y: auto` para simular o histórico de mensagens rolável.
- Adicionar um spinner ou indicador de carregamento (ex: do Bootstrap ou CSS puro) que fica oculto por padrão e só é exibido via JavaScript enquanto a requisição `fetch` aguarda a resposta.

---

## Exemplo de Implementação (Django + Fetch API)

Abaixo está o modelo de implementação utilizando a arquitetura atual do **MEI Gestão**:

### 1. Backend: `core/views.py`
Crie uma view para receber a mensagem via AJAX e consultar o Ollama.

```python
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Configurações da API Local do Ollama
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3" # ou o modelo que estiver configurado no seu Ollama

# System Prompt rigoroso para o MEI Gestão
SYSTEM_PROMPT = """Você é o Suporte Oficial do SISTEMA MEI Gestão.
Sua função é ajudar os usuários exclusivamente com dúvidas sobre o software (Vendas, Estoque, Financeiro, Fiscal, Relatórios e BI).
Seja educado, direto e não responda a perguntas fora desse escopo."""

@csrf_exempt # Apenas para o exemplo, idealmente valide o CSRF token no JS
def chat_suporte_ia(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("mensagem", "")
            
            if not user_message:
                return JsonResponse({"erro": "Mensagem vazia."}, status=400)
                
            full_prompt = f"{SYSTEM_PROMPT}\n\nUsuário: {user_message}\nSuporte MEI Gestão:"
            
            payload = {
                "model": MODEL_NAME,
                "prompt": full_prompt,
                "stream": False
            }
            
            # Chamada ao modelo local
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
            
            if response.status_code == 200:
                resposta_ia = response.json().get("response", "Erro no processamento.")
                return JsonResponse({"resposta": resposta_ia})
            else:
                return JsonResponse({"erro": "Falha no servidor de IA local."}, status=502)
                
        except Exception as e:
            return JsonResponse({"erro": str(e)}, status=500)
            
    return JsonResponse({"erro": "Método não permitido."}, status=405)
```

### 2. Rotas: `core/urls.py`
Registre a URL da view criada.

```python
from django.urls import path
from . import views

urlpatterns = [
    # ... suas outras urls
    path('api/suporte-ia/', views.chat_suporte_ia, name='chat_suporte_ia'),
]
```

### 3. Frontend: `templates/suporte_ia.html`
A interface do usuário utilizando HTML e JavaScript (Fetch) para manter a fluidez.

```html
<div class="chat-container">
    <div id="chatHistory" style="height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 15px; margin-bottom: 10px; background-color: #f8f9fa;">
        <!-- Mensagens aparecerão aqui -->
    </div>
    
    <div class="input-group">
        <input type="text" id="userInput" class="form-control" placeholder="Digite sua dúvida sobre o sistema...">
        <button id="sendBtn" class="btn btn-primary" onclick="enviarMensagem()">Enviar</button>
    </div>
    
    <!-- Spinner de Loading -->
    <div id="loadingIndicator" style="display: none; margin-top: 10px;">
        <span class="spinner-border spinner-border-sm text-primary" role="status"></span>
        <span class="text-muted ms-2">A IA está processando...</span>
    </div>
</div>

<script>
async function enviarMensagem() {
    const inputEl = document.getElementById('userInput');
    const chatHistory = document.getElementById('chatHistory');
    const loadingEl = document.getElementById('loadingIndicator');
    const msg = inputEl.value.trim();
    
    if (!msg) return;
    
    // Adiciona a mensagem do usuário na tela
    chatHistory.innerHTML += `<div style="margin-bottom: 10px;"><b>Você:</b> ${msg}</div>`;
    inputEl.value = ''; // limpa o input
    
    // Mostra o loading
    loadingEl.style.display = 'block';
    chatHistory.scrollTop = chatHistory.scrollHeight; // Rola pra baixo
    
    try {
        const resposta = await fetch('/api/suporte-ia/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // 'X-CSRFToken': getCookie('csrftoken') // Adicione para segurança no Django
            },
            body: JSON.stringify({ mensagem: msg })
        });
        
        const data = await resposta.json();
        
        // Adiciona a resposta da IA na tela
        if (resposta.ok) {
            chatHistory.innerHTML += `<div style="margin-bottom: 10px; color: #0056b3;"><b>Suporte MEI Gestão:</b> ${data.resposta}</div>`;
        } else {
            chatHistory.innerHTML += `<div style="margin-bottom: 10px; color: red;"><b>Erro:</b> ${data.erro}</div>`;
        }
        
    } catch (error) {
        chatHistory.innerHTML += `<div style="margin-bottom: 10px; color: red;"><b>Erro de conexão.</b></div>`;
    } finally {
        // Esconde o loading independente de sucesso ou erro
        loadingEl.style.display = 'none';
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
}

// Permitir envio com tecla Enter
document.getElementById('userInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') enviarMensagem();
});
</script>
```

### Por que esta abordagem é a ideal para o MEI Gestão?
1. **Sem bloqueio de interface:** O uso do `fetch` assíncrono no JavaScript resolve a exigência de não travar a UI (mesmo conceito que usaríamos no Flet, mas adaptado para a Web padrão do Django).
2. **Segurança do Prompt:** Ao invés do Frontend conversar direto com o Ollama, ele conversa com a *view* do Django. Isso esconde o `SYSTEM_PROMPT` no backend e protege a arquitetura.
3. **Feedback visual:** O uso do JavaScript permite manipular o DOM (`display: none` para `block`) exibindo o spinner de carregamento no exato instante em que a requisição é disparada para o Django.

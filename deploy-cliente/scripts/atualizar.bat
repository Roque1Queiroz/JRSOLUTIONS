@echo off
chcp 65001 >nul
REM ============================================================
REM  SISTEMA GESTOR — Atualizacao on-premise (Windows)
REM
REM  O QUE FAZ (3 passos, do mais cuidadoso para o mais rapido):
REM    1. Backup do banco PostgreSQL (dados do cliente)
REM    2. Substitui o codigo (app/) pela nova versao, mantendo .env e volumes
REM    3. Reconstrói as imagens Docker e aplica as migrations
REM
REM  COMO USAR:
REM    1. Coloque a pasta 'app/' NOVA (vinda do sistema-gestor-cliente-v2.X.zip)
REM       junto deste .bat, na MESMA pasta onde estao docker-compose.yml e .env
REM    2. Duplo clique em atualizar.bat
REM    3. Aguarde o sistema subir e responder em http://localhost:8000
REM
REM  O QUE NAO MUCA:
REM    - .env (chaves, senhas, GROQ_API_KEY)
REM    - Volumes Docker (db_data, media, staticfiles)
REM    - Empresas, usuarios, cadastros, ordens de servico
REM
REM  Requisitos: Docker com plugin "docker compose".
REM ============================================================
echo ==========================================
echo  SISTEMA GESTOR - Atualizacao
echo ==========================================
echo.

REM --- Pre-requisito: docker compose ---
docker compose version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Docker / docker compose nao encontrado.
    echo         Instale o Docker Desktop: https://docs.docker.com/desktop/install/windows/
    pause
    exit /b 1
)

REM --- Pre-requisito: pasta app/ nova presente ---
if not exist app\manage.py (
    echo [ERRO] Nao encontrei a pasta app\ com o codigo novo.
    echo         Coloque a pasta app\ desta versao junto deste .bat
    echo         (extraia do sistema-gestor-cliente-vX.zip).
    pause
    exit /b 1
)

REM --- 1. Backup do banco (PostgreSQL) ---
echo [1/4] Fazendo backup do banco...
for /f "tokens=1-4 delims=/- " %%a in ("%date%") do set D=%%c%%b%%a
set BAK=backup_%D%.sql
docker compose exec -T db pg_dump -U gestor gestor > %BAK% 2>nul
if errorlevel 1 (
    echo        AVISO: backup nao foi possivel. Continuando mesmo assim...
) else (
    echo        Backup salvo em: %BAK%
)
echo.

REM --- 2. Backup do .env (defesa) ---
echo [2/4] Protegendo o .env...
if exist .env (
    copy /Y .env .env.bak >nul
    echo        Cópia de seguranca em .env.bak
) else (
    echo        AVISO: .env nao encontrado. Rode scripts\instalar.sh primeiro.
    pause
    exit /b 1
)
echo.

REM --- 3. Reconstruir e subir com a nova versao ---
echo [3/4] Atualizando o sistema (pode demorar alguns minutos)...
docker compose up -d --build
echo.

REM --- 4. Aplicar migrations ---
echo [4/4] Aplicando atualizacoes do banco...
docker compose exec web python manage.py migrate --noinput
echo.

echo ==========================================
echo  PRONTO! Acesse: http://localhost:8000
echo ==========================================
echo.
echo  Se algo deu errado, o backup do banco esta em: %BAK%
echo  Para reverter:  copie o app\ antigo de volta e rode este script de novo.
echo.
pause
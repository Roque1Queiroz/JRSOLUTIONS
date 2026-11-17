@echo off
setlocal enabledelayedexpansion
title Sistema Gestor - Baixar pacote on-premise
echo.
echo ============================================================
echo   SISTEMA GESTOR - Baixar pacote do cliente (para o HD)
echo ============================================================
echo.

REM ============ CONFIGURACAO (altere so se mudar o acesso) ============
REM Usuario@IP desta maquina (onde o Hermes roda)
set "HOST=hermes@10.0.0.28"

REM Versao do pacote que quer baixar
set "VERSAO=v1.0"

REM Onde salvar no seu Windows
set "BASE=%USERPROFILE%\Downloads"
set "DEST=%BASE%\SistemaGestor_pacote_%VERSAO%"
REM ====================================================================

scp -V >nul 2>&1
if errorlevel 1 (
  echo [ERRO] Comando scp nao encontrado.
  echo O scp ja vem com o Windows 10/11. Abra o "Prompt de Comando" como administrador.
  goto :fim
)

echo Verificando conexao com %HOST% ...
ping -n 1 10.0.0.28 >nul 2>&1
if errorlevel 1 (
  echo [AVISO] Nao respondeu ao ping, mas continuando (as vezes o ping e bloqueado)...
)

if not exist "%DEST%" mkdir "%DEST%"

echo.
echo  Baixando arquivos para: %DEST%
echo  (se pedir senha, digite a do usuario %HOST% e Enter)
echo.

set "REMOTA=/opt/data/workspace/auditoria-sistema-gestor/projeto-correcao/deploy-cliente"

scp "%HOST%:%REMOTA%/dist/sistema-gestor-cliente-%VERSAO%.zip" "%DEST%"
if not exist "%DEST%\sistema-gestor-cliente-%VERSAO%.zip" (
  echo [AVISO] Zip nao chegou. Verifique a versao (%VERSAO%) e a conexao.
) else (
  echo [OK] Zip baixado.
)

scp "%HOST%:%REMOTA%/GUIA_INSTALACAO_CLIENTE.md" "%DEST%"
scp "%HOST%:%REMOTA%/README_INSTALACAO.md"        "%DEST%"

echo.
echo ============================================================
echo   PRONTO! Arquivos salvos em:
echo     %DEST%
echo   Agora plugue o HD externo e copie a pasta inteira para la.
echo ============================================================
if exist "%DEST%\sistema-gestor-cliente-%VERSAO%.zip" (
  echo  Conteudo:
  dir /b "%DEST%"
) else (
  echo  Nada foi copiado - confira a mensagem de erro acima.
)
echo.

:fim
echo.
pause

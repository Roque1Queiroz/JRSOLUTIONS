#!/bin/bash

# =========================================================================
# SCRIPT DE BACKUP AUTOMATICO - SISTEMA GESTOR (AMBIENTE NUVEM / PRODUCAO)
# =========================================================================
# Este script deve ser agendado via Cron no servidor Linux.
# Exemplo de Crontab para rodar todo dia as 03:00 da manha:
# 0 3 * * * /caminho/do/projeto/scripts/backup_banco.sh >> /var/log/backup_gestor.log 2>&1

# Definir o diretorio raiz do projeto (ajuste conforme o servidor em nuvem)
PROJETO_DIR="/var/www/mei_gestao"
BACKUP_DIR="${PROJETO_DIR}/backups"
DATA_ATUAL=$(date +"%Y-%m-%d_%H-%M-%S")

# 1. Cria a pasta de backups se ela nao existir
mkdir -p "$BACKUP_DIR"

# 2. Fazendo o Backup
# Se o banco em producao for SQLite (padrao atual):
ARQUIVO_BANCO="${PROJETO_DIR}/db.sqlite3"
ARQUIVO_BACKUP="${BACKUP_DIR}/backup_sqlite_${DATA_ATUAL}.sqlite3.gz"

if [ -f "$ARQUIVO_BANCO" ]; then
    echo "[$(date)] Iniciando backup do banco SQLite..."
    # Cria uma copia compactada para economizar espaco no servidor
    gzip -c "$ARQUIVO_BANCO" > "$ARQUIVO_BACKUP"
    echo "[$(date)] Backup concluido: $ARQUIVO_BACKUP"
else
    echo "[$(date)] ERRO: Arquivo do banco de dados (db.sqlite3) nao encontrado!"
fi

# NOTA PARA O FUTURO (POSTGRESQL):
# Se o banco for migrado para PostgreSQL na nuvem, comente o bloco acima e descomente abaixo:
# echo "[$(date)] Iniciando backup PostgreSQL..."
# pg_dump -U usuario_banco -h localhost nome_do_banco | gzip > "${BACKUP_DIR}/backup_pg_${DATA_ATUAL}.sql.gz"

# 3. Limpeza automatica (Retencao)
# Apaga arquivos de backup mais velhos que 15 dias para nao lotar o disco do servidor na nuvem.
echo "[$(date)] Limpando backups antigos (mais de 15 dias)..."
find "$BACKUP_DIR" -type f -name "backup_*.gz" -mtime +15 -exec rm {} \;

echo "[$(date)] Rotina de backup finalizada com sucesso!"

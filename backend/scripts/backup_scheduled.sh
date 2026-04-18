#!/bin/bash
# Script para backup agendado (cron)
# Adicionar ao crontab: 0 2 * * * /caminho/para/backup_scheduled.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Ativar ambiente virtual se existir
if [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# Executar backup
python scripts/backup_manual.py

# Opcional: Enviar backup para local remoto (exemplo)
# scp backups/plans_backup_*.db user@backup-server:/backups/


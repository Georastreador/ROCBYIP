#!/usr/bin/env python3
"""
Script manual para restaurar backup do banco de dados
Uso: python restore_backup.py <nome_do_backup.db|.dump>
"""
import sys
import os

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.backup import restore_backup, list_backups
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Uso: python restore_backup.py <nome_do_backup.db ou .dump>")
        print("\n📋 Backups disponíveis:")
        backups = list_backups()
        if backups:
            for i, backup in enumerate(backups[:10], 1):  # Mostrar apenas 10 mais recentes
                print(f"   {i}. {backup['filename']} ({backup['age_days']} dias atrás)")
        else:
            print("   Nenhum backup encontrado")
        sys.exit(1)
    
    backup_filename = sys.argv[1]
    
    print(f"🔄 Restaurando backup: {backup_filename}")
    print("⚠️  ATENÇÃO: Esta operação irá substituir o banco de dados atual!")
    
    confirm = input("Deseja continuar? (sim/não): ")
    if confirm.lower() not in ['sim', 's', 'yes', 'y']:
        print("❌ Operação cancelada")
        sys.exit(0)
    
    try:
        from app.services.backup import BACKUP_DIR
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        success = restore_backup(backup_path)
        
        if success:
            print(f"✅ Backup restaurado com sucesso!")
        else:
            print(f"❌ Falha ao restaurar backup")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Erro ao restaurar backup: {str(e)}")
        sys.exit(1)


#!/usr/bin/env python3
"""
Script manual para criar backup do banco de dados
Uso: python backup_manual.py
"""
import sys
import os

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.backup import create_backup, cleanup_old_backups, get_backup_stats
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    print("🔄 Criando backup do banco de dados...")
    
    try:
        backup_path = create_backup()
        print(f"✅ Backup criado com sucesso: {backup_path}")
        
        # Limpar backups antigos
        removed = cleanup_old_backups()
        if removed > 0:
            print(f"🗑️  {removed} backup(s) antigo(s) removido(s)")
        
        # Mostrar estatísticas
        stats = get_backup_stats()
        print(f"\n📊 Estatísticas de Backup:")
        print(f"   Total de backups: {stats['total_backups']}")
        print(f"   Tamanho total: {stats['total_size_mb']} MB")
        if stats['newest_backup']:
            print(f"   Backup mais recente: {stats['newest_backup']}")
        
    except Exception as e:
        print(f"❌ Erro ao criar backup: {str(e)}")
        sys.exit(1)


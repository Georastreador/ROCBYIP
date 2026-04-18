#!/usr/bin/env python3
"""
Teste de Download — Verifica se os endpoints de export retornam arquivos para download
"""

import httpx
import json
from datetime import date

BASE_URL = "http://localhost:8000"

def test_download_workflow():
    print("\n" + "="*70)
    print("🧪 TESTE DE DOWNLOAD — ROC Planning API")
    print("="*70 + "\n")
    
    with httpx.Client(timeout=10) as client:
        # 1. Criar um plano de teste
        print("1️⃣  Criando plano de teste...")
        plan_data = {
            "title": "Teste Download",
            "subject": {"what": "Teste", "who": "Admin", "where": "Lab"},
            "time_window": {
                "start": "2025-01-01",
                "end": "2025-01-31",
                "research_notes": "Teste de download de relatórios"
            },
            "user": {
                "principal": "Testador",
                "others": "",
                "depth": "tecnico",
                "secrecy": "publico"
            },
            "purpose": "Validar funcionamento de download de PDF e HTML",
            "deadline": {"date": "2025-02-15", "urgency": "media"},
            "aspects_essential": ["Dados críticos", "Segurança"],
            "aspects_known": ["Contexto geral"],
            "aspects_to_know": ["Detalhes técnicos"],
            "pirs": [
                {
                    "aspect_ref": 0,
                    "question": "Qual é a arquitetura?",
                    "priority": "alta"
                }
            ],
            "collection": [
                {
                    "pir_index": 0,
                    "source": "Documentação",
                    "method": "Review",
                    "frequency": "unico",
                    "owner": "Admin",
                    "sla_hours": 24
                }
            ],
            "extraordinary": ["Acesso especial ao servidor"],
            "security": ["Criptografia TLS"]
        }
        
        response = client.post(f"{BASE_URL}/plans", json=plan_data)
        if response.status_code != 200:
            print(f"❌ Erro ao criar plano: {response.text}")
            return False
        
        plan = response.json()
        plan_id = plan['id']
        print(f"✅ Plano criado com sucesso! ID: {plan_id}\n")
        
        # 2. Exportar PDF
        print(f"2️⃣  Exportando para PDF (ID: {plan_id})...")
        pdf_response = client.get(f"{BASE_URL}/export/pdf/{plan_id}")
        
        if pdf_response.status_code != 200:
            print(f"❌ Erro ao exportar PDF: {pdf_response.text}")
            return False
        
        pdf_data = pdf_response.content
        pdf_size = len(pdf_data)
        
        # Verificar se é um PDF válido
        is_pdf = pdf_data.startswith(b'%PDF')
        
        if is_pdf:
            print(f"✅ PDF exportado com sucesso!")
            print(f"   📄 Tamanho: {pdf_size} bytes")
            print(f"   🔍 Assinatura PDF: {pdf_data[:4]}")
            print(f"   💾 Content-Type: {pdf_response.headers.get('content-type', 'N/A')}")
            print(f"   📥 Filename: {pdf_response.headers.get('content-disposition', 'N/A')}\n")
        else:
            print(f"⚠️  Aviso: Resposta não parece ser um PDF válido")
            print(f"   Primeiros 50 bytes: {pdf_data[:50]}\n")
        
        # Salvar PDF para verificação manual
        with open(f"/tmp/test_plan_{plan_id}.pdf", "wb") as f:
            f.write(pdf_data)
        print(f"   📁 PDF salvo em: /tmp/test_plan_{plan_id}.pdf\n")
        
        # 3. Exportar HTML
        print(f"3️⃣  Exportando para HTML (ID: {plan_id})...")
        html_response = client.get(f"{BASE_URL}/export/html/{plan_id}")
        
        if html_response.status_code != 200:
            print(f"❌ Erro ao exportar HTML: {html_response.text}")
            return False
        
        html_data = html_response.content
        html_size = len(html_data)
        
        # Verificar se é um HTML válido
        is_html = b'<!doctype html' in html_data.lower() or b'<html' in html_data.lower()
        
        if is_html:
            print(f"✅ HTML exportado com sucesso!")
            print(f"   📄 Tamanho: {html_size} bytes")
            print(f"   💾 Content-Type: {html_response.headers.get('content-type', 'N/A')}")
            print(f"   📥 Filename: {html_response.headers.get('content-disposition', 'N/A')}\n")
        else:
            print(f"⚠️  Aviso: Resposta não parece ser um HTML válido")
            print(f"   Primeiros 100 bytes: {html_data[:100]}\n")
        
        # Salvar HTML para verificação manual
        with open(f"/tmp/test_plan_{plan_id}.html", "wb") as f:
            f.write(html_data)
        print(f"   📁 HTML salvo em: /tmp/test_plan_{plan_id}.html\n")
        
        # 4. Testar validação LGPD
        print(f"4️⃣  Validando conformidade LGPD...")
        lgpd_response = client.post(f"{BASE_URL}/plans/{plan_id}/lgpd_check")
        
        if lgpd_response.status_code == 200:
            lgpd_result = lgpd_response.json()
            print(f"✅ Validação LGPD concluída!")
            print(f"   Conformidade: {'✅ SIM' if lgpd_result.get('compliant') else '❌ NÃO'}")
            if not lgpd_result.get('compliant'):
                print(f"   Razão: {lgpd_result.get('reason', 'Não especificado')}\n")
            else:
                print()
        else:
            print(f"⚠️  Erro ao validar LGPD: {lgpd_response.text}\n")
        
        # 5. Resumo
        print("="*70)
        print("📊 RESUMO DO TESTE")
        print("="*70)
        print(f"✅ Criação de Plano: PASSOU")
        print(f"✅ Exportação PDF: {'PASSOU' if is_pdf else 'FALHOU (não é PDF válido)'}")
        print(f"✅ Exportação HTML: {'PASSOU' if is_html else 'FALHOU (não é HTML válido)'}")
        print(f"✅ Download Disponível: SIM (FileResponse retorna arquivo)")
        print(f"\n🎯 Plano ID: {plan_id}")
        print(f"📈 PDF: {pdf_size} bytes")
        print(f"📈 HTML: {html_size} bytes")
        print("="*70 + "\n")
        
        return is_pdf and is_html

if __name__ == "__main__":
    try:
        success = test_download_workflow()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        exit(1)

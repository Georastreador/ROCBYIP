from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.platypus import Table, TableStyle
from datetime import datetime
import json

def _kv_block(c, x, y, title, body, w, h):
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, title)
    y -= 16
    c.setFont("Helvetica", 10)
    for line in body.split("\n"):
        c.drawString(x, y, line[:120])
        y -= 14
        if y < 3*cm:
            c.showPage()
            y = h - 2*cm
            c.setFont("Helvetica", 10)
    return y - 8

def generate_plan_pdf(plan: dict, outfile: str):
    c = canvas.Canvas(outfile, pagesize=A4)
    w, h = A4
    x, y = 2*cm, h - 2*cm

    # Parse JSON strings in plan data
    if isinstance(plan.get("subject"), str):
        plan["subject"] = json.loads(plan["subject"]) if plan["subject"] else {}
    if isinstance(plan.get("time_window"), str):
        plan["time_window"] = json.loads(plan["time_window"]) if plan["time_window"] else {}
    if isinstance(plan.get("user"), str):
        plan["user"] = json.loads(plan["user"]) if plan["user"] else {}
    if isinstance(plan.get("deadline"), str):
        plan["deadline"] = json.loads(plan["deadline"]) if plan["deadline"] else {}
    if isinstance(plan.get("aspects_essential"), str):
        plan["aspects_essential"] = json.loads(plan["aspects_essential"]) if plan["aspects_essential"] else []
    if isinstance(plan.get("aspects_known"), str):
        plan["aspects_known"] = json.loads(plan["aspects_known"]) if plan["aspects_known"] else []
    if isinstance(plan.get("aspects_to_know"), str):
        plan["aspects_to_know"] = json.loads(plan["aspects_to_know"]) if plan["aspects_to_know"] else []
    if isinstance(plan.get("pirs"), str):
        plan["pirs"] = json.loads(plan["pirs"]) if plan["pirs"] else []
    if isinstance(plan.get("collection"), str):
        plan["collection"] = json.loads(plan["collection"]) if plan["collection"] else []
    if isinstance(plan.get("extraordinary"), str):
        plan["extraordinary"] = json.loads(plan["extraordinary"]) if plan["extraordinary"] else []
    if isinstance(plan.get("security"), str):
        plan["security"] = json.loads(plan["security"]) if plan["security"] else []

    c.setFillColor(colors.HexColor("#0F172A"))
    c.rect(0, h-60, w, 60, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, h-40, "Plano de Inteligência — 1ª Fase (Planejamento)")
    c.setFont("Helvetica", 9)
    c.drawRightString(w-2*cm, h-30, datetime.utcnow().isoformat()+"Z")
    c.setFillColor(colors.black)

    y = h - 80
    y = _kv_block(c, x, y, "Título", plan.get("title",""), w, h)
    
    # Format Assunto nicely
    subject = plan.get("subject", {})
    subject_text = f"O quê: {subject.get('what','')}\nQuem: {subject.get('who','')}\nOnde: {subject.get('where','')}"
    y = _kv_block(c, x, y, "Assunto", subject_text, w, h)
    
    # Format Faixa de Tempo nicely
    time_window = plan.get("time_window", {})
    time_text = f"Início: {time_window.get('start','')}\nFim: {time_window.get('end','')}\nNotas: {time_window.get('research_notes','') or '(nenhuma anotação)'}"
    y = _kv_block(c, x, y, "Faixa de Tempo (Pesquisa)", time_text, w, h)
    
    # Format Usuário nicely
    user = plan.get("user", {})
    user_text = f"Principal: {user.get('principal','')}\nOutros: {user.get('others','') or '(nenhum)'}\nProfundidade: {user.get('depth','')}\nSigilo: {user.get('secrecy','')}"
    y = _kv_block(c, x, y, "Usuário", user_text, w, h)
    
    y = _kv_block(c, x, y, "Finalidade", plan.get("purpose",""), w, h)
    
    # Format Prazo nicely
    deadline = plan.get("deadline", {})
    deadline_text = f"Data Limite: {deadline.get('date','')}\nUrgência: {deadline.get('urgency','')}"
    y = _kv_block(c, x, y, "Prazo", deadline_text, w, h)

    def list_to_text(lst):
        return "\n".join([f"• {i}" for i in lst]) if lst else "-"

    sections = [
        ("Aspectos Essenciais", list_to_text(plan.get("aspects_essential",[]))),
        ("Aspectos Conhecidos", list_to_text(plan.get("aspects_known",[]))),
        ("Aspectos a Conhecer", list_to_text(plan.get("aspects_to_know",[]))),
        ("Medidas Extraordinárias", list_to_text(plan.get("extraordinary",[]))),
        ("Medidas de Segurança", list_to_text(plan.get("security",[]))),
    ]
    for title, body in sections:
        y = _kv_block(c, x, y, title, body, w, h)
        if y < 3*cm:
            c.showPage(); y = h - 2*cm

    pirs = plan.get("pirs", [])
    if pirs:
        c.showPage()
        y = h - 2*cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, y, "PIRs (Requisitos de Inteligência)")
        y -= 20
        data = [["#", "Aspecto Ref", "Pergunta", "Prioridade"]]
        for i, p in enumerate(pirs):
            data.append([str(i), str(p.get("aspect_ref","-")), p.get("question",""), p.get("priority","")])
        table = Table(data, colWidths=[1.2*cm, 3*cm, 10*cm, 3*cm])
        table.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0), colors.HexColor("#E2E8F0")),
            ("GRID",(0,0),(-1,-1), 0.5, colors.grey),
            ("FONT",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONT",(0,1),(-1,-1),"Helvetica"),
        ]))
        table.wrapOn(c, w, h)
        table_height = 18 * (len(data))
        table.drawOn(c, x, y - table_height)

    col = plan.get("collection", [])
    if col:
        c.showPage()
        y = h - 2*cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x, y, "Plano de Coleta")
        y -= 20
        data = [["PIR #","Fonte","Método","Freq.","Owner","SLA (h)"]]
        for t in col:
            data.append([str(t.get("pir_index","")), t.get("source",""), t.get("method",""), t.get("frequency",""), t.get("owner",""), str(t.get("sla_hours",0))])
        table = Table(data, colWidths=[2*cm, 4*cm, 5*cm, 2*cm, 3*cm, 2*cm])
        table.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0), colors.HexColor("#E2E8F0")),
            ("GRID",(0,0),(-1,-1), 0.5, colors.grey),
            ("FONT",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONT",(0,1),(-1,-1),"Helvetica"),
        ]))
        table.wrapOn(c, w, h)
        table_height = 18 * (len(data))
        table.drawOn(c, x, y - table_height)

    c.showPage()
    c.save()

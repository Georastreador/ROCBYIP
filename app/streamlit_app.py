import streamlit as st
import httpx
from datetime import date, datetime, timedelta, timezone
import pandas as pd
from PIL import Image

# Use environment variable or default to localhost:8000
import os
from pathlib import Path

from i18n import t
from kinde_streamlit import check_auth

# Constantes de validação
MAX_TITLE_LENGTH = 200
MAX_TEXT_LENGTH = 5000
MAX_PIR_QUESTION_LENGTH = 500
MAX_ITEM_LENGTH = 1000
MAX_RESEARCH_NOTES_LENGTH = 2000

API_URL = os.getenv("API_URL", "http://localhost:8000")


def _api_headers():
    """Cabeçalhos para API: API Key (opcional) + JWT (opcional) para modos api_key / jwt / api_key_or_jwt."""
    h = {}
    ak = os.getenv("API_KEY", "").strip()
    if ak:
        h["X-API-Key"] = ak
    tok = st.session_state.get("jwt_token")
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent
# Assets podem estar em app/attached_assets ou docs/attached_assets
ASSETS_DIR_APP = SCRIPT_DIR / "attached_assets"
ASSETS_DIR_DOCS = SCRIPT_DIR.parent / "docs" / "attached_assets"

# Usar o diretório que existir (priorizar docs/attached_assets)
# Verificar múltiplos caminhos possíveis para garantir que encontre
possible_paths = [
    ASSETS_DIR_DOCS,  # Caminho preferido
    ASSETS_DIR_APP,   # Alternativo
    Path(__file__).parent.parent / "docs" / "attached_assets",  # Absoluto alternativo
]

ASSETS_DIR = None
for path in possible_paths:
    if path.exists():
        ASSETS_DIR = path
        break

# Se nenhum existir, usar o preferido
if ASSETS_DIR is None:
    ASSETS_DIR = ASSETS_DIR_DOCS

# Configurar favicon - Streamlit procura automaticamente favicon.ico ou favicon.png
# no diretório onde o script está rodando (app/) ou em .streamlit/
# Os arquivos favicon.png e favicon.ico já foram criados com texto "ROC BYIP"
# Tentar usar o favicon como arquivo de imagem
try:
    favicon_img = Image.open(SCRIPT_DIR / "favicon.png")
    st.set_page_config(
        page_title="ROC BYIP",
        page_icon=favicon_img,  # Usar imagem diretamente
        layout="wide"
    )
except:
    st.set_page_config(
        page_title="ROC BYIP - Planejamento de Inteligência",
        page_icon="👑",  # Emoji como fallback - favicon.ico será detectado automaticamente
        layout="wide"
    )

# ── Autenticação Kinde (deve vir antes de qualquer conteúdo da app) ───────────
if not check_auth():
    st.stop()

if "lang" not in st.session_state:
    st.session_state.lang = "pt"

if "jwt_token" not in st.session_state:
    st.session_state.jwt_token = None

if "plan" not in st.session_state:
    st.session_state.plan = {
        "title": "",
        "subject": {"what":"", "who":"", "where":""},
        "time_window": {"start":"", "end":""},
        "user": {"principal":"", "others":"", "depth":"executivo", "secrecy":"publico"},
        "purpose": "",
        "deadline": {"date":"", "urgency":"media"},
        "aspects_essential": [],
        "aspects_known": [],
        "aspects_to_know": [],
        "pirs": [],
        "collection": [],
        "extraordinary": [],
        "security": []
    }

st.title(t("app_title"))

steps = [
    t("step_assunto"), t("step_faixa_tempo"), t("step_usuario"), t("step_finalidade"), t("step_prazo"),
    t("step_aspectos_essenciais"), t("step_aspectos_conhecidos"), t("step_aspectos_conhecer"),
    t("step_pirs_coleta"), t("step_medidas_extraordinarias"), t("step_medidas_seguranca"),
    t("step_preview"), t("step_revisao_export"), t("step_imagens")
]

with st.sidebar:
    lang_opt = st.selectbox(
        t("lang_label"),
        options=["pt", "en"],
        format_func=lambda x: "Português" if x == "pt" else "English",
        index=0 if st.session_state.get("lang", "pt") == "pt" else 1,
        key="lang_selector"
    )
    if lang_opt != st.session_state.get("lang", "pt"):
        st.session_state.lang = lang_opt
        st.rerun()

    with st.expander(t("auth_expand"), expanded=False):
        st.caption(t("auth_hint"))
        with st.form("jwt_login"):
            le = st.text_input(t("auth_email"), key="login_email")
            lp = st.text_input(t("auth_password"), type="password", key="login_pw")
            sub = st.form_submit_button(t("auth_login_btn"))
            if sub:
                try:
                    r = httpx.post(
                        f"{API_URL}/auth/token",
                        data={"username": le, "password": lp},
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                        timeout=20,
                    )
                    if r.status_code == 200:
                        st.session_state.jwt_token = r.json().get("access_token")
                        st.success(t("auth_ok"))
                        st.rerun()
                    else:
                        st.error(t("auth_fail", text=r.text))
                except Exception as ex:
                    st.error(str(ex))
        if st.session_state.jwt_token and st.button(t("auth_logout"), key="logout_jwt"):
            st.session_state.jwt_token = None
            st.rerun()

    st.markdown("---")
    st.header(t("sidebar_steps"))
    current = st.radio(t("sidebar_navigation"), steps, index=0)
    
    st.markdown("---")

    @st.dialog(t("manual_title"), width="large")
    def show_manual():
        manual_path = SCRIPT_DIR.parent / "docs" / "MANUAL_DE_OPERACAO.md"
        if manual_path.exists():
            with open(manual_path, encoding="utf-8") as f:
                st.markdown(f.read())
        else:
            st.warning("Manual não encontrado. Consulte docs/MANUAL_DE_OPERACAO.md")

    if st.button(t("manual_btn"), use_container_width=True, key="btn_manual_sidebar"):
        show_manual()

    st.markdown("---")
    st.subheader(t("sidebar_time_window"))
    
    # Initialize research_notes if not exists
    if "plan" in st.session_state and "time_window" in st.session_state.plan:
        if "research_notes" not in st.session_state.plan["time_window"]:
            st.session_state.plan["time_window"]["research_notes"] = ""
    
    # Sidebar notes input
    research_notes = st.text_area(
        t("sidebar_research_notes"),
        value=st.session_state.plan["time_window"].get("research_notes", ""),
        height=120,
        placeholder=t("sidebar_research_placeholder"),
        max_chars=MAX_RESEARCH_NOTES_LENGTH
    )
    st.session_state.plan["time_window"]["research_notes"] = research_notes

plan = st.session_state.plan

def sanitize_string(value, max_length=None):
    """Sanitiza string removendo caracteres de controle"""
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    
    # Converter para string e remover caracteres de controle
    text = str(value)
    # Remover caracteres de controle (exceto \n, \r, \t)
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Limitar tamanho se especificado
    if max_length:
        text = text[:max_length]
    
    return text.strip()

def sanitize_plan_data(plan):
    """Sanitiza todos os dados do plano antes de enviar para API"""
    sanitized = {}
    
    # Sanitizar campos de texto
    sanitized["title"] = sanitize_string(plan.get("title"), MAX_TITLE_LENGTH)
    sanitized["purpose"] = sanitize_string(plan.get("purpose"), MAX_TEXT_LENGTH)
    
    # Sanitizar subject
    sanitized["subject"] = {
        "what": sanitize_string(plan.get("subject", {}).get("what"), MAX_ITEM_LENGTH),
        "who": sanitize_string(plan.get("subject", {}).get("who"), MAX_ITEM_LENGTH),
        "where": sanitize_string(plan.get("subject", {}).get("where"), MAX_ITEM_LENGTH)
    }
    
    # Sanitizar time_window (incluindo research_notes)
    time_window = plan.get("time_window", {})
    sanitized["time_window"] = {
        "start": time_window.get("start", ""),
        "end": time_window.get("end", ""),
        "research_notes": sanitize_string(time_window.get("research_notes"), MAX_RESEARCH_NOTES_LENGTH)
    }
    
    # Sanitizar user
    user = plan.get("user", {})
    sanitized["user"] = {
        "principal": sanitize_string(user.get("principal"), MAX_ITEM_LENGTH),
        "others": sanitize_string(user.get("others"), MAX_ITEM_LENGTH),
        "depth": user.get("depth", "executivo"),
        "secrecy": user.get("secrecy", "publico")
    }
    
    # Sanitizar deadline
    sanitized["deadline"] = plan.get("deadline", {})
    
    # Sanitizar arrays de strings
    sanitized["aspects_essential"] = [
        sanitize_string(item, MAX_ITEM_LENGTH) for item in plan.get("aspects_essential", [])
    ]
    sanitized["aspects_known"] = [
        sanitize_string(item, MAX_ITEM_LENGTH) for item in plan.get("aspects_known", [])
    ]
    sanitized["aspects_to_know"] = [
        sanitize_string(item, MAX_ITEM_LENGTH) for item in plan.get("aspects_to_know", [])
    ]
    
    # Sanitizar PIRs
    sanitized["pirs"] = []
    for pir in plan.get("pirs", []):
        sanitized_pir = {
            "aspect_ref": pir.get("aspect_ref"),
            "question": sanitize_string(pir.get("question"), MAX_PIR_QUESTION_LENGTH),
            "priority": pir.get("priority", "media"),
            "justification": sanitize_string(pir.get("justification"), MAX_ITEM_LENGTH)
        }
        sanitized["pirs"].append(sanitized_pir)
    
    # Sanitizar collection
    sanitized["collection"] = []
    for coll in plan.get("collection", []):
        sanitized_coll = {
            "pir_index": coll.get("pir_index"),
            "source": sanitize_string(coll.get("source"), MAX_ITEM_LENGTH),
            "method": sanitize_string(coll.get("method"), MAX_ITEM_LENGTH),
            "frequency": coll.get("frequency", "unico"),
            "owner": sanitize_string(coll.get("owner"), MAX_ITEM_LENGTH),
            "sla_hours": coll.get("sla_hours", 0)
        }
        sanitized["collection"].append(sanitized_coll)
    
    # Sanitizar arrays de medidas
    sanitized["extraordinary"] = [
        sanitize_string(item, MAX_ITEM_LENGTH) for item in plan.get("extraordinary", [])
    ]
    sanitized["security"] = [
        sanitize_string(item, MAX_ITEM_LENGTH) for item in plan.get("security", [])
    ]
    
    return sanitized

def save_list(label, key):
    items = plan.get(key, [])
    v = st.text_input(t("list_add_item", label=label), key=f"add_{key}", max_chars=MAX_ITEM_LENGTH)
    if st.button(t("list_include", label=label)):
        vv = (v or "").strip()
        if vv:
            items.append(vv)
            plan[key] = items
            st.success(t("list_included"))
    if items:
        st.write(t("list_items"))
        for i, val in enumerate(items):
            cols = st.columns([0.9,0.1])
            with cols[0]:
                st.write(f"- {val}")
            with cols[1]:
                if st.button("✖", key=f"del_{key}_{i}"):
                    items.pop(i)
                    plan[key] = items
                    st.rerun()

if current == t("step_assunto"):
    st.subheader(t("assunto_header"))
    plan["title"] = st.text_input(t("assunto_titulo"), plan["title"] or t("plan_default_title"), max_chars=MAX_TITLE_LENGTH)
    c1, c2, c3 = st.columns(3)
    with c1:
        plan["subject"]["what"] = st.text_input(t("assunto_what"), plan["subject"]["what"], max_chars=MAX_ITEM_LENGTH)
    with c2:
        plan["subject"]["who"] = st.text_input(t("assunto_who"), plan["subject"]["who"], max_chars=MAX_ITEM_LENGTH)
    with c3:
        plan["subject"]["where"] = st.text_input(t("assunto_where"), plan["subject"]["where"], max_chars=MAX_ITEM_LENGTH)
    
    st.markdown("---")
    with st.expander(t("assunto_guia"), expanded=False):
        st.markdown("""
O processo de produção de conhecimento (Inteligência) inicia-se com o acionamento por parte do **DECISOR** ou **DEMANDANTE** (no caso de empresas ou organizações).

**Sequência:**

**DEMANDA** → acionamento  
**ABORDAGEM** → coleta dos dados/informações iniciais (contexto, problema, envolvidos, sistemas, prazos, espaço temporal e ligações)  
**EXECUÇÃO** → NECESSIDADE DE CONHECIMENTOS ⇒ PLANO DE OBTENÇÃO ⇒ EXECUÇÃO DO CICLO DE INTELIGÊNCIA ⇒ PRODUÇÃO DE CONHECIMENTOS ⇒ ENTREGA DOS CONHECIMENTOS

**Processamento:**

### 1ª FASE - PLANEJAMENTO (Identificar e listar a Necessidade de Conhecimentos)

Planejar é conceber a solução para um problema. É combinar arte e ciência para obter a mais precisa compreensão sobre ele, vislumbrando o estado final ou os objetivos que se desejam alcançar quando o problema for resolvido, e estabelecendo formas eficazes para que isso aconteça.

**O bom planejamento facilita:**
- Compreender e desenvolver soluções para os problemas.
- Antecipar eventos e adaptar-se às mudanças de circunstâncias.
- Organizar os meios a sua disposição e priorizar esforços

Dada a natureza incerta e dinâmica das sociedades, o objeto do planejamento não é eliminar a incerteza, mas desenvolver um quadro de ação no meio de tanta incerteza.

Simplificando, o planejar é **pensar de forma crítica e criativa** sobre o que fazer e como fazê-lo para solução de problema(s), enquanto antecipa mudanças ao longo do caminho.

A **1ª Fase - Planejamento de Inteligência**, é a fase na qual o analista de Inteligência, encarregado de produzir um conhecimento, realiza o estudo preliminar e geral do problema e estabelece os procedimentos necessários para cumprir a missão.

**Durante a fase do planejamento, o analista adota os seguintes procedimentos:**

**a) determinação do assunto a ser abordado:**
   
O assunto é, normalmente, definido por meio de uma expressão oral ou escrita, respondendo às seguintes perguntas:
- **O quê?**
- **Quem?**
- **Onde?**
        """)

elif current == t("step_faixa_tempo"):
    st.subheader(t("tempo_header"))
    c1, c2 = st.columns(2)
    with c1:
        start = st.date_input(t("tempo_inicio"), value=date.today())
        plan["time_window"]["start"] = start.isoformat()
    with c2:
        end = st.date_input(t("tempo_fim"), value=date.today())
        plan["time_window"]["end"] = end.isoformat()
    
    st.info(t("tempo_info"))
    
    with st.expander(t("tempo_guia"), expanded=False):
        st.markdown("""
**b) determinação da faixa de tempo em que o assunto deve ser considerado;**

Este procedimento consiste em estabelecer a amplitude do tempo para o estudo considerado. A determinação da faixa de tempo é feita levando-se em conta, sobretudo, as necessidades do usuário do conhecimento em produção.
        """)
    
    # Carregar imagem da faixa de tempo (tentar múltiplos caminhos)
    try:
        faixa_paths = [
            ASSETS_DIR / "faixa_tempo.png",
            SCRIPT_DIR / "attached_assets" / "faixa_tempo.png",
            SCRIPT_DIR.parent / "docs" / "attached_assets" / "faixa_tempo.png",
        ]
        img_faixa = None
        for p in faixa_paths:
            if p.exists() and p.is_file():
                try:
                    img_faixa = Image.open(p)
                    break
                except Exception:
                    continue
        if img_faixa:
            st.image(img_faixa, caption=t("tempo_caption"), use_column_width=True)
        else:
            st.info(t("tempo_img_fallback"))
    except (FileNotFoundError, IOError, OSError) as e:
        st.info(t("tempo_img_fallback"))
    except Exception:
        st.info(t("tempo_img_fallback"))

elif current == t("step_usuario"):
    st.subheader(t("usuario_header"))
    plan["user"]["principal"] = st.text_input(t("usuario_principal"), plan["user"]["principal"], max_chars=MAX_ITEM_LENGTH)
    plan["user"]["others"] = st.text_input(t("usuario_outros"), plan["user"]["others"], max_chars=MAX_ITEM_LENGTH)
    plan["user"]["depth"] = st.selectbox(t("usuario_profundidade"), ["executivo","gerencial","tecnico"], index=0)
    plan["user"]["secrecy"] = st.selectbox(t("usuario_sigilo"), ["publico","restrito","confidencial","secreto"], index=0)
    
    st.info(t("usuario_info"))
    
    with st.expander(t("usuario_guia"), expanded=False):
        st.markdown("""
**c) determinação do usuário do conhecimento;**

Esse procedimento visa a ajustar o conhecimento que está sendo produzido ao nível do usuário e a auxiliar a definição de prioridades.

O analista deverá definir a autoridade a que se destina o produto e, no caso de haver mais de um usuário, a prioridade de atendimento. Exemplo: CEO e divisão jurídica.

A determinação do usuário visa, principalmente, a estabelecer o nível de profundidade do conhecimento a ser produzido, medidas de sigilo e utilização de meios auxiliares para explicação (fotos, gráficos, outros idiomas, etc).
        """)

elif current == t("step_finalidade"):
    st.subheader(t("finalidade_header"))
    plan["purpose"] = st.text_area(t("finalidade_label"), plan["purpose"], height=150, max_chars=MAX_TEXT_LENGTH)
    
    st.info(t("finalidade_info"))
    
    with st.expander(t("finalidade_guia"), expanded=False):
        st.markdown("""
**d) determinação da finalidade do conhecimento;**

Este tópico diz respeito à utilização, pelo usuário, do conhecimento em produção (Muito Importante). Nem sempre é possível a determinação dessa finalidade (o cliente sabe o que quer, mas não sabe transmitir). Nesse caso, o planejamento é orientado para esgotar o assunto tratado, de tal modo que o usuário venha a encontrar subsídios úteis à sua atuação.

O correto entendimento do processo decisório e, consequentemente, das atribuições próprias de cada uma das autoridades, facilita a determinação da finalidade do conhecimento.
        """)

elif current == t("step_prazo"):
    st.subheader(t("prazo_header"))
    c1, c2 = st.columns(2)
    with c1:
        plan["deadline"]["date"] = st.date_input(t("prazo_data"), value=date.today()).isoformat()
    with c2:
        plan["deadline"]["urgency"] = st.selectbox(t("prazo_urgencia"), ["baixa","media","alta","critica"], index=1)
    
    with st.expander(t("prazo_guia"), expanded=False):
        st.markdown("""
**e) determinação do prazo disponível para a produção do conhecimento;**

Quando esses prazos não estão previamente determinados, são eles estabelecidos com base:
- no correto entendimento do problema e da dinâmica de coleta de dados e informações nesse processo;
- na importância do trabalho em execução e do seu usuário; e
- na complexidade do trabalho que está sendo desenvolvido.

A correta determinação do prazo constitui um fator preponderante para que o conhecimento em produção seja utilizado em tempo hábil, atendendo ao princípio da oportunidade.

Determinará, também, a abrangência do assunto, pois, quanto menos tempo dispuser o analista para finalizar o seu estudo, menor quantidade de dados e conhecimentos poderá reunir.
        """)

elif current == t("step_aspectos_essenciais"):
    st.subheader(t("aspectos_ess_header"))
    save_list(t("step_aspectos_essenciais"), "aspects_essential")
    
    st.info(t("aspectos_ess_info"))
    
    with st.expander(t("aspectos_ess_guia"), expanded=False):
        st.markdown("""
**f) identificação dos aspectos essenciais do assunto**

Realiza-se um levantamento dos aspectos essenciais que deverão ser abordados, para que o assunto possa ser esclarecido. Compõem um arcabouço preliminar do conhecimento em produção, coerente com as considerações a respeito do usuário e da finalidade anteriormente abordadas.

O levantamento dos aspectos essenciais deve ser flexível, de tal modo que possa ser, eventualmente, redimensionado, de acordo com mudanças imprevistas na configuração do assunto e/ou do fato ou da situação ao longo do trabalho de produção do conhecimento.

Trata-se de listar o que o analista, nesta etapa do estudo, necessita saber para extrair conclusões sobre o assunto estudado. Tal lista poderá ser ampliada ou sofrer supressões em decorrência da evolução do estudo (Pivotagem).
        """)

elif current == t("step_aspectos_conhecidos"):
    st.subheader(t("aspectos_known_header"))
    save_list(t("step_aspectos_conhecidos"), "aspects_known")
    
    st.info(t("aspectos_known_info"))
    
    with st.expander(t("aspectos_known_guia"), expanded=False):
        st.markdown("""
**g) identificação dos aspectos essenciais conhecidos;**

Este procedimento consiste em verificar, dentre os aspectos essenciais já determinados, aqueles para os quais já se tenha algum tipo de resposta, antes do desencadeamento de qualquer medida de reunião.

Sendo o planejamento de uso estritamente pessoal do analista, o seu equacionamento é livre. Em razão disso, especificamente quanto à verificação dos aspectos essenciais conhecidos, poderá variar desde a simples indicação dos aspectos já conhecidos até o relacionamento de todas as respostas que a eles se vinculem.

É indispensável que, dos aspectos essenciais conhecidos, sejam separadas as respostas completas das incompletas e as que expressam certeza daquelas que apresentam algum grau de incerteza.

A execução desse procedimento é fundamental para a verificação dos aspectos essenciais a conhecer (próxima subfase).
        """)

elif current == t("step_aspectos_conhecer"):
    st.subheader(t("aspectos_toknow_header"))
    st.caption(t("aspectos_toknow_dica"))
    save_list(t("step_aspectos_conhecer"), "aspects_to_know")
    
    with st.expander(t("aspectos_toknow_guia"), expanded=False):
        st.markdown("""
**h) identificação dos aspectos essenciais a conhecer;**

Esta tarefa consiste, basicamente, na verificação dos aspectos essenciais para os quais o analista:
- não tenha, em seu acervo, qualquer resposta;
- necessite de novos elementos de convicção para as respostas já à sua disposição; e
- necessite completar as respostas já disponíveis.

Este procedimento será materializado em uma listagem do que obter para atender aos casos acima, como forma de preparar, com objetividade, a fase da reunião.

Na prática, o procedimento proposto é o resultado do levantamento dos Aspectos Essenciais (necessários ao assunto) menos os Aspectos Essenciais Conhecidos (excluídos os incompletos e os que não expressam certeza). O produto são as **NECESSIDADES DE CONHECER**.
        """)

elif current == t("step_pirs_coleta"):
    st.subheader(t("pirs_header"))
    
    st.info(t("pirs_info"))
    
    if plan["aspects_to_know"]:
        aspect_options = [f"{i} - {txt}" for i, txt in enumerate(plan["aspects_to_know"])]
        aspect_sel = st.selectbox(t("pirs_link_aspect"), aspect_options, index=0)
        q = st.text_input(t("pirs_pergunta"), max_chars=MAX_PIR_QUESTION_LENGTH)
        pr = st.selectbox(t("pirs_prioridade"), ["baixa","media","alta","critica"], index=1)
        just = st.text_input(t("pirs_justificativa"), max_chars=MAX_ITEM_LENGTH)
        if st.button(t("pirs_incluir")):
            idx = int(aspect_sel.split(" - ")[0]) if aspect_sel else None
            plan["pirs"].append({"aspect_ref": idx, "question": q, "priority": pr, "justification": just})
            st.success(t("pirs_incluido"))
    else:
        st.info(t("pirs_add_aspects"))
    if plan["pirs"]:
        st.write("### " + t("pirs_cadastrados"))
        for i, p in enumerate(plan["pirs"]):
            st.write(f"- **#{i}** [aspecto {p.get('aspect_ref','-')}] — {p.get('question','')} (prio: {p.get('priority','')})")

    st.markdown("---")
    st.subheader(t("coleta_header"))
    if plan["pirs"]:
        pir_opts = [f"{i} - {p.get('question','')[:60]}" for i,p in enumerate(plan["pirs"])]
        sel_pir = st.selectbox(t("coleta_ref"), pir_opts, index=0, key="pir_sel_coleta")
        src = st.text_input(t("coleta_fonte"), max_chars=MAX_ITEM_LENGTH)
        mth = st.text_input(t("coleta_metodo"), max_chars=MAX_ITEM_LENGTH)
        freq = st.selectbox(t("coleta_frequencia"), ["unico","diario","semanal","mensal"], index=0)
        owner = st.text_input(t("coleta_responsavel"), max_chars=MAX_ITEM_LENGTH)
        sla = st.number_input(t("coleta_sla"), min_value=0, value=0, step=1)
        if st.button(t("coleta_incluir")):
            pir_index = int(sel_pir.split(" - ")[0])
            plan["collection"].append({"pir_index": pir_index, "source": src, "method": mth, "frequency": freq, "owner": owner, "sla_hours": int(sla)})
            st.success(t("coleta_incluida"))
    else:
        st.info(t("coleta_cadastre_pir"))

elif current == t("step_medidas_extraordinarias"):
    st.subheader(t("extra_header"))
    save_list(t("step_medidas_extraordinarias"), "extraordinary")
    
    with st.expander(t("extra_guia"), expanded=False):
        st.markdown("""
**i) previsão de medidas extraordinárias**

Este procedimento se traduz na previsão de medidas que extrapolem os recursos normais da estrutura de Inteligência e que se mostrem indispensáveis à produção do conhecimento (pesquisas de opinião, contratação de especialistas, acesso a base de dados, etc.).

Medidas desse tipo, normalmente, são previstas somente nos níveis mais elevados da estrutura de Inteligência, particularmente no nível estratégico.
        """)

elif current == t("step_medidas_seguranca"):
    st.subheader(t("seg_header"))
    save_list(t("step_medidas_seguranca"), "security")
    
    with st.expander(t("seg_guia"), expanded=False):
        st.markdown("""
**j) adoção de medidas de segurança, se for o caso.**

Já no planejamento, o analista identifica e estabelece as medidas necessárias à proteção das ações que estão sendo desenvolvidas (os próprios procedimentos do planejamento já configuram ações de produção) e do resultado que, gradualmente, vem sendo obtido. Para isso, adota medidas cautelares (com base, principalmente, na natureza do assunto tratado), que se estendem por toda a produção do conhecimento.

Este é um procedimento considerado muito relevante, já que é da própria essência da atividade de Inteligência a vinculação entre a produção e a proteção do conhecimento.

Há de se considerar que a adoção de medidas de segurança poderá ser um fator de limitação das ações desenvolvidas nas demais fases da metodologia.
        """)

elif current == t("step_preview"):
    st.subheader(t("preview_header"))
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### " + t("preview_identificacao"))
        st.write("**" + t("preview_titulo") + "**", plan["title"])
        st.write("**" + t("preview_assunto") + "**", plan["subject"])
        st.write("**" + t("preview_tempo") + "**", plan["time_window"])
        st.write("**" + t("preview_usuario") + "**", plan["user"])
        st.write("**" + t("preview_finalidade") + "**", plan["purpose"])
        st.write("**" + t("preview_prazo") + "**", plan["deadline"])
    with c2:
        st.markdown("### " + t("preview_estrutura"))
        st.write("**" + t("preview_essenciais") + "**", plan["aspects_essential"])
        st.write("**" + t("preview_conhecidos") + "**", plan["aspects_known"])
        st.write("**" + t("preview_conhecer") + "**", plan["aspects_to_know"])
        st.write("**" + t("preview_pirs") + "**", plan.get("pirs", []))
        st.write("**" + t("preview_coleta") + "**", plan.get("collection", []))
        st.write("**" + t("preview_extra") + "**", plan["extraordinary"])
        st.write("**" + t("preview_seg") + "**", plan["security"])

    st.markdown("---")
    st.markdown("### " + t("preview_kpis"))
    total_ess = len(plan["aspects_essential"])
    total_known = len(plan["aspects_known"])
    total_to_know = len(plan["aspects_to_know"])
    total_pirs = len(plan.get("pirs", []))
    total_tasks = len(plan.get("collection", []))
    coverage = (total_known / total_ess * 100) if total_ess else 0.0
    linkage = (total_tasks / total_pirs * 100) if total_pirs else 0.0
    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric(t("preview_essenciais_metric"), total_ess)
    k2.metric(t("preview_conhecidos_metric"), total_known)
    k3.metric(t("preview_conhecer_metric"), total_to_know)
    k4.metric(t("preview_pirs_metric"), total_pirs)
    k5.metric(t("preview_tarefas_metric"), total_tasks)
    st.caption(t("preview_coverage", pct=coverage, link=linkage))

    st.markdown("### " + t("preview_gantt"))
    if total_tasks > 0:
        rows = []
        try:
            dl = datetime.fromisoformat(plan["deadline"].get("date") or "")
        except (ValueError, TypeError):
            dl = datetime.now(timezone.utc)
        for i, coll in enumerate(plan.get("collection", [])):
            sla_h = int(coll.get("sla_hours",0))
            start = dl - timedelta(hours=sla_h)
            end = dl
            rows.append({t("gantt_task"): f"PIR{coll.get('pir_index','')} - {coll.get('source','')}", t("gantt_start"): start, t("gantt_end"): end})
        df = pd.DataFrame(rows)
        st.dataframe(df)
    else:
        st.info(t("preview_sem_tarefas"))

elif current == t("step_revisao_export"):
    st.subheader(t("revisao_header"))
    
    # Criar abas para melhor organização
    tab1, tab2, tab3, tab4 = st.tabs([t("revisao_visualizar"), t("revisao_salvar"), t("revisao_exportar"), t("revisao_evidencias")])
    
    with tab1:
        st.markdown("### " + t("revisao_conteudo"))
        st.json(plan)
    
    with tab2:
        st.markdown("### " + t("revisao_gerenciamento"))
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### " + t("revisao_salvar_plano"))
            if st.button(t("revisao_salvar_btn"), key="save_plan", use_container_width=True):
                with st.spinner(t("revisao_salvando")):
                    # Sanitizar dados antes de enviar
                    sanitized_plan = sanitize_plan_data(plan)
                    with httpx.Client(timeout=10, headers=_api_headers()) as client:
                        r = client.post(f"{API_URL}/plans", json=sanitized_plan)
                        if r.status_code == 200:
                            st.session_state.saved_plan = r.json()
                            st.success(t("revisao_sucesso", id=r.json()['id']))
                        else:
                            st.error(t("revisao_erro", text=r.text))
            
            # Mostrar status do plano salvo
            saved = st.session_state.get("saved_plan")
            if saved:
                st.info(t("revisao_plano_atual", id=saved['id']))

            st.markdown("#### " + t("revisao_atualizar_sec"))
            vl = st.text_input(t("revisao_version_label"), value="", key="ver_label_put", max_chars=200)
            if st.button(t("revisao_atualizar_plano"), key="update_plan_btn", use_container_width=True):
                saved_u = st.session_state.get("saved_plan")
                if not saved_u:
                    st.warning(t("revisao_salve_primeiro"))
                else:
                    with st.spinner(t("revisao_atualizando")):
                        sanitized_plan = sanitize_plan_data(plan)
                        lbl = vl.strip()
                        sanitized_plan["version_label"] = lbl if lbl else None
                        with httpx.Client(timeout=20, headers=_api_headers()) as client:
                            r = client.put(f"{API_URL}/plans/{saved_u['id']}", json=sanitized_plan)
                        if r.status_code == 200:
                            st.session_state.saved_plan = r.json()
                            st.success(t("revisao_atualizado"))
                        else:
                            st.error(t("revisao_erro", text=r.text))
        
        with col2:
            st.markdown("#### " + t("revisao_lgpd"))
            if st.button(t("revisao_check_lgpd"), key="check_lgpd", use_container_width=True):
                saved = st.session_state.get("saved_plan")
                if not saved:
                    st.warning(t("revisao_salve_primeiro"))
                else:
                    with st.spinner(t("revisao_validando")):
                        with httpx.Client(timeout=10, headers=_api_headers()) as client:
                            r = client.post(f"{API_URL}/plans/{saved['id']}/lgpd_check")
                            result = r.json()
                            
                            # Mostrar resultado com cores
                            if result.get("compliant"):
                                st.success(t("revisao_conforme"))
                            else:
                                st.error(t("revisao_nao_conforme"))
                            
                            # Expandir detalhes
                            with st.expander(t("revisao_detalhes")):
                                st.json(result)
    
    with tab3:
        st.markdown("### " + t("revisao_exportar_relatorio"))
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### " + t("revisao_exportar_pdf"))
            if st.button(t("revisao_gerar_pdf"), key="export_pdf_btn", use_container_width=True):
                saved = st.session_state.get("saved_plan")
                if not saved:
                    st.warning(t("revisao_salve_para_pdf"))
                else:
                    with st.spinner(t("revisao_gerando")):
                        with httpx.Client(timeout=10, headers=_api_headers()) as client:
                            r = client.get(f"{API_URL}/export/pdf/{saved['id']}")
                            if r.status_code == 200:
                                st.session_state.pdf_content = r.content
                                st.session_state.pdf_filename = f"plan_{saved['id']}.pdf"
                                st.success(t("revisao_pdf_ok"))
                            else:
                                st.error(t("revisao_erro", text=r.text))
            
            # Botão de download se PDF foi gerado
            if "pdf_content" in st.session_state:
                st.download_button(
                    label=t("revisao_baixar_pdf"),
                    data=st.session_state.pdf_content,
                    file_name=st.session_state.pdf_filename,
                    mime="application/pdf",
                    use_container_width=True
                )
        
        with col2:
            st.markdown("#### " + t("revisao_exportar_html"))
            if st.button(t("revisao_gerar_html"), key="export_html_btn", use_container_width=True):
                saved = st.session_state.get("saved_plan")
                if not saved:
                    st.warning(t("revisao_salve_para_html"))
                else:
                    with st.spinner(t("revisao_gerando")):
                        with httpx.Client(timeout=10, headers=_api_headers()) as client:
                            r = client.get(f"{API_URL}/export/html/{saved['id']}")
                            if r.status_code == 200:
                                st.session_state.html_content = r.content
                                st.session_state.html_filename = f"plan_{saved['id']}.html"
                                st.success(t("revisao_html_ok"))
                            else:
                                st.error(t("revisao_erro", text=r.text))
            
            # Botão de download se HTML foi gerado
            if "html_content" in st.session_state:
                st.download_button(
                    label=t("revisao_baixar_html"),
                    data=st.session_state.html_content,
                    file_name=st.session_state.html_filename,
                    mime="text/html",
                    use_container_width=True
                )
    
    with tab4:
        st.markdown("### " + t("revisao_evidencias_titulo"))
        saved = st.session_state.get("saved_plan")
        if not saved:
            st.info(t("revisao_salve_evidencias"))
        else:
            st.markdown("#### " + t("revisao_upload"))
            up = st.file_uploader(t("revisao_selecionar"), key=f"uploader_{saved['id']}")
            if up is not None:
                if st.button(t("revisao_enviar"), key=f"upload_btn_{saved['id']}", use_container_width=True):
                    with st.spinner(t("revisao_enviando")):
                        # Sanitizar nome do arquivo
                        safe_filename = os.path.basename(up.name) if up.name else "file"
                        safe_filename = sanitize_string(safe_filename, 255)
                        with httpx.Client(timeout=60, headers=_api_headers()) as client:
                            files = {"file": (safe_filename, up.getvalue())}
                            data = {"plan_id": str(saved["id"])}
                            r = client.post(f"{API_URL}/evidence/upload", files=files, data=data)
                            if r.status_code == 200:
                                result = r.json()
                                st.success(t("revisao_evidencia_ok"))
                                st.info(f"📄 **{result['filename']}** → SHA-256: `{result['sha256']}`")
                            else:
                                st.error(f"❌ Erro no upload: {r.text}")

elif current == t("step_imagens"):
    st.subheader(t("imagens_header"))
    st.markdown(t("imagens_desc"))
    
    st.markdown("---")
    st.info(t("imagens_info"))
    
    st.markdown("### " + t("imagens_sequenciamento"))
    try:
        # Caminho correto: docs/attached_assets/Metod Prod Conh ROC.png
        metod_paths = [
            SCRIPT_DIR.parent / "docs" / "attached_assets" / "Metod Prod Conh ROC.png",
            ASSETS_DIR / "Metod Prod Conh ROC.png",
            SCRIPT_DIR / "attached_assets" / "Metod Prod Conh ROC.png",
            SCRIPT_DIR.parent / "docs" / "attached_assets" / "Metod_Prod_Conh_ROC.png",
            ASSETS_DIR / "Metod_Prod_Conh_ROC.png",
        ]
        img1 = None
        for p in metod_paths:
            if p.exists() and p.is_file():
                try:
                    img1 = Image.open(p)
                    break
                except Exception:
                    continue
        if img1:
            st.image(img1, caption=t("imagens_metodologia"), use_column_width=True)
        else:
            st.info(t("imagens_fallback"))
    except (FileNotFoundError, IOError, OSError):
        st.info(t("imagens_fallback"))
    except Exception:
        st.info(t("imagens_fallback"))
    
    st.markdown("---")
    st.markdown("### " + t("imagens_ciclo"))
    try:
        # Tentar múltiplos nomes possíveis para a imagem do ciclo (nome correto primeiro)
        img_filenames = [
            "Ciclo Inteligencia ROC.png",
            "Ciclo_Inteligencia_ROC.png",
            "CicloInteligenciaROC.png",
            "REALIMENTAÇÃO_1762990436433.png",  # Fallback para nome antigo
            "ciclo_inteligencia.png",  # Fallback adicional
            "REALIMENTAÇÃO.png",
            "ciclo.png",
        ]
        
        img2 = None
        found_path = None
        for img_filename in img_filenames:
            img_paths = [
                ASSETS_DIR / img_filename,
                Path(__file__).parent.parent / "docs" / "attached_assets" / img_filename,
                Path(__file__).parent / "attached_assets" / img_filename,
                Path(__file__).parent.parent.parent / "docs" / "attached_assets" / img_filename,
            ]
            
            for img_path in img_paths:
                if img_path.exists() and img_path.is_file():
                    try:
                        img2 = Image.open(img_path)
                        found_path = img_path
                        break
                    except Exception as e:
                        continue
            
            if img2:
                break
        
        if img2:
            # Reduzir tamanho da imagem para melhor compreensão (~70% das dimensões originais)
            w, h = img2.size
            new_size = (int(w * 0.7), int(h * 0.7))
            try:
                resample = Image.Resampling.LANCZOS
            except AttributeError:
                resample = Image.LANCZOS
            img2_resized = img2.resize(new_size, resample=resample)
            st.image(img2_resized, caption=t("imagens_ciclo_caption"))
        else:
            st.info(t("imagens_fallback"))
    except (FileNotFoundError, IOError, OSError):
        st.info(t("imagens_fallback"))
    except Exception:
        st.info(t("imagens_fallback"))

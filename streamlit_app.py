import hashlib
import os
from datetime import datetime

import pandas as pd
import streamlit as st

from backend.app.registry import ModelRegistry
from backend.app.schemas import AnalyzeRequest
from backend.app.service import Analyzer
from backend.app.signals import assess_quality, prepare_signal
from portal.access import ALLOWED_DOMAINS, authorize_claims
from portal.catalog import MODALITIES, SYMPTOMS, generate_signal
from portal.reporting import html_report, json_document
from portal.signal_io import compact_signal, read_signal_bytes


st.set_page_config(
    page_title="PET-Saúde PathClass 3.0",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)


STYLES = """
<style>
:root {
  --navy: #112f38;
  --teal: #0f766e;
  --mint: #dff2ed;
  --ink: #183036;
  --muted: #66797c;
  --line: #dce5e3;
}
[data-testid="stAppViewContainer"] {
  background: #f3f6f5;
}
[data-testid="stHeader"] {
  background: rgba(243, 246, 245, 0.92);
}
[data-testid="stSidebar"] {
  background: var(--navy);
}
[data-testid="stSidebar"] * {
  color: #f8fbfa;
}
[data-testid="stSidebar"] [role="radiogroup"] label {
  border-radius: 9px;
  padding: 8px 10px;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
  background: rgba(255, 255, 255, 0.08);
}
.block-container {
  max-width: 1440px;
  padding-top: 2rem;
  padding-bottom: 4rem;
}
h1, h2, h3 {
  color: var(--ink);
  letter-spacing: -0.02em;
}
p, li {
  color: var(--muted);
}
.brand {
  padding: 4px 2px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.14);
  margin-bottom: 20px;
}
.brand strong {
  display: block;
  color: #ffffff;
  font-size: 1.14rem;
}
.brand span {
  color: #a8c4c4;
  font-size: 0.78rem;
}
.page-head {
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 28px 30px;
  margin-bottom: 18px;
}
.page-head h1 {
  margin: 2px 0 8px;
  font-size: 2rem;
}
.page-head p {
  margin: 0;
  max-width: 840px;
}
.eyebrow {
  color: var(--teal);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.institutional {
  background: var(--mint);
  border: 1px solid #b9ddd4;
  border-radius: 10px;
  color: #155e56;
  padding: 11px 14px;
  margin: 8px 0 18px;
  font-size: 0.86rem;
}
.login-card {
  max-width: 560px;
  margin: 12vh auto 0;
  padding: 34px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 16px;
  box-shadow: 0 18px 55px rgba(17, 47, 56, 0.09);
}
.result-head {
  background: var(--navy);
  border-radius: 14px;
  padding: 24px 26px;
  margin-top: 28px;
}
.result-head h2, .result-head p, .result-head span {
  color: #ffffff;
}
.notice {
  background: #fff8e8;
  border: 1px solid #eddbad;
  border-radius: 10px;
  padding: 13px 15px;
  color: #6e5417;
  margin: 14px 0;
}
.case-title {
  font-weight: 700;
  color: var(--ink);
}
div[data-testid="stMetric"] {
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 14px 16px;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
  border-color: var(--line);
  border-radius: 13px;
}
.stButton > button[kind="primary"] {
  background: var(--teal);
  border-color: var(--teal);
}
</style>
"""


st.markdown(STYLES, unsafe_allow_html=True)


@st.cache_resource
def analyzer() -> Analyzer:
    os.environ.setdefault("PET_SAUDE_DEMO_MODE", "true")
    return Analyzer(ModelRegistry())


def local_access_enabled() -> bool:
    return os.getenv("PET_SAUDE_LOCAL_AUTH_BYPASS", "false").strip().lower() == "true"


def authentication_configured() -> bool:
    try:
        settings = st.secrets["auth"]
        required = ["redirect_uri", "cookie_secret", "client_id", "client_secret", "server_metadata_url"]
        return all(settings.get(item) for item in required)
    except (FileNotFoundError, KeyError, TypeError):
        return False


def access_screen() -> dict:
    if local_access_enabled():
        return {"email": "desenvolvimento@ucpel.edu.br", "name": "Desenvolvimento local", "local": True}
    if not authentication_configured():
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.title("PET-Saúde PathClass 3.0")
        st.error("A autenticação Google ainda não foi configurada nesta instalação.")
        st.write("Adicione as credenciais OIDC aos Secrets do Streamlit antes de liberar a aplicação.")
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()
    if not st.user.is_logged_in:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<span class="eyebrow">Acesso institucional</span>', unsafe_allow_html=True)
        st.title("PET-Saúde PathClass 3.0")
        st.write("Entre com sua conta Google institucional para acessar a aplicação.")
        st.markdown("<div class=\"institutional\">Domínios autorizados: @ucpel.edu.br e @sou.ucpel.edu.br</div>", unsafe_allow_html=True)
        if st.button("Entrar com Google", type="primary", use_container_width=True):
            st.login()
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()
    claims = dict(st.user)
    allowed, email, reason = authorize_claims(claims)
    if not allowed:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.title("Acesso não autorizado")
        st.error(reason)
        if email:
            st.write(f"Conta autenticada: {email}")
        if st.button("Sair da conta", use_container_width=True):
            st.logout()
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()
    return {"email": email, "name": claims.get("name") or email.split("@", 1)[0], "local": False}


def initialize_state() -> None:
    defaults = {
        "view": "Visão geral",
        "modality": "ecg",
        "signal": None,
        "file_name": "",
        "file_token": "",
        "sample_rate": MODALITIES["ecg"]["sample_rate"],
        "record_code": f"PET-{datetime.now().year}-001",
        "symptoms": [],
        "notes": "",
        "result": None,
        "history": []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def select_modality(modality: str, load_demo: bool = False) -> None:
    st.session_state.modality = modality
    st.session_state.sample_rate = MODALITIES[modality]["sample_rate"]
    st.session_state.signal = generate_signal(modality) if load_demo else None
    st.session_state.file_name = f"amostra_{modality}_demonstrativa.csv" if load_demo else ""
    st.session_state.file_token = f"demo-{modality}" if load_demo else ""
    st.session_state.result = None


def open_demo(modality: str) -> None:
    select_modality(modality, True)
    st.session_state.view = "Nova análise"
    st.rerun()


def save_case(result: dict) -> None:
    previous = [item for item in st.session_state.history if item["id"] != result["id"]]
    st.session_state.history = [result, *previous][:20]


def page_header(kicker: str, title: str, description: str) -> None:
    st.markdown(
        f'<section class="page-head"><span class="eyebrow">{kicker}</span><h1>{title}</h1><p>{description}</p></section>',
        unsafe_allow_html=True
    )


def overview_page() -> None:
    page_header(
        "PET-Saúde",
        "Análise de sinais fisiológicos",
        "Selecione uma modalidade, envie um sinal desidentificado e consulte a avaliação de qualidade e a pré-análise acadêmica."
    )
    left, center, right = st.columns(3)
    left.metric("Modalidades preparadas", "7", "ECG, EMG, EEG, PPG, RESP, LUNG e PCG", delta_color="off")
    center.metric("Bases catalogadas", "16", "Treinamento e validação por modalidade", delta_color="off")
    right.metric("Casos nesta sessão", len(st.session_state.history), "Sem persistência no servidor", delta_color="off")
    st.subheader("Análises disponíveis")
    columns = st.columns(3)
    for index, (modality, metadata) in enumerate(MODALITIES.items()):
        with columns[index % 3]:
            with st.container(border=True):
                st.markdown(f"### {metadata['name']}")
                st.write(metadata["full_name"])
                st.caption(metadata["target"])
                preview = compact_signal(generate_signal(modality, 480), 180)
                st.line_chart(preview, height=105)
                if st.button("Abrir demonstração", key=f"overview-{modality}", use_container_width=True):
                    open_demo(modality)
    st.subheader("Análises recentes")
    if not st.session_state.history:
        with st.container(border=True):
            st.info("Nenhuma análise foi salva nesta sessão.")
            if st.button("Iniciar análise", type="primary"):
                st.session_state.view = "Nova análise"
                st.rerun()
        return
    recent = [{
        "Modalidade": item["modalityName"],
        "Caso": item["recordCode"],
        "Classe priorizada": item["primaryFinding"],
        "Qualidade": f"{item['inspection']['quality']}%",
        "Status": item["status"]
    } for item in st.session_state.history[:5]]
    st.dataframe(pd.DataFrame(recent), use_container_width=True, hide_index=True)


def load_uploaded_signal(uploaded) -> None:
    data = uploaded.getvalue()
    token = hashlib.sha256(data).hexdigest()
    if token == st.session_state.file_token:
        return
    values = read_signal_bytes(data, uploaded.name)
    st.session_state.signal = values
    st.session_state.file_name = uploaded.name
    st.session_state.file_token = token
    st.session_state.result = None


def signal_quality():
    values = st.session_state.signal
    if values is None:
        return None, None
    prepared = prepare_signal(values.tolist(), int(st.session_state.sample_rate), st.session_state.modality)
    return prepared, assess_quality(prepared)


def quality_panel(quality: dict | None) -> None:
    with st.container(border=True):
        st.subheader("Controle de qualidade")
        if quality is None:
            st.info("Envie um sinal para avaliar duração, ruído, saturação e faixa dinâmica.")
            return
        st.progress(quality["quality"] / 100, text=f"{quality['status']} · {quality['quality']}%")
        st.write(quality["message"])
        first, second = st.columns(2)
        first.metric("Amostras válidas", f"{quality['valid_samples']:,}".replace(",", "."))
        second.metric("Duração", f"{quality['duration']:.2f} s")
        third, fourth = st.columns(2)
        third.metric("Ruído relativo", f"{quality['noise_ratio'] * 100:.1f}%")
        fourth.metric("Saturação", f"{quality['clipping'] * 100:.1f}%")


def analysis_result(result: dict) -> None:
    st.markdown(
        f'<section class="result-head"><span class="eyebrow">Resultado para revisão</span><h2>Pré-análise concluída</h2><p>{result["id"]} · {result["recordCode"]}</p></section>',
        unsafe_allow_html=True
    )
    if result.get("urgentContext"):
        st.error("Há sinal ou sintoma de alarme informado. Aplique o protocolo assistencial institucional independentemente da classificação.")
    if result.get("outOfDistribution"):
        st.warning("O sinal difere da distribuição de referência ou não existe um modelo treinado registrado. A classificação não deve orientar decisão clínica.")
    calibrated = result.get("probabilityMode") == "calibrated_research"
    score_label = "Probabilidade" if calibrated else "Escore"
    finding, probability, quality = st.columns(3)
    finding.metric("Classe priorizada", result["primaryFinding"])
    probability.metric(score_label, f"{result['confidence']}%", f"Incerteza {result['uncertainty'].lower()}", delta_color="off")
    quality.metric("Qualidade", f"{result['inspection']['quality']}%", result["inspection"]["status"], delta_color="off")
    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.subheader("Hipóteses do modelo")
            probabilities = pd.DataFrame({
                "Hipótese": [item["label"] for item in result["probabilities"]],
                score_label: [round(item["value"] * 100, 2) for item in result["probabilities"]]
            }).set_index("Hipótese")
            st.bar_chart(probabilities, height=280)
            if calibrated:
                st.caption("Probabilidades condicionais de pesquisa, calibradas no domínio documentado. Não representam prevalência ou risco individual.")
            else:
                st.caption("Escores demonstrativos sem calibração clínica. Não representam prevalência ou risco individual.")
    with right:
        with st.container(border=True):
            st.subheader("Características examinadas")
            features = pd.DataFrame({
                "Característica": [item["name"] for item in result["features"]],
                "Relevância relativa": [item["value"] for item in result["features"]]
            }).set_index("Característica")
            st.bar_chart(features, height=280)
            for feature in result["features"]:
                st.caption(f"{feature['name']}: {feature['direction']}")
    with st.container(border=True):
        st.subheader("Próximas verificações")
        for position, recommendation in enumerate(result["recommendations"], 1):
            st.write(f"{position}. {recommendation}")
        st.info(result["decisionSupportNotice"])
        st.caption(f"{result['model']} · {result['status']}")
    first, second, third = st.columns(3)
    if first.button("Salvar nesta sessão", use_container_width=True):
        save_case(result)
        st.success("Caso salvo durante esta sessão.")
    second.download_button(
        "Exportar JSON",
        data=json_document(result),
        file_name=f"{result['id']}.json",
        mime="application/json",
        use_container_width=True
    )
    third.download_button(
        "Baixar relatório",
        data=html_report(result),
        file_name=f"{result['id']}.html",
        mime="text/html",
        use_container_width=True
    )


def analysis_page() -> None:
    page_header(
        "Fluxo orientado",
        "Nova análise de sinal",
        "Utilize somente códigos anonimizados e revise a qualidade da aquisição antes de gerar a pré-análise."
    )
    main, side = st.columns([2.25, 1], gap="large")
    quality = None
    with main:
        with st.container(border=True):
            st.subheader("1. Modalidade do exame")
            identifiers = list(MODALITIES)
            selected = st.selectbox(
                "Tipo de sinal",
                options=identifiers,
                index=identifiers.index(st.session_state.modality),
                format_func=lambda item: f"{MODALITIES[item]['name']} · {MODALITIES[item]['target']}"
            )
            if selected != st.session_state.modality:
                select_modality(selected)
                st.rerun()
        with st.container(border=True):
            st.subheader("2. Sinal fisiológico")
            uploaded = st.file_uploader("Selecione um arquivo CSV, TXT ou JSON", type=["csv", "txt", "json"])
            if uploaded is not None:
                try:
                    load_uploaded_signal(uploaded)
                except (ValueError, UnicodeDecodeError, pd.errors.ParserError) as exception:
                    st.error(str(exception))
            if st.button("Usar amostra demonstrativa", use_container_width=True):
                select_modality(st.session_state.modality, True)
                st.rerun()
            values = st.session_state.signal
            if values is not None:
                st.caption(f"{st.session_state.file_name} · {values.size:,} amostras".replace(",", "."))
                st.session_state.sample_rate = st.number_input(
                    "Frequência de amostragem em Hz",
                    min_value=20,
                    max_value=20_000,
                    value=int(st.session_state.sample_rate),
                    step=1
                )
                metadata = MODALITIES[st.session_state.modality]
                try:
                    prepared, quality = signal_quality()
                    st.line_chart(compact_signal(prepared.filtered), height=250)
                    first, second, third = st.columns(3)
                    first.metric("Canal", metadata["channel"])
                    second.metric("Duração", f"{quality['duration']:.2f} s")
                    third.metric("Unidade", metadata["unit"])
                except ValueError as exception:
                    st.error(str(exception))
        with st.container(border=True):
            st.subheader("3. Contexto para revisão")
            st.caption("Não informe nome, CPF, prontuário, telefone ou endereço.")
            st.session_state.record_code = st.text_input("Código anonimizado do caso", value=st.session_state.record_code, max_chars=64)
            st.session_state.symptoms = st.multiselect("Sinais e sintomas relatados", SYMPTOMS, default=st.session_state.symptoms)
            st.session_state.notes = st.text_area(
                "Observações clínicas desidentificadas",
                value=st.session_state.notes,
                max_chars=4000,
                height=110
            )
            consent = st.checkbox("Utilizarei o resultado somente para ensino ou pesquisa, com revisão de profissional habilitado.")
            insufficient = quality is None or quality["quality"] < 60
            if quality is not None and quality["quality"] < 60:
                st.warning("A qualidade é insuficiente para prosseguir. Revise a aquisição ou envie outro sinal.")
            if st.button(
                "Gerar pré-análise",
                type="primary",
                use_container_width=True,
                disabled=insufficient or not consent
            ):
                try:
                    request = AnalyzeRequest(
                        modality=st.session_state.modality,
                        samples=st.session_state.signal.tolist(),
                        sample_rate=int(st.session_state.sample_rate),
                        record_code=st.session_state.record_code,
                        symptoms=st.session_state.symptoms,
                        notes=st.session_state.notes
                    )
                    response = analyzer().analyze(request)
                    st.session_state.result = response.model_dump(mode="json", by_alias=True)
                except (ValueError, LookupError) as exception:
                    st.error(str(exception))
    with side:
        quality_panel(quality)
        with st.container(border=True):
            st.subheader("Modalidade selecionada")
            metadata = MODALITIES[st.session_state.modality]
            st.write(f"**{metadata['name']}**")
            st.caption(metadata["full_name"])
            st.write(metadata["target"])
            st.caption(f"Referência de amostragem: {metadata['sample_rate']} Hz")
        with st.container(border=True):
            st.subheader("Uso responsável")
            st.write("A saída organiza evidências para discussão acadêmica e não substitui avaliação clínica.")
    if st.session_state.result:
        analysis_result(st.session_state.result)


def cases_page() -> None:
    page_header(
        "Registro desta sessão",
        "Casos analisados",
        "Os casos permanecem apenas na memória desta sessão e devem utilizar códigos desidentificados."
    )
    action, count = st.columns([1, 4])
    if action.button("Limpar histórico", disabled=not st.session_state.history, use_container_width=True):
        st.session_state.history = []
        st.rerun()
    count.write(f"{len(st.session_state.history)} caso(s) salvo(s) nesta sessão")
    if not st.session_state.history:
        st.info("Nenhum caso foi salvo nesta sessão.")
        return
    for result in st.session_state.history:
        with st.container(border=True):
            top, probability, quality = st.columns([2, 1, 1])
            top.markdown(f"<div class=\"case-title\">{result['recordCode']} · {result['modalityName']}</div>", unsafe_allow_html=True)
            top.caption(result["primaryFinding"])
            probability.metric("Probabilidade" if result.get("probabilityMode") == "calibrated_research" else "Escore", f"{result['confidence']}%")
            quality.metric("Qualidade", f"{result['inspection']['quality']}%")
            left, right = st.columns(2)
            left.download_button(
                "Exportar JSON",
                data=json_document(result),
                file_name=f"{result['id']}.json",
                mime="application/json",
                key=f"json-{result['id']}",
                use_container_width=True
            )
            right.download_button(
                "Baixar relatório",
                data=html_report(result),
                file_name=f"{result['id']}.html",
                mime="text/html",
                key=f"html-{result['id']}",
                use_container_width=True
            )


user = access_screen()
initialize_state()

with st.sidebar:
    st.markdown('<div class="brand"><strong>PET-Saúde</strong><span>Sinais clínicos 3.0 · UCPel</span></div>', unsafe_allow_html=True)
    st.caption(f"Acesso: {user['email']}")
    st.radio("Navegação", ["Visão geral", "Nova análise", "Casos analisados"], key="view")
    st.markdown("---")
    st.caption("Aplicação acadêmica para análise exploratória de sinais fisiológicos.")
    if not user["local"] and st.button("Sair", use_container_width=True):
        st.logout()


if st.session_state.view == "Visão geral":
    overview_page()
elif st.session_state.view == "Nova análise":
    analysis_page()
else:
    cases_page()

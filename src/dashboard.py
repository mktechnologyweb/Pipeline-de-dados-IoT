import streamlit as st
import pandas as pd
import time
from sqlalchemy import create_engine

st.set_page_config(layout="wide")


#  CSS
st.markdown("""
<style>
.stApp {
    background-color: #0b1220;
    color: white;
}
.metric-card {
    padding: 15px;
    border-radius: 8px;
    background: #111827;
    text-align: center;
    border: 2px solid transparent;
}
.border-blue { border-color: #3b82f6; }
.border-yellow { border-color: #facc15; }
.border-red { border-color: #ef4444; }
.border-purple { border-color: #a855f7; }

.metric-title { font-size: 14px; color: #9ca3af; }
.metric-value { font-size: 28px; font-weight: bold; }

.stButton>button:first-child {
    background-color: #22c55e;
    color: white;
}
.stButton>button:last-child {
    background-color: #1f2937;
    color: white;
}
.stProgress > div > div {
    background-color: #22c55e;
}
</style>
""", unsafe_allow_html=True)


# CONEXÃO

engine = create_engine("postgresql://user:password@localhost:5432/iot_db")

def load_data(view):
    return pd.read_sql(f"SELECT * FROM {view}", engine)


# LOG FIXO

def render_log(logs):
    logs_limitados = logs[-100:]
    return f"""
    <div style="height:180px;overflow-y:auto;background:#020617;padding:10px;border-radius:8px;
    border:1px solid #1f2937;font-family:monospace;font-size:12px;color:#22c55e;">
    {'<br>'.join(logs_limitados)}
    </div>
    """


#  QUALIDADE DE DADOS

def analisar_dados(df):
    resultado = {}
    resultado["nulos"] = df.isnull().sum()
    resultado["duplicados"] = df.duplicated().sum()

    outliers = {}
    for col in df.select_dtypes(include=['float64', 'int64']).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers[col] = df[(df[col] < lower) | (df[col] > upper)].shape[0]

    resultado["outliers"] = outliers
    return resultado


#  ESTADOS

if "executado" not in st.session_state:
    st.session_state.executado = False

if "dados" not in st.session_state:
    st.session_state.dados = None


#  HEADER

st.markdown("Simulador de Pipeline Automatizado")


# BOTÕES

col_btn1, col_btn2 = st.columns(2)

run = col_btn1.button("▶ Executar Agora")
clear = col_btn2.button("🧹 Limpar Log")

progress_bar = st.progress(0)
log_placeholder = st.empty()


# EXECUÇÃO DO CODIGO
if run:
    logs = []

    def add_log(msg):
         logs.append(msg)
         log_placeholder.markdown(render_log(logs), unsafe_allow_html=True)
         time.sleep(0.4)

    progress_bar.progress(5)
    add_log("[INFO] Iniciando pipeline...")

    progress_bar.progress(10)
    add_log("[INFO] Conectando ao banco de dados...")

    progress_bar.progress(20)
    add_log("[INFO] Extraindo dados: temperature_readings")

    df_raw = load_data("temperature_readings")

    progress_bar.progress(40)
    add_log("[INFO] Validando dados...")

    nulos = df_raw.isnull().sum().sum()
    duplicados = df_raw.duplicated().sum()

    add_log(f"[INFO] Nulos encontrados: {nulos}")
    add_log(f"[INFO] Duplicados encontrados: {duplicados}")

    progress_bar.progress(60)
    add_log("[INFO] Calculando outliers...")

# cálculo simples
    outliers_total = 0
    for col in df_raw.select_dtypes(include=['float64', 'int64']).columns:
        Q1 = df_raw[col].quantile(0.25)
        Q3 = df_raw[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers_total += df_raw[(df_raw[col] < Q1 - 1.5*IQR) | (df_raw[col] > Q3 + 1.5*IQR)].shape[0]

    add_log(f"[INFO] Outliers detectados: {outliers_total}")

    progress_bar.progress(80)
    add_log("[INFO] Gerando agregações...")

    df_avg = load_data("avg_temp_por_sala")
    df_hora = load_data("leituras_por_hora")
    df_dia = load_data("temp_max_min_por_dia")

    progress_bar.progress(95)
    add_log("[INFO] Finalizando pipeline...")

    # salvar no estado
    st.session_state.dados = {
        "avg": df_avg,
        "hora": df_hora,
        "dia": df_dia,
        "raw": df_raw,
}

    st.session_state.executado = True

    progress_bar.progress(100)
    add_log("[SUCCESS] Pipeline executado com sucesso!")
    log_placeholder.markdown(render_log(logs), unsafe_allow_html=True)


#  RESET

if clear:
    st.session_state.executado = False
    st.session_state.dados = None
    progress_bar.progress(0)
    log_placeholder.empty()


#  DASHBOARD

if st.session_state.executado:

    dados = st.session_state.dados
    df_raw = dados["raw"]

    analise = analisar_dados(df_raw)

    total_nulos = int(analise["nulos"].sum())
    total_duplicados = int(analise["duplicados"])
    total_outliers = int(sum(analise["outliers"].values()))

    qualidade = round(
        100 - ((total_nulos + total_outliers) / len(df_raw)) * 100, 2
    )

    #  KPIs NOVOS
    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"<div class='metric-card border-blue'><div class='metric-title'>Nulos</div><div class='metric-value'>{total_nulos}</div></div>", unsafe_allow_html=True)

    col2.markdown(f"<div class='metric-card border-yellow'><div class='metric-title'>Duplicados</div><div class='metric-value'>{total_duplicados}</div></div>", unsafe_allow_html=True)

    col3.markdown(f"<div class='metric-card border-red'><div class='metric-title'>Outliers</div><div class='metric-value'>{total_outliers}</div></div>", unsafe_allow_html=True)

    col4.markdown(f"<div class='metric-card border-purple'><div class='metric-title'>Qualidade (%)</div><div class='metric-value'>{qualidade}%</div></div>", unsafe_allow_html=True)

    st.divider()

    # GRÁFICOS
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("Média por Sala")
        st.bar_chart(dados["avg"].set_index("sala"))

    with col_g2:
        st.subheader("Leituras por Hora")
        st.line_chart(dados["hora"].set_index("hora"))

    st.subheader("Max e Min por Dia")
    st.line_chart(dados["dia"].set_index("dia"))

else:
    st.info("Clique em ▶ Executar Agora para iniciar o pipeline.")
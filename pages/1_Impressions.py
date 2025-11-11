import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Impressões - Análise SUS",
    page_icon="📊",
    layout="wide"
)

# Carregar CSS
def load_css():
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.markdown("""
<div class="main-header">
    <h1>📊 Impressões Iniciais</h1>
    <p class="subtitle">Análise Exploratória Completa dos Dados</p>
</div>
""", unsafe_allow_html=True)

# Verificar se os dados estão carregados
if "df_original" not in st.session_state or "df_ibge" not in st.session_state:
    st.error("⚠️ Dados não encontrados. Volte à página principal para carregar os dados.")
    st.stop()

df_original = st.session_state.df_original
df_ibge = st.session_state.df_ibge

# Estatísticas completas dos datasets
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="custom-table">
        <h3>📊 Estatísticas do Dataset SUS</h3>
        <p><strong>Forma do dataset:</strong> {df_original.shape[0]} linhas × {df_original.shape[1]} colunas</p>
        <p><strong>Valores nulos:</strong> {df_original.isnull().sum().sum()} no total</p>
        <p><strong>Tipos de dados:</strong></p>
        <ul>
            <li>ID: {df_original['ID'].dtype} (Valores únicos: {df_original['ID'].nunique()})</li>
            <li>MUNICÍPIO: {df_original['MUNICÍPIO'].dtype} (Valores únicos: {df_original['MUNICÍPIO'].nunique()})</li>
            <li>PRIMEIRO_NOME: {df_original['PRIMEIRO_NOME'].dtype} (Valores únicos: {df_original['PRIMEIRO_NOME'].nunique()})</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="custom-table">
        <h3>🏙️ Estatísticas do Dataset IBGE</h3>
        <p><strong>Forma do dataset:</strong> {df_ibge.shape[0]} linhas × {df_ibge.shape[1]} colunas</p>
        <p><strong>Valores nulos:</strong> {df_ibge.isnull().sum().sum()} no total</p>
        <p><strong>Tipos de dados:</strong></p>
        <ul>
            <li>Municípios: {df_ibge.iloc[:, 0].dtype} (Valores únicos: {df_ibge.iloc[:, 0].nunique()})</li>
            <li>Código municipal: {df_ibge.iloc[:, 1].dtype}</li>
            <li>UF: {df_ibge['UF'].dtype} (Valores únicos: {df_ibge['UF'].nunique()})</li>
            <li>pessoas: {df_ibge['pessoas'].dtype if 'pessoas' in df_ibge.columns else 'N/A'}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Seção de dados analisados
with st.expander("🔍 Visualização Completa dos Dados", expanded=True):
    tab1, tab2 = st.tabs(["📋 Dados SUS Completos", "🏙️ Dados IBGE Completos"])
    
    with tab1:
        st.markdown("### Dataset Completo - Atendimentos SUS")
        st.dataframe(df_original, use_container_width=True, height=600)
        
        # Estatísticas descritivas
        st.markdown("#### Estatísticas Descritivas")
        st.dataframe(df_original.describe(include='all'), use_container_width=True)
    
    with tab2:
        st.markdown("### Dataset Completo - IBGE")
        st.dataframe(df_ibge, use_container_width=True, height=600)
        
        # Estatísticas descritivas
        if 'pessoas' in df_ibge.columns:
            st.markdown("#### Estatísticas Populacionais")
            st.dataframe(df_ibge['pessoas'].describe(), use_container_width=True)

# Informações detalhadas dos datasets
st.markdown('<div class="metric-container">', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">🏥 Atendimentos SUS</div>
        <div class="metric-value">{df_original.shape[0]:,}</div>
        <div class="metric-desc">Registros totais</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">🏙️ Municípios IBGE</div>
        <div class="metric-value">{df_ibge.shape[0]:,}</div>
        <div class="metric-desc">Registros totais</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">👤 Nomes Únicos</div>
        <div class="metric-value">{df_original['PRIMEIRO_NOME'].nunique():,}</div>
        <div class="metric-desc">Primeiros nomes</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    estados_ne = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
    ufs_ne = df_ibge[df_ibge['UF'].isin(estados_ne)]['UF'].nunique()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">📍 UFs Nordeste</div>
        <div class="metric-value">{ufs_ne}</div>
        <div class="metric-desc">Estados na região</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Informações dos datasets
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="custom-table">
    <h3>📋 Estrutura dos Atendimentos SUS</h3>
    <table>
        <tr><th>Coluna</th><th>Tipo</th><th>Descrição</th></tr>
        <tr><td>ID</td><td>Numérico</td><td>Identificador único de cada atendimento</td></tr>
        <tr><td>MUNICÍPIO</td><td>Texto</td><td>Nome do município onde ocorreu o atendimento</td></tr>
        <tr><td>PRIMEIRO_NOME</td><td>Texto</td><td>Primeiro nome do paciente atendido</td></tr>
    </table>
    <div style="margin-top: 1.5rem;">
        <span class="badge">Registros: {df_original.shape[0]:,}</span>
        <span class="badge">Colunas: {df_original.shape[1]}</span>
        <span class="badge">Municípios únicos: {df_original['MUNICÍPIO'].nunique()}</span>
    </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="custom-table">
    <h3>🏙️ Estrutura dos Dados IBGE</h3>
    <table>
        <tr><th>Coluna</th><th>Tipo</th><th>Descrição</th></tr>
        <tr><td>Municípios</td><td>Texto</td><td>Nome completo do município</td></tr>
        <tr><td>Código municipal</td><td>Numérico</td><td>Código IBGE do município</td></tr>
        <tr><td>UF</td><td>Texto</td><td>Sigla da Unidade Federativa</td></tr>
        <tr><td>pessoas</td><td>Numérico</td><td>População residente (Censo 2022)</td></tr>
    </table>
    <div style="margin-top: 1.5rem;">
        <span class="badge">Registros: {df_ibge.shape[0]:,}</span>
        <span class="badge">Colunas: {df_ibge.shape[1]}</span>
        <span class="badge">UFs únicas: {df_ibge['UF'].nunique()}</span>
    </div>
    </div>
    """, unsafe_allow_html=True)

# Observações detalhadas
st.markdown(f"""
<div class="custom-table">
<h3>🔍 Observações e Insights dos Datasets</h3>

<h4>📊 Características dos Dados de Atendimento SUS:</h4>
<ul>
    <li><strong>🕒 Temporalidade:</strong> Não há informações sobre datas dos atendimentos</li>
    <li><strong>👥 Identificação:</strong> Dados anonimizados - apenas primeiro nome dos pacientes</li>
    <li><strong>🌍 Abrangência:</strong> Foco na região Nordeste do Brasil</li>
    <li><strong>📈 Volume:</strong> {df_original.shape[0]:,} registros representam uma amostra significativa</li>
</ul>

<h4>🏛️ Características dos Dados IBGE:</h4>
<ul>
    <li><strong>📅 Atualidade:</strong> Dados do Censo Demográfico 2022</li>
    <li><strong>🎯 Precisão:</strong> Informações oficiais do Instituto Brasileiro de Geografia e Estatística</li>
    <li><strong>📊 Métrica:</strong> População residente por município</li>
</ul>

<h4>⚠️ Considerações para Análise:</h4>
<ul>
    <li><strong>🔗 Relacionamento:</strong> Os datasets podem ser unidos pela coluna de municípios</li>
    <li><strong>🧹 Qualidade:</strong> {df_original[df_original.isnull().any(axis=1)].shape[0]} registros com valores nulos no dataset SUS</li>
    <li><strong>🎯 Foco Geográfico:</strong> Análise concentrada nos 9 estados do Nordeste</li>
    <li><strong>📋 Pré-processamento:</strong> Foram removidas colunas não essenciais para análise agregada</li>
</ul>

<h4>🎯 Objetivos da Análise:</h4>
<ul>
    <li>Identificar padrões de atendimento por região</li>
    <li>Correlacionar volume de atendimentos com população municipal</li>
    <li>Analisar distribuição geográfica dos serviços de saúde</li>
    <li>Identificar possíveis disparidades regionais</li>
</ul>
</div>
""", unsafe_allow_html=True)
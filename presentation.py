import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Análise SUS - Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar CSS personalizado
def load_css():
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Título principal com estilo
st.markdown("""
<div class="main-header">
    <h1>🏥 Projeto de Análise de Dados - SUS</h1>
    <p class="subtitle">Análise Enriquecida de Atendimentos SUS com Informações Municipais</p>
</div>
""", unsafe_allow_html=True)

# Seção da equipe com cards
st.markdown("""
<div class="team-section">
    <h2>👥 Nossa Equipe</h2>
    <div class="team-grid">
        <div class="team-card">
            <div class="team-member">Alexandre Henrique</div>
            <div class="team-id">2210375</div>
        </div>
        <div class="team-card">
            <div class="team-member">Alexandre Pinto Franco</div>
            <div class="team-id">2214674</div>
        </div>
        <div class="team-card">
            <div class="team-member">Felipe Pascoal</div>
            <div class="team-id">2214671</div>
        </div>
        <div class="team-card">
            <div class="team-member">Natan Coelho Pucci Benevides</div>
            <div class="team-id">2111126</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Carregar dados na session state
if "df_original" not in st.session_state:
    try:
        st.session_state.df_original = pd.read_csv('./data/DADOS.txt')
        st.success("✅ Dados de atendimentos SUS carregados com sucesso!")
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados de atendimentos: {e}")

if "df_ibge" not in st.session_state:
    try:
        st.session_state.df_ibge = pd.read_csv(
            './data/populacao_municipios/Censo 2022 - População residente - Municípios.csv', 
            sep=';'
        )
        st.success("✅ Dados do IBGE carregados com sucesso!")
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados do IBGE: {e}")

# Resumo dos dados
st.markdown('<div class="metric-container">', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

if "df_original" in st.session_state:
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">📋 Total de Atendimentos</div>
            <div class="metric-value">{st.session_state.df_original.shape[0]:,}</div>
            <div class="metric-desc">Registros do SUS</div>
        </div>
        """, unsafe_allow_html=True)

if "df_ibge" in st.session_state:
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">🏙️ Municípios no IBGE</div>
            <div class="metric-value">{st.session_state.df_ibge.shape[0]:,}</div>
            <div class="metric-desc">Registros municipais</div>
        </div>
        """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">🎯 Região Foco</div>
        <div class="metric-value">Nordeste</div>
        <div class="metric-desc">9 estados analisados</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Navegação entre páginas
st.markdown("""
<div class="navigation-section">
    <h2>📊 Navegação do Projeto</h2>
    <div class="nav-cards">
        <div class="nav-card" onclick="window.parent.document.querySelector('[data-testid=\"stSidebarNav\"]').querySelector('a[href*=\"1_Impressions\"]').click()">
            <h3>📊 Impressões Iniciais</h3>
            <p>Primeira análise exploratória dos dados e visão geral completa dos datasets</p>
        </div>
        <div class="nav-card" onclick="window.parent.document.querySelector('[data-testid=\"stSidebarNav\"]').querySelector('a[href*=\"2_Analysys\"]').click()">
            <h3>📈 Análises Interativas</h3>
            <p>Gráficos dinâmicos, filtros avançados e visualizações interativas dos dados</p>
        </div>
        <div class="nav-card" onclick="window.parent.document.querySelector('[data-testid=\"stSidebarNav\"]').querySelector('a[href*=\"3_BI_Maps\"]').click()">
            <h3>🗺️ BI e Mapas</h3>
            <p>Análises avançadas de BI, mapas interativos e relatórios executivos</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Análise Rápida dos Dados
if "df_original" in st.session_state and "df_ibge" in st.session_state:
    st.markdown("""
    <div class="custom-table">
        <h3>🚀 Análise Rápida dos Dados</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="custom-table">
            <h4>📋 Dataset de Atendimentos SUS</h4>
            <p><strong>Dimensões:</strong> {st.session_state.df_original.shape[0]} linhas × {st.session_state.df_original.shape[1]} colunas</p>
            <p><strong>Colunas:</strong> {', '.join(st.session_state.df_original.columns)}</p>
            <p><strong>Tipos de dados:</strong></p>
            <ul>
                <li>ID: Identificador único</li>
                <li>MUNICÍPIO: Dados categóricos</li>
                <li>PRIMEIRO_NOME: Dados textuais</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="custom-table">
            <h4>🏙️ Dataset do IBGE</h4>
            <p><strong>Dimensões:</strong> {st.session_state.df_ibge.shape[0]} linhas × {st.session_state.df_ibge.shape[1]} colunas</p>
            <p><strong>Colunas:</strong> {', '.join(st.session_state.df_ibge.columns)}</p>
            <p><strong>Tipos de dados:</strong></p>
            <ul>
                <li>Municípios: Nomes dos municípios</li>
                <li>Código municipal: Identificadores</li>
                <li>UF: Unidades federativas</li>
                <li>pessoas: Dados populacionais numéricos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(
    page_title="BI e Mapas - Análise SUS",
    page_icon="🗺️",
    layout="wide"
)

# Carregar CSS
def load_css():
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.markdown("""
<div class="main-header">
    <h1>📈 Business Intelligence & Mapas Interativos</h1>
    <p class="subtitle">Análises Avançadas e Visualizações Geográficas</p>
</div>
""", unsafe_allow_html=True)

# Verificar se os dados estão carregados
if "df_original" not in st.session_state or "df_ibge" not in st.session_state:
    st.error("⚠️ Dados não encontrados. Volte à página principal para carregar os dados.")
    st.stop()

# Preparar dados
df_original = st.session_state.df_original.copy()
df_ibge = st.session_state.df_ibge.copy()

# Limpar e padronizar dados
df_original['MUNICÍPIO'] = df_original['MUNICÍPIO'].str.strip().str.upper()
df_ibge['Municípios'] = df_ibge['Municípios'].str.strip().str.upper()

# Filtrar apenas Nordeste
estados_ne = ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]
df_ibge_ne = df_ibge[df_ibge['UF'].isin(estados_ne)].copy()
df_ibge_ne = df_ibge_ne.rename(columns={'Municípios': 'MUNICÍPIO'})

# Fazer merge dos dados
df_merged = df_ibge_ne.merge(
    df_original.groupby('MUNICÍPIO').size().reset_index(name='TOTAL_ATENDIMENTOS'),
    on='MUNICÍPIO',
    how='inner'
)

# Sidebar com filtros
with st.sidebar:
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
        <h3>🎛️ Filtros de Análise</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtro por UF
    ufs_disponiveis = sorted(df_merged['UF'].unique())
    ufs_selecionadas = st.multiselect(
        "Selecione as UFs:",
        options=ufs_disponiveis,
        default=ufs_disponiveis
    )
    
    # Filtro por faixa populacional
    if 'pessoas' in df_merged.columns:
        min_pop = int(df_merged['pessoas'].min())
        max_pop = int(df_merged['pessoas'].max())
        pop_range = st.slider(
            "Faixa populacional:",
            min_value=min_pop,
            max_value=max_pop,
            value=(min_pop, max_pop),
            step=1000
        )
    
    # Aplicar filtros
    df_filtrado = df_merged[df_merged['UF'].isin(ufs_selecionadas)]
    if 'pessoas' in df_filtrado.columns:
        df_filtrado = df_filtrado[
            (df_filtrado['pessoas'] >= pop_range[0]) & 
            (df_filtrado['pessoas'] <= pop_range[1])
        ]

# Métricas principais
st.markdown('<div class="metric-container">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_atendimentos = df_filtrado['TOTAL_ATENDIMENTOS'].sum()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">🏥 Total de Atendimentos</div>
        <div class="metric-value">{total_atendimentos:,}</div>
        <div class="metric-desc">Registros filtrados</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    municipios_ativos = df_filtrado.shape[0]
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">🏙️ Municípios Ativos</div>
        <div class="metric-value">{municipios_ativos}</div>
        <div class="metric-desc">Com atendimentos</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if 'pessoas' in df_filtrado.columns:
        populacao_total = df_filtrado['pessoas'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">👥 População Total</div>
            <div class="metric-value">{populacao_total:,}</div>
            <div class="metric-desc">Habitantes</div>
        </div>
        """, unsafe_allow_html=True)

with col4:
    if 'pessoas' in df_filtrado.columns and populacao_total > 0:
        taxa_100k = (total_atendimentos / populacao_total) * 100000
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">📊 Taxa Geral</div>
            <div class="metric-value">{taxa_100k:.1f}</div>
            <div class="metric-desc">Atend./100k hab.</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 1. VOLUME DE ATENDIMENTOS POR REGIÃO E MUNICÍPIO
st.markdown("""
<div class="custom-table">
    <h2>📊 Volume de Atendimentos por Região e Município</h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Volume por UF
    volume_uf = df_filtrado.groupby('UF').agg({
        'TOTAL_ATENDIMENTOS': 'sum',
        'pessoas': 'sum'
    }).reset_index()
    
    fig_uf = px.bar(
        volume_uf,
        x='UF',
        y='TOTAL_ATENDIMENTOS',
        title='📈 Volume de Atendimentos por Estado',
        color='UF',
        text='TOTAL_ATENDIMENTOS',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_uf.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig_uf.update_layout(
        xaxis_title='Estado',
        yaxis_title='Total de Atendimentos',
        showlegend=False
    )
    st.plotly_chart(fig_uf, use_container_width=True)

with col2:
    # Top 15 municípios por volume
    top_municipios = df_filtrado.nlargest(15, 'TOTAL_ATENDIMENTOS')
    
    fig_municipios = px.bar(
        top_municipios,
        x='TOTAL_ATENDIMENTOS',
        y='MUNICÍPIO',
        orientation='h',
        title='🏆 Top 15 Municípios - Volume de Atendimentos',
        color='TOTAL_ATENDIMENTOS',
        color_continuous_scale='Viridis',
        text='TOTAL_ATENDIMENTOS'
    )
    fig_municipios.update_traces(texttemplate='%{text:,}', textposition='outside')
    fig_municipios.update_layout(
        xaxis_title='Total de Atendimentos',
        yaxis_title='Município',
        yaxis={'categoryorder': 'total ascending'}
    )
    st.plotly_chart(fig_municipios, use_container_width=True)

# 2. PROPORÇÃO POR 100 MIL HABITANTES
st.markdown("""
<div class="custom-table">
    <h2>📈 Proporção de Atendimentos por 100 mil Habitantes</h2>
</div>
""", unsafe_allow_html=True)

if 'pessoas' in df_filtrado.columns:
    # Calcular taxa por 100k habitantes
    df_filtrado['TAXA_100K'] = (df_filtrado['TOTAL_ATENDIMENTOS'] / df_filtrado['pessoas']) * 100000
    df_filtrado['TAXA_100K'] = df_filtrado['TAXA_100K'].round(2)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Taxa por UF
        taxa_uf = df_filtrado.groupby('UF').agg({
            'TAXA_100K': 'mean',
            'pessoas': 'sum',
            'TOTAL_ATENDIMENTOS': 'sum'
        }).reset_index()
        
        fig_taxa_uf = px.bar(
            taxa_uf,
            x='UF',
            y='TAXA_100K',
            title='📊 Taxa Média de Atendimentos por 100k hab. - por Estado',
            color='TAXA_100K',
            color_continuous_scale='Blues',
            text='TAXA_100K'
        )
        fig_taxa_uf.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_taxa_uf.update_layout(
            xaxis_title='Estado',
            yaxis_title='Atendimentos por 100k habitantes'
        )
        st.plotly_chart(fig_taxa_uf, use_container_width=True)
    
    with col2:
        # Distribuição da taxa
        fig_distribuicao = px.box(
            df_filtrado,
            x='TAXA_100K',
            title='📋 Distribuição da Taxa de Atendimentos por 100k hab.',
            orientation='h'
        )
        fig_distribuicao.update_layout(xaxis_title='Atendimentos por 100k habitantes')
        st.plotly_chart(fig_distribuicao, use_container_width=True)

# 3. RANKING DE MUNICÍPIOS
st.markdown("""
<div class="custom-table">
    <h2>🏆 Ranking de Municípios - Volume Proporcional</h2>
</div>
""", unsafe_allow_html=True)

if 'pessoas' in df_filtrado.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 maiores taxas
        top_maiores = df_filtrado.nlargest(10, 'TAXA_100K')[['MUNICÍPIO', 'UF', 'TAXA_100K', 'TOTAL_ATENDIMENTOS', 'pessoas']]
        
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
            <h4>🥇 Maiores Taxas (por 100k hab.)</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Formatar a tabela
        top_maiores_display = top_maiores.copy()
        top_maiores_display['TAXA_100K'] = top_maiores_display['TAXA_100K'].apply(lambda x: f"{x:,.1f}")
        top_maiores_display['pessoas'] = top_maiores_display['pessoas'].apply(lambda x: f"{x:,.0f}")
        top_maiores_display['TOTAL_ATENDIMENTOS'] = top_maiores_display['TOTAL_ATENDIMENTOS'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(
            top_maiores_display,
            column_config={
                "MUNICÍPIO": "Município",
                "UF": "UF",
                "TAXA_100K": "Taxa/100k",
                "TOTAL_ATENDIMENTOS": "Atendimentos",
                "pessoas": "População"
            },
            use_container_width=True
        )
    
    with col2:
        # Top 10 menores taxas
        top_menores = df_filtrado.nsmallest(10, 'TAXA_100K')[['MUNICÍPIO', 'UF', 'TAXA_100K', 'TOTAL_ATENDIMENTOS', 'pessoas']]
        
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
            <h4>📉 Menores Taxas (por 100k hab.)</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Formatar a tabela
        top_menores_display = top_menores.copy()
        top_menores_display['TAXA_100K'] = top_menores_display['TAXA_100K'].apply(lambda x: f"{x:,.1f}")
        top_menores_display['pessoas'] = top_menores_display['pessoas'].apply(lambda x: f"{x:,.0f}")
        top_menores_display['TOTAL_ATENDIMENTOS'] = top_menores_display['TOTAL_ATENDIMENTOS'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(
            top_menores_display,
            column_config={
                "MUNICÍPIO": "Município",
                "UF": "UF",
                "TAXA_100K": "Taxa/100k",
                "TOTAL_ATENDIMENTOS": "Atendimentos",
                "pessoas": "População"
            },
            use_container_width=True
        )

# 4. MAPA INTERATIVO
st.markdown("""
<div class="custom-table">
    <h2>🗺️ Mapa Interativo - Atendimentos SUS</h2>
</div>
""", unsafe_allow_html=True)

# Criar coordenadas aproximadas para os estados do Nordeste (para demonstração)
coordenadas_estados = {
    'MA': {'lat': -4.9609, 'lon': -45.2744, 'nome': 'Maranhão'},
    'PI': {'lat': -8.2377, 'lon': -43.1001, 'nome': 'Piauí'},
    'CE': {'lat': -5.4984, 'lon': -39.3206, 'nome': 'Ceará'},
    'RN': {'lat': -5.4026, 'lon': -36.9541, 'nome': 'Rio Grande do Norte'},
    'PB': {'lat': -7.2400, 'lon': -36.7810, 'nome': 'Paraíba'},
    'PE': {'lat': -8.8137, 'lon': -36.9541, 'nome': 'Pernambuco'},
    'AL': {'lat': -9.5713, 'lon': -36.7820, 'nome': 'Alagoas'},
    'SE': {'lat': -10.5741, 'lon': -37.3857, 'nome': 'Sergipe'},
    'BA': {'lat': -12.5797, 'lon': -41.7007, 'nome': 'Bahia'}
}

# Preparar dados para o mapa
dados_mapa = df_filtrado.groupby('UF').agg({
    'TOTAL_ATENDIMENTOS': 'sum',
    'pessoas': 'sum',
    'MUNICÍPIO': 'count'
}).reset_index()
dados_mapa = dados_mapa.rename(columns={'MUNICÍPIO': 'QTD_MUNICIPIOS'})

# Adicionar coordenadas e calcular taxa
dados_mapa['lat'] = dados_mapa['UF'].map(lambda x: coordenadas_estados.get(x, {}).get('lat', 0))
dados_mapa['lon'] = dados_mapa['UF'].map(lambda x: coordenadas_estados.get(x, {}).get('lon', 0))
dados_mapa['TAXA_100K'] = (dados_mapa['TOTAL_ATENDIMENTOS'] / dados_mapa['pessoas']) * 100000
dados_mapa['TAXA_100K'] = dados_mapa['TAXA_100K'].round(2)

# Criar mapa
col1, col2 = st.columns(2)

with col1:
    # Mapa de calor por volume
    fig_mapa_volume = px.scatter_mapbox(
        dados_mapa,
        lat="lat",
        lon="lon",
        size="TOTAL_ATENDIMENTOS",
        color="TOTAL_ATENDIMENTOS",
        hover_name="UF",
        hover_data={
            "TOTAL_ATENDIMENTOS": True,
            "QTD_MUNICIPIOS": True,
            "TAXA_100K": True,
            "lat": False,
            "lon": False
        },
        size_max=30,
        zoom=4,
        title="🗺️ Mapa de Calor - Volume de Atendimentos por Estado",
        color_continuous_scale="Viridis",
        mapbox_style="carto-positron"
    )
    fig_mapa_volume.update_layout(height=500)
    st.plotly_chart(fig_mapa_volume, use_container_width=True)

with col2:
    # Mapa por taxa
    fig_mapa_taxa = px.scatter_mapbox(
        dados_mapa,
        lat="lat",
        lon="lon",
        size="TAXA_100K",
        color="TAXA_100K",
        hover_name="UF",
        hover_data={
            "TOTAL_ATENDIMENTOS": True,
            "QTD_MUNICIPIOS": True,
            "TAXA_100K": True,
            "lat": False,
            "lon": False
        },
        size_max=30,
        zoom=4,
        title="📊 Mapa - Taxa de Atendimentos por 100k hab.",
        color_continuous_scale="Blues",
        mapbox_style="carto-positron"
    )
    fig_mapa_taxa.update_layout(height=500)
    st.plotly_chart(fig_mapa_taxa, use_container_width=True)
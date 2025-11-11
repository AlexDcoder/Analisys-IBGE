import pandas as pd
import streamlit as st
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Análises - Análise SUS", 
    page_icon="📈",
    layout="wide"
)

# Carregar CSS
def load_css():
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.title('📊 Análises Interativas')

# --- Preparação dos dados ---
df_filtered = st.session_state.df_original[['MUNICÍPIO', 'PRIMEIRO_NOME']].copy()
df_filtered.dropna(subset=['PRIMEIRO_NOME'], inplace=True)
df_filtered['MUNICÍPIO'] = df_filtered['MUNICÍPIO'].apply(lambda x: x.strip())
df_filtered['PRIMEIRO_NOME'] = df_filtered['PRIMEIRO_NOME'].apply(
    lambda x: ' '.join([w for w in x.strip().split() if len(w) >= 3])
)

# Cria df_nordeste se ainda não existir
if "df_nordeste" not in st.session_state:
    st.session_state.df_nordeste = st.session_state.df_ibge.query(
        'UF in ["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"]'
    )
    st.session_state.df_nordeste['Municípios'] = st.session_state.df_nordeste['Municípios'].apply(lambda x: x.strip().upper())
    st.session_state.df_nordeste = st.session_state.df_nordeste.rename(columns={'Municípios': 'MUNICÍPIO'})

# Merge entre os dados
if 'df_merged' not in st.session_state:
    st.session_state.df_merged = st.session_state.df_nordeste.merge(df_filtered, how='inner', on='MUNICÍPIO')

df_merged = st.session_state.df_merged

df_pessoas_municipio = df_merged.groupby('MUNICÍPIO')['pessoas'].sum().reset_index()
df_pessoas_atendimentos = df_merged.groupby('MUNICÍPIO')['PRIMEIRO_NOME'].count().reset_index().rename(columns={'PRIMEIRO_NOME': 'VOLUME_ATENDIMENTOS'})
df_total = df_pessoas_municipio.merge(df_pessoas_atendimentos, how='inner', on='MUNICÍPIO')
df_total['DISCREPANCIA'] = df_total['pessoas'] < df_total['VOLUME_ATENDIMENTOS']

# Total de municípios com atendimentos maior que o volume de pessoas
# --- 🎛️ Filtros interativos ---
with st.sidebar.form("filtro_form"):
    st.markdown("### 🔍 Filtros")

    # Filtro por UF
    ufs = sorted(df_merged['UF'].unique())
    uf_selecionadas = st.multiselect("Selecione as UFs:", options=ufs, default=ufs)

    # Filtro por Município (dependente das UFs)
    municipios = sorted(df_merged.query("UF in @uf_selecionadas")['MUNICÍPIO'].unique())
    municipios_selecionados = st.multiselect("Selecione os Municípios:", options=municipios, default=municipios)

    # Botão para aplicar
    aplicar = st.form_submit_button("Aplicar Filtros")

# --- Aplicação dos filtros ---
if aplicar or (len(uf_selecionadas) < len(ufs)) or (len(municipios_selecionados) < len(municipios)):
    df_filtrado = df_merged.query("UF in @uf_selecionadas and MUNICÍPIO in @municipios_selecionados")
else:
    df_filtrado = df_merged.copy()

# --- 📈 Cálculos e gráficos ---
atendimentos_por_municipio = df_filtrado.groupby(
    ['UF', 'MUNICÍPIO'], as_index=False
).agg({'PRIMEIRO_NOME': 'count'}).rename(columns={'PRIMEIRO_NOME': 'VOLUME_ATENDIMENTOS'})

# Gráfico 1 - Barras por UF
fig_bar = px.bar(
    atendimentos_por_municipio.groupby('UF', as_index=False)['VOLUME_ATENDIMENTOS'].sum(),
    x='UF',
    y='VOLUME_ATENDIMENTOS',
    color='UF',
    text='VOLUME_ATENDIMENTOS',
    title='📈 Volume de Atendimentos por UF (Região)'
)
fig_bar.update_traces(textposition='outside')

# Gráfico 2 - Sunburst
fig_sunburst = px.sunburst(
    atendimentos_por_municipio,
    path=['UF', 'MUNICÍPIO'],
    values='VOLUME_ATENDIMENTOS',
    color='UF',
    color_discrete_sequence=px.colors.qualitative.Pastel,
    title='🗺️ Volume de Atendimentos por UF e Município'
)

# Exibição lado a lado
col1, col2 = st.columns(2)
col1.plotly_chart(fig_bar, use_container_width=True)
col2.plotly_chart(fig_sunburst, use_container_width=True)

# Estatísticas adicionais
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_atendimentos = df_filtrado.shape[0]
    st.metric("Total de Atendimentos", f"{total_atendimentos:,}")

with col2:
    municipios_unicos = df_filtrado['MUNICÍPIO'].nunique()
    st.metric("Municípios com Atendimento", municipios_unicos)

with col3:
    nomes_unicos = df_filtrado['PRIMEIRO_NOME'].nunique()
    st.metric("Nomes Únicos", f"{nomes_unicos:,}")

with col4:
    st.metric("Total de Discrepancias", df_total['DISCREPANCIA'].sum(), help="Total de municípios com atendimentos maior que o volume de pessoas")


# Tabela detalhada
with st.expander("📋 Ver Dados Detalhados"):
    st.dataframe(atendimentos_por_municipio.sort_values('VOLUME_ATENDIMENTOS', ascending=False))
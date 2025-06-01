import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Dashboard de Veículos de Luxo", page_icon="🚗", layout="wide")

# Cor principal para o tema dos gráficos
main_color = '#656d4a'

@st.cache_data
def generate_luxury_car_sales_data():
    np.random.seed(42)
    models = ['Mercedes-Benz S-Class', 'BMW Série 7', 'Audi A8', 'Porsche Cayenne', 'Lexus LS']
    regions = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
    
    sales_data = pd.DataFrame({
        'Modelo': models,
        'Vendas': np.random.randint(50, 500, size=len(models)),
        'Lucro': np.random.uniform(200000, 800000, size=len(models)).round(2),
        'Custo': np.random.uniform(150000, 600000, size=len(models)).round(2)
    })
    
    periods = 16
    dates = pd.date_range(end=datetime.today(), periods=periods, freq='Q')
    time_series = pd.DataFrame({
        'Data': dates,
        'Vendas': np.random.randint(40, 150, size=periods),
        'Clientes': np.random.randint(30, 90, size=periods)
    })
    
    region_data = pd.DataFrame({
        'Região': regions,
        'Vendas': np.random.randint(100, 600, size=len(regions)),
        'Satisfação': np.random.uniform(4.0, 5.0, size=len(regions)).round(2),
        'Lat': [-1.4558, -7.1153, -15.7801, -22.9035, -30.0346],
        'Lon': [-62.8266, -36.6612, -47.9292, -43.2096, -51.2177]
    })
    
    return sales_data, time_series, region_data

sales_data, time_series, region_data = generate_luxury_car_sales_data()

st.title("🚗 Dashboard de Veículos Importados de Luxo - Brasil")

# --------- FILTROS ---------
with st.sidebar:
    st.header("🔎 Filtros")
    modelos_selecionados = st.multiselect(
        "Modelos de veículos", sales_data['Modelo'].unique(), default=sales_data['Modelo'].unique()
    )
    regioes_selecionadas = st.multiselect(
        "Regiões", region_data['Região'].unique(), default=region_data['Região'].unique()
    )
    datas_selecionadas = st.date_input(
        "Período (trimestres)", (time_series['Data'].min(), time_series['Data'].max())
    )
    if len(datas_selecionadas) != 2:
        st.error("Selecione um intervalo de datas válido.")
        st.stop()

# --------- FILTRAGEM ---------
sales_data_filtered = sales_data[sales_data['Modelo'].isin(modelos_selecionados)]
region_data_filtered = region_data[region_data['Região'].isin(regioes_selecionadas)]
start_date, end_date = datas_selecionadas
time_series_filtered = time_series[(time_series['Data'] >= pd.to_datetime(start_date)) & 
                                   (time_series['Data'] <= pd.to_datetime(end_date))]

# --------- TABS ---------
tab1, tab2 = st.tabs(["📊 Análises", "📍 Regiões e Insights"])

# === ABA 1 ===
with tab1:
    st.subheader("📌 Indicadores de Desempenho")
    col1, col2, col3, col4 = st.columns(4)

    total_vendas = sales_data_filtered['Vendas'].sum()
    total_lucro = sales_data_filtered['Lucro'].sum()
    total_custo = sales_data_filtered['Custo'].sum()
    margem_lucro = (total_lucro / total_vendas) if total_vendas > 0 else 0

    col1.metric("Vendas Totais", f"{total_vendas:,}", "+8%")
    col2.metric("Lucro Total", f"R$ {total_lucro:,.2f}", "+5%")
    col3.metric("Custo Total", f"R$ {total_custo:,.2f}", "-3%")
    col4.metric("Margem de Lucro (%)", f"{margem_lucro:.2f}", "+2%")

    st.markdown("### 📈 Distribuição de Desempenho por Modelo")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(sales_data_filtered, names='Modelo', values='Vendas',
                     title="Participação nas Vendas", color_discrete_sequence=px.colors.sequential.Aggrnyl)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(sales_data_filtered, x='Modelo', y=['Vendas', 'Lucro', 'Custo'], barmode='group',
                     title="Comparativo: Vendas, Lucro e Custo")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### ⏳ Evolução Trimestral")
    fig = px.line(time_series_filtered, x='Data', y=['Vendas', 'Clientes'],
                  title="Tendência de Vendas e Novos Clientes",
                  markers=True, color_discrete_sequence=[main_color, "#a3b18a"])
    st.plotly_chart(fig, use_container_width=True)

# === ABA 2 ===
with tab2:
    st.subheader("📍 Desempenho por Região")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(region_data_filtered, x='Região', y='Vendas',
                     title="Vendas por Região", color='Região',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.scatter(region_data_filtered, x='Vendas', y='Satisfação',
                         size='Vendas', color='Região',
                         title="Relação entre Vendas e Satisfação",
                         size_max=60)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🗺️ Mapa Interativo")
    fig = px.scatter_mapbox(
        region_data_filtered,
        lat='Lat', lon='Lon', size='Vendas',
        color='Satisfação', hover_name='Região',
        color_continuous_scale='Viridis', zoom=3.5,
        mapbox_style='carto-positron'
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🤖 Insights Inteligentes")
    if not sales_data_filtered.empty:
        insights = [
            f"✅ O modelo **{sales_data_filtered.loc[sales_data_filtered['Lucro'].idxmax(), 'Modelo']}** possui o maior lucro.",
            f"⭐ A região **{region_data_filtered.loc[region_data_filtered['Satisfação'].idxmax(), 'Região']}** apresenta a melhor satisfação (nota {region_data_filtered['Satisfação'].max()}/5).",
            "📈 Tendência positiva de crescimento anual de aproximadamente 4%.",
            f"⚠️ Modelo mais caro: **{sales_data_filtered.loc[sales_data_filtered['Custo'].idxmax(), 'Modelo']}** (R$ {sales_data_filtered['Custo'].max():,.2f})"
        ]
    else:
        insights = ["🔍 Aplique filtros válidos para gerar insights."]

    for ins in insights:
        st.info(ins)

    st.caption("📅 Atualizado em: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
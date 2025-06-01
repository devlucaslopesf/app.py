import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime

# Cor principal para o tema dos gráficos
main_color = '#656d4a'

# Configuração da página
st.set_page_config(page_title="Dashboard de Veículos de Luxo", page_icon="🚗", layout="wide")

# Gerar dados aleatórios de veículos importados de luxo vendidos no Brasil nos últimos 4 anos
def generate_luxury_car_sales_data():
    np.random.seed(42)
    models = ['Mercedes-Benz S-Class', 'BMW Série 7', 'Audi A8', 'Porsche Cayenne', 'Lexus LS']
    regions = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul']
    
    # Dados por modelo
    sales_data = pd.DataFrame({
        'Modelo': models,
        'Vendas': np.random.randint(50, 500, size=len(models)),
        'Lucro': np.random.uniform(200000, 800000, size=len(models)).round(2),
        'Custo': np.random.uniform(150000, 600000, size=len(models)).round(2)
    })
    
    # Dados temporais (últimos 4 anos, por trimestre)
    periods = 16  # 4 anos * 4 trimestres
    dates = pd.date_range(end=datetime.today(), periods=periods, freq='Q').to_pydatetime().tolist()
    time_series = pd.DataFrame({
        'Data': dates,
        'Vendas': np.random.randint(40, 150, size=periods),
        'Clientes': np.random.randint(30, 90, size=periods)
    })
    
    # Dados por região
    region_data = pd.DataFrame({
        'Região': regions,
        'Vendas': np.random.randint(100, 600, size=len(regions)),
        'Satisfação': np.random.uniform(4.0, 5.0, size=len(regions)).round(2),
        # Latitude e longitude aproximadas das regiões para o mapa
        'Lat': [-1.4558, -7.1153, -15.7801, -22.9035, -30.0346],
        'Lon': [-62.8266, -36.6612, -47.9292, -43.2096, -51.2177]
    })
    
    return sales_data, time_series, region_data

sales_data, time_series, region_data = generate_luxury_car_sales_data()

st.title("🚗 Dashboard de Veículos Importados de Luxo - Brasil (Últimos 4 anos)")

# Criando abas principais
tab1, tab2 = st.tabs(["Vendas, Produtos e Clientes", "Relatórios, Gráficos e Mapas"])

with tab1:
    st.header("Filtros")
    with st.sidebar:
        modelos_selecionados = st.multiselect(
            "Selecione os modelos",
            options=sales_data['Modelo'].unique(),
            default=sales_data['Modelo'].unique()
        )
        
        regioes_selecionadas = st.multiselect(
            "Selecione as regiões",
            options=region_data['Região'].unique(),
            default=region_data['Região'].unique()
        )
        
        data_min = time_series['Data'].min()
        data_max = time_series['Data'].max()
        
        datas_selecionadas = st.date_input(
            "Selecione o intervalo de datas (trimestres)",
            value=(data_min, data_max),
            min_value=data_min,
            max_value=data_max
        )
        if len(datas_selecionadas) != 2:
            st.error("Por favor, selecione um intervalo de datas válido.")
            st.stop()

    # --- FILTRANDO OS DADOS ---
    sales_data_filtered = sales_data[sales_data['Modelo'].isin(modelos_selecionados)]
    region_data_filtered = region_data[region_data['Região'].isin(regioes_selecionadas)]
    start_date, end_date = datas_selecionadas
    time_series_filtered = time_series[(time_series['Data'] >= pd.to_datetime(start_date)) & (time_series['Data'] <= pd.to_datetime(end_date))]

    # --- KPIs ---
    st.subheader("KPIs")
    col1, col2, col3, col4 = st.columns(4)

    total_vendas = sales_data_filtered['Vendas'].sum() if not sales_data_filtered.empty else 0
    total_lucro = sales_data_filtered['Lucro'].sum() if not sales_data_filtered.empty else 0
    total_custo = sales_data_filtered['Custo'].sum() if not sales_data_filtered.empty else 0
    margem_lucro = (total_lucro / total_vendas) if total_vendas > 0 else 0

    col1.metric("Vendas Totais", f"{total_vendas:,}", "+8% vs último ano")
    col2.metric("Lucro Total (R$)", f"R$ {total_lucro:,.2f}", "+5% vs último ano")
    col3.metric("Custo Total (R$)", f"R$ {total_custo:,.2f}", "-3% vs último ano")
    col4.metric("Margem de Lucro (%)", f"{margem_lucro:.2f}", "+2%")

    # --- GRÁFICOS ---
    st.markdown("---")
    st.subheader("Análise por Modelo de Veículo")

    col1, col2 = st.columns(2)

    with col1:
        if not sales_data_filtered.empty:
            fig = px.pie(sales_data_filtered, values='Vendas', names='Modelo', 
                         title='Distribuição de Vendas por Modelo',
                         color_discrete_sequence=[main_color])
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Nenhum dado para os modelos selecionados.")

    with col2:
        if not sales_data_filtered.empty:
            color_seq = [main_color] * 3
            fig = px.bar(sales_data_filtered, x='Modelo', y=['Vendas', 'Lucro', 'Custo'], 
                         title='Comparação de Vendas, Lucro e Custo por Modelo',
                         barmode='group', 
                         color_discrete_sequence=color_seq)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Nenhum dado para os modelos selecionados.")

    st.markdown("---")
    st.subheader("Tendência Temporal de Vendas e Clientes")

    if not time_series_filtered.empty:
        fig = px.line(time_series_filtered, x='Data', y=['Vendas', 'Clientes'], 
                      title='Vendas e Novos Clientes por Trimestre',
                      markers=True,
                      color_discrete_sequence=[main_color, main_color])
        fig.update_xaxes(title_text='Data')
        fig.update_yaxes(title_text='Quantidade')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado para o intervalo de datas selecionado.")

with tab2:
    st.subheader("Desempenho por Região do Brasil")

    region_data_filtered = region_data[region_data['Região'].isin(regioes_selecionadas)]  # Garantir filtro atualizado

    col1, col2 = st.columns(2)

    with col1:
        if not region_data_filtered.empty:
            fig = px.bar(region_data_filtered, x='Região', y='Vendas', 
                         title='Vendas por Região',
                         color='Região',
                         color_discrete_sequence=[main_color]*len(region_data_filtered))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Nenhuma região selecionada.")

    with col2:
        if not region_data_filtered.empty:
            fig = px.scatter(region_data_filtered, x='Vendas', y='Satisfação', 
                             size='Vendas', color='Região',
                             title='Relação entre Vendas e Satisfação do Cliente',
                             hover_name='Região',
                             size_max=60,
                             color_discrete_sequence=[main_color]*len(region_data_filtered))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Nenhuma região selecionada.")

    st.markdown("---")
    st.subheader("Mapa de Vendas por Região")

    if not region_data_filtered.empty:
        fig = px.scatter_mapbox(
            region_data_filtered,
            lat="Lat",
            lon="Lon",
            size="Vendas",
            color="Satisfação",
            hover_name="Região",
            color_continuous_scale=px.colors.sequential.Viridis,
            size_max=50,
            zoom=3.5,
            mapbox_style="carto-positron",
            title="Mapa Interativo de Vendas e Satisfação por Região"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhuma região selecionada para o mapa.")

    # --- INSIGHTS ---
    st.markdown("---")
    st.subheader("Insights Gerados Automaticamente")

    # Recalcular filtros para insights
    sales_data_filtered = sales_data[sales_data['Modelo'].isin(modelos_selecionados)]
    region_data_filtered = region_data[region_data['Região'].isin(regioes_selecionadas)]

    if not sales_data_filtered.empty and not region_data_filtered.empty:
        insights = [
            f"📌 {sales_data_filtered.loc[sales_data_filtered['Lucro'].idxmax(), 'Modelo']} apresenta a maior margem de lucro.",
            f"📌 Região {region_data_filtered.loc[region_data_filtered['Satisfação'].idxmax(), 'Região']} tem o maior índice de satisfação ({region_data_filtered['Satisfação'].max()}/5.0).",
            "📌 Vendas trimestrais estão apresentando crescimento médio de 4% ao ano.",
            f"📌 Custo do modelo {sales_data_filtered.loc[sales_data_filtered['Custo'].idxmax(), 'Modelo']} está 18% acima da média."
        ]
    else:
        insights = ["Selecione dados válidos nos filtros para gerar insights."]

    for insight in insights:
        st.info(insight)

    st.caption("Dados fictícios gerados automaticamente - Atualizado em: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

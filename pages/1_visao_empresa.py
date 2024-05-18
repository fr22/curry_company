# Libraries
from haversine import haversine
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static
#ajustando largura da página
st.set_page_config(
    page_title = 'Visão Empresa',
    layout='wide')



#============================
#=========== funções
#============================
def country_maps(dfb):
    cols = [
    'City',
    'Road_traffic_density',
    'Delivery_location_latitude',
    'Delivery_location_longitude'
    ]
    cols_group = [
    'City',
    'Road_traffic_density'
    ]
    df6= dfb.loc[:, cols].groupby(cols_group).median().reset_index()
    #removendo nan
    df6 = df6[df6['City'] != 'NaN']
    df6 = df6[df6['Road_traffic_density'] != 'NaN']
    #plotando mapa
    map = folium.Map()
    for index, row in df6.iterrows():
        folium.Marker([row['Delivery_location_latitude'
               ],row['Delivery_location_longitude']],
            popup= row[['City', 'Road_traffic_density']]).add_to(map)
    folium_static(map, width=1024, height = 600)

def order_share_by_week(dfb):
    """Faz gráfico de linhas"""
    #pedidos por semana
    df5a = dfb.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()            
    #entregadores por semana
    df5b = dfb.loc[:, ['week_of_year', 'Delivery_person_ID']].groupby('week_of_year').nunique().reset_index()  
    #merge
    df5m = pd.merge(df5a,df5b, how='inner',)
    # coluna media
    df5m['orders/deliverer'] =df5m['ID']/df5m['Delivery_person_ID']
    #grafico
    fig = px.line(df5m, x='week_of_year', y='orders/deliverer')
    return fig

def order_by_week(dfb):
    """Faz gráfico de linhas"""
    #criando coluna semana
    dfb['week_of_year'] = dfb['Order_Date'].dt.strftime('%U')
    #agrupando por semana
    df2 = dfb.loc[:, ['week_of_year', 'ID']].groupby('week_of_year').count().reset_index()
    fig = px.line(df2, x= 'week_of_year', y='ID')
    return fig
def traffic_order_city(dfb):
    """Faz gráfico bolhas"""
    cols = ['City', 'Road_traffic_density', 'ID']
    df4 = (dfb.loc[:, cols]
           .groupby(['City', 'Road_traffic_density'])
           .count().reset_index())
    fig = px.scatter(df4, x= 'City', y='Road_traffic_density', size = 'ID', color = 'ID')
    return fig

def traffic_order_share(dfb):
    """Gerar gráfico de pizza"""
    cols = ['Road_traffic_density', 'ID']
    df3 = (dfb.loc[:, cols]
           .groupby(by='Road_traffic_density').count().reset_index())
    df3['percent'] = 100 * df3['ID']/df3['ID'].sum()    
    fig = px.pie(df3, values = 'percent', names = 'Road_traffic_density')
    return fig

def order_metric(dfb):
    """ Gerar gráfico de barras
    """
            
    cols = ['Order_Date', 'ID']
    df1 = dfb.loc[:, cols].groupby('Order_Date').count().reset_index()
    fig = px.bar(df1, x='Order_Date', y='ID')
    return fig

def clean_code(dfb):
    """
        Esta função tem a responsabilidade de limpar o dataframe
        Tipos de limpeza:
        1. Remoção de dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços da variável de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo(remoção do texto da variável numérica)

        Input: Dataframe
        Output: Dataframe
    """
    
    linhas = dfb['Delivery_person_Age'] != 'NaN '
    dfb = dfb.loc[linhas, :].copy()
    dfb['Delivery_person_Age'] = dfb['Delivery_person_Age'].astype(int)
    
    # convertendo trafego
    linhas = dfb['Road_traffic_density'] != 'NaN '
    dfb  = dfb.loc[linhas, :].copy()
    
    # convertendo City
    linhas = dfb['City'] != 'NaN '
    dfb  = dfb.loc[linhas, :].copy()
    
    # convertendo Festival
    linhas = dfb['Festival'] != 'NaN '
    dfb  = dfb.loc[linhas, :].copy()
    
    #convertendo ratings
    dfb['Delivery_person_Ratings'] = dfb['Delivery_person_Ratings'].astype(float)
    
    #3 convertendo order date
    dfb['Order_Date'] = pd.to_datetime(dfb['Order_Date'], format = '%d-%m-%Y')
    
    #4 convertendo multiple deliveries
    linhas = dfb['multiple_deliveries'] != 'NaN '
    dfb = dfb.loc[linhas, :].copy()
    dfb['multiple_deliveries'] = dfb['multiple_deliveries'].astype(int)
    
    #5 convertendo Time_taken(min)	
    dfb['Time_taken(min)'] = dfb['Time_taken(min)'].str.replace('(min) ','').astype(int)
    
    # removendo espaços
    dfb['ID'] = dfb['ID'].str.strip()
    dfb['Road_traffic_density'] =dfb['Road_traffic_density'].str.strip()
    dfb['Type_of_order'] =dfb['Type_of_order'].str.strip()
    dfb['Type_of_vehicle'] =dfb['Type_of_vehicle'].str.strip()
    dfb['City'] = dfb['City'].str.strip()
    dfb['Festival'] = dfb['Festival'].str.strip()

    return dfb
#-------------------------Início da estrutura lógica do código-------------------

#carregando dataset
df = pd.read_csv('train.csv')
#dfb = df.copy()
#limpeza
dfb = clean_code(df)


# ==============================================
# = Barra lateral
# ==============================================
st.header('Marketplace - Visão Cliente')
image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest delivery in town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = datetime(2022,4,13),
   min_value = datetime(2022,2,11),
   max_value = datetime(2022,4,6),
    format = 'DD-MM-YYYY'
    
)
# filtro por data
linhas = dfb['Order_Date'] < date_slider
dfb = dfb.loc[linhas, :]




st.sidebar.markdown("""---""")

traffic_options =st.sidebar.multiselect('Quais as condições do trânsito',
      ['Low', 'Medium', 'High','Jam'],
       default = ['Low', 'Medium', 'High','Jam']
                      )
st.sidebar.markdown("""---""")
#filtro por transito
linhas = dfb['Road_traffic_density'].isin(traffic_options)
dfb = dfb.loc[linhas,:]

# ==============================================
# = Layout Streamlit
# ==============================================

tab1, tab2, tab3 =st.tabs(['Visão Gerencial', 'Visão Tática', 
         'Visão Geográfica'])

with tab1:
    # Order metric
    with st.container():
          
        st.markdown('# Orders by day')
        fig = order_metric(dfb)
        st.plotly_chart(fig, use_container_width = True)
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic order share')
            fig = traffic_order_share(dfb)                       
            st.plotly_chart(fig, use_container_width = True)
        with col2:
            st.header('Traffic order City')
            fig = traffic_order_city(dfb)
            st.plotly_chart(fig, use_container_width = True)

with tab2:
    with st.container():
        st.markdown('# Order by week')
        fig = order_by_week(dfb)        
        st.plotly_chart(fig, use_container_width = True)
    with st.container():
        st.markdown('# Order share by week')
        fig = order_share_by_week(dfb)
        st.plotly_chart(fig, use_container_width = True)
        
with tab3:
    st.markdown('# Country Maps')
    country_maps(dfb)
    



# st.header(date_slider)
# st.dataframe(dfb)



#print('Estou aqui')

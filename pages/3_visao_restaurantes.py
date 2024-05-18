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
import numpy as np

#ajustando largura da página
st.set_page_config(
    page_title = 'Visão Restaurantes',
    layout='wide')

#=======================================
# Funções
#=======================================
def avg_std_time_on_traffic(dfb):
    cols = ['City', 'Road_traffic_density', 'Time_taken(min)']
    df5 = dfb.loc[:, cols].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
    df5.columns = ['avg_time','std_time']
    df5 = df5.reset_index()
    #plot
    fig = px.sunburst(df5, path=['City', 'Road_traffic_density'], values = 'avg_time',
          color = 'std_time', color_continuous_scale='RdBu',
          color_continuous_midpoint= np.average(df5['std_time']))
    return fig

def avg_std_time_graph(dfb):
                
    cols = ['City', 'Time_taken(min)']
    df3 = dfb.loc[:, cols].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
    df3.columns = ['avg_time','std_time']
    df3 = df3.reset_index()
    # plot
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name = 'Control',
        x = df3['City'],
        y = df3['avg_time'],
        error_y = {'type': 'data', 'array': df3['std_time']}
        
    ))
    fig.update_layout(barmode='group')
    return fig

def avg_std_time_delivery(dfb, op, festival):
                
    cols = ['Festival', 'Time_taken(min)']
    df6 = dfb.loc[:, cols].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})
    df6.columns = ['avg_time','std_time']
    df6 = df6.reset_index()
    linhas = df6['Festival'] == festival
    var = df6.loc[linhas, op]
    return var

def distance(dfb, fig):
    if fig == False:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude',
        'Delivery_location_longitude']
        dfb['distance'] = dfb.loc[:, cols].apply(lambda x: haversine(
        (x['Restaurant_latitude'], x['Restaurant_longitude']),
        (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1)
        media = np.round(dfb['distance'].mean(),2)
        return media
    else:
        avg_distance = dfb.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
            #plotando
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0,0.1,0])])
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

#=========================
# carregando dataset
#=========================

df = pd.read_csv('train.csv')
dfb = clean_code(df)

# ==============================================
# = Barra lateral
# ==============================================
st.header('Marketplace - Visão Restaurantes')
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
#st.dataframe(dfb.head())
# ==============================================
# = Layout Streamlit
# ==============================================
tab1, tab2, tab3 =st.tabs(['Visão Gerencial', '--', 
         '--'])
with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        with col1:
            
            entregadores = dfb.loc[:, 'Delivery_person_ID'].nunique()
            st.metric('Entregadores', entregadores)
        with col2:
                            
            col2.metric('Distância média(Km)', distance(dfb, fig=False))
        with col3:
            
            col3.metric('Tempo de entrega em festival', np.round(
                avg_std_time_delivery(dfb, op = 'avg_time', festival = 'Yes'),2))
        with col4:
            
            col4.metric('Desv pad em festival', np.round(
                avg_std_time_delivery(dfb, op = 'std_time', festival = 'Yes'),2))
        with col5:
            
            col5.metric('Tempo de entrega fora de festival', np.round(
                 avg_std_time_delivery(dfb, op = 'avg_time', festival = 'No'),2))
        with col6:
            
            col6.metric('Desv pad fora de festival', np.round(
                avg_std_time_delivery(dfb, op = 'std_time', festival = 'No'),2))
        
    with st.container():
        st.markdown("""___""")
        col1, col2 = st.columns(2)
        with col1:
            
            #graf barras
            st.title('Tempo médio de entrega por cidade')
            fig = avg_std_time_graph(dfb)
                        
            st.plotly_chart(fig, use_container_width = True)

        with col2:
            st.title('Tempo médio por cidade e tráfego')

            cols = ['City', 'Road_traffic_density', 'Time_taken(min)']
            df5 = dfb.loc[:, cols].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
            df5.columns = ['avg_time','std_time']
            df5 = df5.reset_index()
            st.dataframe(df5)

        
        
    with st.container():
        st.markdown("""___""")
        st.title('Distribuição de tempo')
        col1,col2 = st.columns(2)
        with col1:
            # conteúdo na funçao distance()
            fig = distance(dfb, fig=True)
            st.plotly_chart(fig)
           
        with col2:
            
            fig = avg_std_time_on_traffic(dfb)
            st.plotly_chart(fig)
        
    
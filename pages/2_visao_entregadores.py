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
    page_title = 'Visão Entregadores',
    layout='wide')

#===========================
# Funções
#===========================
def top_delivers(dfb, top_asc):
                
    df7 = ((dfb.loc[:, ['City', 'Delivery_person_ID', 'Time_taken(min)']]
            .groupby(['City', 'Delivery_person_ID'])
            .mean().sort_values('Time_taken(min)', ascending = top_asc).reset_index()))
    df_aux01 = df7.loc[df7['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df7.loc[df7['City'] == 'Urban', :].head(10)
    df_aux03 = df7.loc[df7['City'] == 'Semi-Urban', :].head(10)
    df_r = pd.concat([df_aux01, df_aux02, df_aux03])
    return df_r

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
st.header('Marketplace - Visão Entregadores')
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

tab1, tab2, tab3 =st.tabs(['Visão Gerencial', '--', 
         '--'])
with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap = 'large'
                                           )
        with col1:
            
            maior = dfb['Delivery_person_Age'].max()
            col1.metric('Maior idade', maior)
        with col2:
            
            menor = dfb['Delivery_person_Age'].min()
            col2.metric('Menor idade', menor)
        with col3:
            
            melhor = dfb['Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor)
        with col4:
            
            pior = dfb['Vehicle_condition'].min()
            st.metric('Pior condição', pior)
    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por entregador')
            df3 =( dfb.loc[:, ['Delivery_person_ID', 
                               'Delivery_person_Ratings']]
                  .groupby('Delivery_person_ID')
                  .mean().reset_index())
            st.dataframe(df3)

        with col2:
            st.markdown('##### Avaliação média por trânsito')
            df4 = (dfb.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']]
                   .groupby('Road_traffic_density')
                   .agg({'Delivery_person_Ratings': ['mean', 'std']})
)
            df4.columns = ['deliverer_mean', 'deliverer_std']
            
            df4.reset_index()
            st.dataframe(df4)
                        
            st.markdown('##### Avaliação média por clima')
            df5 = (dfb.loc[:, ['Weatherconditions', 'Delivery_person_Ratings']]
                   .groupby('Weatherconditions')
                   .agg(    {'Delivery_person_Ratings': ['mean', 'std']}
            ))
            df5.columns = ['deliverer_mean', 'deliverer_std']
            
            df5.reset_index()
            st.dataframe(df5)
    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Top entregadores mais rápidos')
            df_r = top_delivers(dfb, top_asc=True)
            st.dataframe(df_r)
        with col2:
            st.subheader('Top entregadores mais lentos')
            df_r = top_delivers(dfb, top_asc=False)
            st.dataframe(df_r)
           
            


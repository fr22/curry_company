import streamlit as st
from PIL import Image


st.set_page_config(
    page_title = 'Home',
    #page_icon = ''
    layout = 'wide'
)

#image_path = "D:\Profissional\TI\Repos\Comunidade_DS\FTC-Python\Ciclo-06\"
image = Image.open(#image_path + 
                   'logo.png')

# ==============================================
# = Barra lateral
# ==============================================

st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest delivery in town')
st.sidebar.markdown("""---""")

#==============================================

st.write('# Curry company groth dashboard')

st.markdown(
    """
    Growth dashboard construído para acompanhar as métricas de crescimento dos entregadores e restaurantes
    ### Como usar esse Growth Dashboard?
    - Visão Empresa
        - Visão Gerencial: Métricas gerais de comportamento
        - Visão Tática: Indicadores semanais de crescimento
        - Visão Geográfica: Insights de geolocalização
    - Visão Entregador
        - Acompanhamento dos indicadores gerais de crescimento
    - Visão restaurante
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Time de data science no discord
        - @time
    
    """
)

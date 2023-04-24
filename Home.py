import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="",
    layout='wide')

image = Image.open( 'logo.jpg' )
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write( "# Cury Company Growth Dashboard" )

st.markdown(
    """
    Growth Dashboard foi criado para acompanhar as métricas de crecimento dos Entregadores e Restaurantes.
    ### Como utilizar o Growth Dashboard ?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: indicadores semanais de crecimento.
        - Visão Geográfica: insights de Geocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crecimento.
    - Visão Restaurante:
        - indicadores semanais de crecimento dos Restaurantes.
    ### Ask For Help
        grupo de Data Scientist
        @LuizMoschetta
    """)
# Libraries
import plotly.express as px
import plotly.graph_objects as go
import folium as fl
from haversine import haversine
from streamlit_folium import folium_static

# bibliotecas nescessrias
import pandas as pd
import streamlit as st
from PIL import Image

st.set_page_config(page_title = 'Visão Empresa', page_icon='',layout='wide')

#------------------------------------------------------------------------
#FUNÇÕES
#------------------------------------------------------------------------

def order_metric(df):
    
    """ 1.Recebe dados do dataframe
        2.executa o dataframe e 
        3.gera uma figura
    """
    
    cols = ['ID','Order_Date']
    dias_aux = df.loc[:,cols].groupby('Order_Date').count().reset_index()
    fig = px.bar(dias_aux,x='Order_Date',y='ID')
    
    return fig

def traffic_order_share(df):
    porcentagem_aux = (df.loc[:,['ID','Road_traffic_density']]
                           .groupby('Road_traffic_density')
                           .count()
                           .reset_index())
    porcentagem_aux['Percent_traffic'] = porcentagem_aux['ID'] / porcentagem_aux['ID'].sum()

    fig = px.pie(porcentagem_aux,values='Percent_traffic',names='Road_traffic_density')
                
    return fig

def traffic_order_city(df):
    volume_aux = (df.loc[:,['ID','City','Road_traffic_density']]
                    .groupby(['City','Road_traffic_density'])
                    .count()
                    .reset_index())
    fig = px.scatter(volume_aux,x='City',y='Road_traffic_density',size='ID',color='City')
            
    return fig

def order_week(df):
    df['Week_of_Year'] = df['Order_Date'].dt.strftime( '%U' )
    semana_aux = df.loc[:,['ID','Week_of_Year']].groupby('Week_of_Year').count().reset_index()
    fig = px.line(semana_aux,x='Week_of_Year',y='ID')
        
    return fig

def order_share_by_week(df):
    df_aux1 = df.loc[:,['ID','Week_of_Year']].groupby('Week_of_Year').count().reset_index()
    df_aux2 = df.loc[:,['Delivery_person_ID','Week_of_Year']].groupby('Week_of_Year').nunique().reset_index()

    df_aux = pd.merge(df_aux1,df_aux2,how='inner')
    df_aux['Order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    fig = px.line(df_aux,x='Week_of_Year',y='Order_by_delivery')
        
    return fig

def country_maps(df):
    cols = ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
    df_aux = (df.loc[:, cols]
                .groupby(['City','Road_traffic_density'])
                .median()
                .reset_index())

    map = fl.Map()

    for index, location_info in df_aux.iterrows():
        fl.Marker([location_info['Delivery_location_latitude'],
                  location_info['Delivery_location_longitude']],
                  popup=location_info[['City','Road_traffic_density']]).add_to(map)
    
    folium_static( map )
    
    return None

def clean_code(df):
    """ Esta Função tem a utilidade de limpar o DataFrame 
        
        Tipos de Limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variaveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto dos numeros)
        
        input: Dataframe
        output: Dataframe
    """
    # Remover spaco da string
    #for i in range( len( df ) ):
    #df.loc[i, 'ID'] = df.loc[i, 'ID'].strip()
    df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    df.loc[:, 'Delivery_person_ID'] = df.loc[:, 'Delivery_person_ID'].str.strip()
    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
    df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
    df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
    df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()
    df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()

    # Excluir as linhas com a idade dos entregadores vazia
    linhas_vazias = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    linhas_vazias = df['City'] != 'NaN'
    df = df.loc[linhas_vazias, :]

    linhas_vazias = df['Festival'] != 'NaN'
    df = df.loc[linhas_vazias, :]

    linhas_vazias = df['Weatherconditions'] != 'conditions NaN'
    df = df.loc[linhas_vazias, :]

    # Conversao de texto/categoria/string para numeros inteiros
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )

    # Conversao de texto/categoria/strings para numeros decimais
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )

    # Conversao de texto para data
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

    # Excluir as linhas com mais de um entregadores vazia
    linhas_vazias = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

    # Comando para remover o texto de números
    #df = df.reset_index( drop=True )
    #for i in range( len( df ) ):
    #  df.loc[i, 'Time_taken(min)'] = re.findall( r'\d+', df.loc[i, 'Time_taken(min)'] )

    #recontar a quantidade linhas
    df = df.reset_index( drop=True )

    #retira o (min)
    df.loc[:,'Time_taken(min)'] = df.loc[:,'Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype( int )
    #df.loc[:,'Time_taken(min)'] = df.loc[:,'Time_taken(min)'].astype( int )
    
    return df

#-------------------------------------Inicio da Estrutura logica do codigo--------------------------------------------- 

#----------------------------------------------------
# IMPORTANDO DATASET
#----------------------------------------------------
df = pd.read_csv('datasets/train.csv')

#----------------------------------------------------
#LIMPANDO DADOS
#----------------------------------------------------
df = clean_code(df)

# =======================================================================
# Barra Lateral
# =======================================================================

st.header('Marketplace - Visão Empresa')

image = Image.open( 'logo.jpg' )
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

data_slider = st.sidebar.slider(
    'Até qual Valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de Transito?',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'])

st.sidebar.markdown("""---""")

#filtro de data
linhas_selecionadas = df['Order_Date'] <= data_slider
df = df.loc[linhas_selecionadas, :]

linhas_selecionadas2 = df['Road_traffic_density'].isin( traffic_options )
df = df.loc[linhas_selecionadas2, :]

# =============================================================
# Layout Streamlit
# =============================================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial','Visão Tática','Visão Geográfica' ] )

with tab1:
    with st.container():
        
        fig = order_metric(df)
        st.markdown('## Orders by Day')
        
        st.plotly_chart( fig, use_container_width=True)
        
    with st.container():
        col1,col2 = st.columns( 2 )
        with col1:
            fig = traffic_order_share(df)
            st.markdown('### Traffic Order Share')
            
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            fig = traffic_order_city(df)
            st.markdown('### Traffic Order City')
            
            st.plotly_chart(fig, use_container_width=True)
            
with tab2:
    with st.container():
        fig = order_week(df)
        st.markdown('## Orders Week')
        
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        fig = order_share_by_week(df)
        st.markdown('## Order Share by Week')
        
        st.plotly_chart(fig, use_container_width=True)
    
with tab3:
    st.markdown('## Country Maps')
    
    country_maps(df)
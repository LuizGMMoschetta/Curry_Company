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

st.set_page_config(page_title = 'Visão Entregadores', page_icon='',layout='wide')

#------------------------------------------------------------------------
#FUNÇÕES
#------------------------------------------------------------------------

def df_rating_media_person(df):
    df_rating_media_person = (df.loc[:,['Delivery_person_ID','Delivery_person_Ratings']]
                                      .groupby('Delivery_person_ID')
                                      .mean()
                                      .reset_index())
    
    return df_rating_media_person

def road_traffic_avg(df):
    road_traffic_avg = ( df.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                                .groupby('Road_traffic_density')
                                .agg({'Delivery_person_Ratings':['mean','std']}))

            #Renome de colunas
    road_traffic_avg.columns = ['Delivery_mean','Delivery_std']

            #reset no index das colunas
    road_traffic_avg = road_traffic_avg.reset_index()
    
    return road_traffic_avg

def Weatherconditions_avg(df):
    Weatherconditions_avg = ( df.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                                     .groupby('Weatherconditions')
                                      .agg({'Delivery_person_Ratings':['mean','std']}))

            #renome de colunas
    Weatherconditions_avg.columns = ['Weatherconditions_mean','Weatherconditions_std']

            #reset de index nas colunas
    Weatherconditions_avg = Weatherconditions_avg.reset_index()
    
    return Weatherconditions_avg

def top_entregadores(df, df_asc):
    df_aux = (df.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
                      .groupby(['City','Delivery_person_ID'])
                      .max()
                      .sort_values(['City','Time_taken(min)'],ascending=df_asc)
                      .reset_index())

    df01 = df_aux.loc[df_aux['City'] == 'Metropolitian'].head(10)
    df02 = df_aux.loc[df_aux['City'] == 'Urban'].head(10)
    df03 = df_aux.loc[df_aux['City'] == 'Semi-Urban'].head(10)

    df3 = pd.concat([df01,df02,df03]).reset_index(drop=True)
    
    return df3
    
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

st.header('Marketplace - Visão Entregadores')

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

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial','_','_' ] )

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns( 4, gap='large')
        with col1:
            maior_idade = df.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior idade',maior_idade)
        with col2:
            menor_idade = df.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade',menor_idade)
        with col3:
            melhor_condicao = df.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condição',melhor_condicao)
        with col4:
            pior_condicao = df.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior condição',pior_condicao)
            
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        
        col1, col2 = st.columns( 2 )
        with col1:
            dataframe = df_rating_media_person(df)
            st.markdown('##### Avaliações medias por entregador')
            
            st.dataframe(dataframe)
        with col2:
            dataframe = road_traffic_avg(df)
            st.markdown('##### Avaliação media por transito')

            st.dataframe(dataframe)
            
            
            dataframe1 = Weatherconditions_avg(df)
            st.markdown('##### Avaliação media por clima')

            st.dataframe(dataframe1)
    
    with st.container():
        st.markdown("""---""")
        st.title('Top Entregadores')
        
        col1, col2 = st.columns( 2 )
        with col1:
            dataframe = top_entregadores(df, df_asc=True)
            st.markdown('#### Top entregadores mais rapidos')

            st.dataframe(dataframe)
        
        with col2:
            dataframe = top_entregadores(df, df_asc=False)
            st.markdown('#### Top entregadores mais lentos')

            st.dataframe(dataframe)
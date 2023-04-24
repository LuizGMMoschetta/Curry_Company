# Libraries
import plotly.express as px
import plotly.graph_objects as go
import folium as fl
import numpy as np
from haversine import haversine
from streamlit_folium import folium_static

# bibliotecas nescessrias
import pandas as pd
import streamlit as st
from PIL import Image

st.set_page_config(page_title = 'Visão Restaurantes', page_icon='',layout='wide')

#------------------------------------------------------------------------
#FUNÇÕES
#------------------------------------------------------------------------

def tempo_medio_desvio_padrao(df):
    df_aux = df.loc[:,['City','Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean','std']})
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x= df_aux['City'], y=df_aux['avg_time'],error_y=dict(type='data',array=df_aux['std_time'] )))
    fig.update_layout(width=340, height=450)
    
    return fig

def tipo_cidade_avg_std(df):
    df_aux1 = (df.loc[:,['City', 'Time_taken(min)', 'Type_of_order']]
                           .groupby(['City','Type_of_order'])
                           .agg({'Time_taken(min)': ['mean','std']}))

    df_aux1.columns = ['avg_time','std_time']
    df_aux1 = df_aux1.reset_index()
    
    return df_aux1

def cidade_tipo_trafego_std_avg(df):
    df_aux2 = (df.loc[:,['City', 'Time_taken(min)', 'Road_traffic_density']]
                            .groupby(['City','Road_traffic_density'])
                            .agg({'Time_taken(min)': ['mean','std']}))

    df_aux2.columns = ['avg_time','std_time']
    df_aux2 = df_aux2.reset_index()
    fig = px.sunburst(df_aux2, path=['City','Road_traffic_density'], values='avg_time',
                              color='std_time',color_continuous_scale='RdBu',
                              color_continuous_midpoint=np.average(df_aux2['std_time']))
            
    fig.update_layout(width=350, height=500)
    
    return fig

def distancia_media(df):
    cols = ['Restaurant_longitude','Restaurant_latitude','Delivery_location_latitude','Delivery_location_longitude']

    df['Distance'] = (df.loc[:,cols].apply(lambda x :
                      haversine(
                         (x['Restaurant_latitude'],x['Restaurant_longitude']),
                         (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1))

    avg_distancia = df.loc[:,['City','Distance']].groupby('City').mean().reset_index()

    fig = go.Figure( data=[ go.Pie( labels= avg_distancia['City'], values=avg_distancia['Distance'],pull=[0,0.1,0])])
    
    return fig

def avg_distancia(df):
    cols = ['Restaurant_longitude','Restaurant_latitude','Delivery_location_latitude','Delivery_location_longitude']

    df['Distance'] = (df.loc[:,cols].apply(lambda x :
                      haversine(
                      (x['Restaurant_latitude'],x['Restaurant_longitude']),
                      (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1))

    avg_distancia = np.round(df['Distance'].mean(),2)
    
    return avg_distancia

def data_analise(df,op,fest):
    """
        "informar se as condições de festival e calculo para a analise"
        fest = 'Yes' para Festival ou 'No' sem Festival
        op = 'std_time' para desvio padrao 'avg_time' para Media
    """
    cols3 = [ 'Time_taken(min)', 'Festival']

    df_aux3 = df.loc[:,cols3].groupby('Festival').agg({'Time_taken(min)': ['mean','std']})

    df_aux3.columns = ['avg_time','std_time']
    df_aux3 = df_aux3.reset_index()
    df_aux3 = np.round(df_aux3.loc[df_aux3['Festival'] == fest ,op],2)
    
    return df_aux3

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

st.header('Marketplace - Visão Restaurantes')

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
        st.markdown('### Overall Metrics')
        
        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        with col1:
            delivery_unique = len(df.loc[:,'Delivery_person_ID'].unique())
            st.metric('Entregadores unicos',delivery_unique)
        with col2:
            metric = avg_distancia(df)
            st.metric('Distancia média',metric)
        with col3:
            metric = data_analise(df,op= 'avg_time',fest='Yes')
            st.metric('Tempo medio de entrega com festival',metric)
        with col4:
            metric = data_analise(df,op= 'std_time',fest='Yes')
            st.metric('O tempo de Desvio padrão com festival',metric)
        with col5:
            metric = data_analise(df,op= 'avg_time',fest='No')
            st.metric('Tempo medio de entrega sem festival',metric)
        with col6:
            metric = data_analise(df,op= 'std_time',fest='No')
            st.metric('Tempo de desvio padrão sem festival',metric)
            
    with st.container():
        st.markdown("""---""")
        
        col1,col2 = st.columns(2)
        with col1:
            fig = tempo_medio_desvio_padrao(df)
            st.markdown('###### Tempo Médio e Desvio Padrão por Cidade')
            
            st.plotly_chart(fig)
        
        with col2:
            dataframe = tipo_cidade_avg_std(df)
            st.markdown('###### Tempo Médio e Desvio Padrão por Cidade e tipo de pedido')

            st.dataframe(dataframe)
        
    with st.container():
        st.markdown("""---""")
        
        col1, col2 = st.columns( 2 )
        with col1:
            fig = cidade_tipo_trafego_std_avg(df)
            st.markdown('###### Tempo Médio e Desvio Padrão por Cidade e tipo de trafego')
            
            st.plotly_chart(fig)
            
        with col2:
            fig = distancia_media(df)
            st.markdown('###### Distancia Media dos Restaurantes')
        
            st.plotly_chart(fig)
        
        
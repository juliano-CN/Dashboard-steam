#%%
import streamlit as st
import pandas as pd
import plotly.express as px

#python -m streamlit run dashboard.py

#configura layout da pagina
st.set_page_config(layout="wide",page_title="Dashboard")

#ler os dados
data = pd.read_parquet("Data/games.parquet")
data_copy = data.copy()#copia o df

data_copy = data_copy[data_copy["Estimated owners"] != "0 - 0"]
data_copy = data_copy[~data_copy['Genres'].isna()]
data_copy['Genres'] = data_copy['Genres'].str.lower().str.strip()

#transformar variaveis
#converte para data
data_copy['Release date'] = data_copy['Release date'].astype("datetime64[ns]")

#título
st.title("Dashborad Steam")

#texto
introduction, = st.columns(1, border=True)  # vírgula desempacota a lista
introduction.write("Dados dos jogos da steam coletados aproximadamente em abril de 2025. Altere os valores " \
"para atualizar os gráficos. Mais informações leia o README.md.")

#barra-------
# Pega a data mínima e máxima do dataframe
min_date = data_copy['Release date'].dt.year.min()
max_date = data_copy['Release date'].dt.year.max()

# Cria um slider de intervalo de datas
date_range = st.slider(
    "Período:",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)# valor inicial (intervalo completo)
)

# escolher o gênero
Genres = data_copy['Genres'].str.lower().dropna()
Genres = Genres.str.strip("[]").str.split(",")

uniques = Genres.explode().str.strip().drop_duplicates().tolist()

g = st.multiselect("Gênero(s)", uniques)

# checkbox-------
freeGames = st.checkbox("Remover jogos grátis")

#filtrar no dataFrame
if freeGames:
        df_Free = data_copy[data_copy['Price'] > 0]
else:
        df_Free = data_copy

df_genres = df_Free[df_Free['Genres'].apply(
                                lambda x:all(item in [x.strip().lower() for x in x.split(",")]
                                for item in g))]

df_filtered = df_genres[(df_genres["Release date"].dt.year>=date_range[0]) &
               (df_genres["Release date"].dt.year<=date_range[1])]

#texto
col0, = st.columns(1, border=True)
col0.write(f"{len(df_filtered)} jogos encontrados")

# graficos/análise-------
col1,col2 = st.columns(2,border=True)

if len(df_filtered) != 0:
        freq_year = df_filtered['Release date'].dt.year.value_counts().sort_index(ascending=True)
        fig_date1 = px.line(freq_year,y= freq_year.values,x = freq_year.index,
                    title = "Quantidades de lançamentos por ano")#,labels={"y": "","Lançamento":""}
        col1.plotly_chart(fig_date1)


        freq_mounth = df_filtered['Release date'].dt.month.value_counts()
        fig_date2 = px.bar(freq_mounth,y= freq_mounth.values,x = freq_mounth.index,
                   title = "Quantidades de lançamentos por mês")
        col2.plotly_chart(fig_date2)


col3,col4 = st.columns(2,border=True)

if len(df_filtered) != 0:
        fig_date3 = px.box(df_filtered,y = 'Price',
                           title='distribuição de preços',
                           hover_data=["Name"])
        col3.plotly_chart(fig_date3)

        fig_date4 = px.scatter(df_filtered,x="Negative",y="Positive",color="Estimated owners",
                               title= "Votos positivos x negativos",
                               hover_data=["Name","Required age","Price"])

        col4.plotly_chart(fig_date4)

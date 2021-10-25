import pandas as pd
import streamlit as st
from streamlit import caching
from datetime import datetime
from datetime import timedelta, date
import altair as alt
import base64
import io
import apiMovidesk
from pesquisaSatisfacao import df_satis
from acoesChamados import consulta_acoes
from io import StringIO
from streamlit_metrics import metric, metric_row
# import sweetviz as sv

st.set_page_config(
    page_title="Chamados Movidesk",
    layout="wide",
    page_icon=":shark",
    initial_sidebar_state="expanded",
)


@st.cache
def load_data():
    # carregando o dataset
    data = pd.read_excel("files/appMovidesk.xlsx")
    return data


df = load_data()


# título
st.title("Bem vindo ao Relatório de Chamados do Movidesk!!!")

# subtítulo
st.subheader("Pare analisar os dados mais recentes, clique no botão abaixo:")
btn_reload = st.button("Atualizar")


# Menu Lateral

st.sidebar.subheader("Filtros")

# mapeando dados do usuário para cada atributo

empresa = st.sidebar.selectbox("Empresa", ("Tudo", "ABDI", "CNSESI", "CREA - RJ", "DATAEASY", "ELET. - AMAZONAS",
                                           "EMGETIS", "FIETO", "IT2B", "MÚTUA", "SANEAGO", "SEBRAE - AC", "SEBRAE - BA",
                                           "SEBRAE - CE", "SEBRAE - MS", "SEBRAE - PE", "SEBRAE - TO", "SERPRO",
                                           "PGE - SP", "PREF. DE SÃO LUÍS", "PREVCOM", "TCE - MS", "VERT"))

status = st.sidebar.selectbox("Status", ("Tudo", "Aguardando", "Cancelado", "Em atendimento", "Fechado", "Resolvido"))

categoria = st.sidebar.selectbox("Categoria", ("Tudo", "Desenvolvimento", "Dúvida", "Infraestrutura", "Problema",
                                               "Solicitação de serviço", "Sugestão", "Não Categorizado"))

# tipo = st.sidebar.selectbox("Tipo", ("Tudo", "Publico", "Interno"))
tipo = st.sidebar.radio("Selecione o Tipo:", ["Tudo", "Publico", "Interno"])

today = datetime.today()
yesterday = today - timedelta(days=182)

# Para facilitar o entendimento a consulta se iniciara no começo do ano
inicio_ano = "2021-01-01"
inicio_ano = datetime.strptime(inicio_ano, "%Y-%m-%d").date()

btn_hoje = st.sidebar.button("Hoje")
btn_mes = st.sidebar.button("Mês atual")


if btn_hoje:
    start_date = st.sidebar.date_input('Data Inicial', today)
else:
    start_date = st.sidebar.date_input('Data Inicial', inicio_ano)

if btn_mes:
    inicio_mes = today.day
    dia_primeiro = today - timedelta(days=inicio_mes - 1)
    start_date = dia_primeiro  # st.sidebar.date_input('Data Inicial', dia_primeiro)
    end_date = st.sidebar.date_input('Data Final', today)
else:
    # start_date = st.sidebar.date_input('Data Inicial', yesterday)
    end_date = st.sidebar.date_input('Data Final', today)

# Fim Menu Lateral


# Página principal

# verificando o dataset
# st.subheader("Selecionando apenas um pequeno conjunto de atributos")


# exibindo os top 10 registro do dataframe

filtros = {"Empresa": empresa, "Status": status, "Categoria": categoria, "Tipo": tipo}

for filtro in filtros:
    nomeDoFiltro = filtro
    valorDoFiltro = filtros[filtro]
    if valorDoFiltro != "Tudo":
        # print(f"Filtrando todos os registros que possuem {nomeDoFiltro} com valor {valorDoFiltro}")
        df = df[df[nomeDoFiltro] == valorDoFiltro]

df_filtrado = (df['Data'] >= pd.Timestamp(start_date)) & (df['Data'] <= pd.Timestamp(end_date))
df = df[df_filtrado]


# Alterando o formato da hora para ser apresentado do Dataframe
df['Data'] = df['Data'].dt.strftime("%d-%m-%Y")
df['DataFechamento'] = df['DataFechamento'].dt.strftime("%d-%m-%Y")
df['DataUltimaAcao'] = df['DataUltimaAcao'].dt.strftime("%d-%m-%Y")

if df.empty:

    st.subheader("Não há dados a serem apresentados com os filtros utilizados. :cry:")
    st.write("Selecione outros filtros no menu lateral. :rewind:")


else:

    st.write("Clique nos itens para expandir")
    with st.beta_expander("Distribuição dos chamados:", expanded=True):
        # Métricas dos chamados
        # metric(label="Temperature", value="70 °F")
        metric_row(
            {
                "Total de chamados": df.Empresa.count(),
                "Em atendimento": (df["Status"] == "Aguardando").sum() + (df["Status"] == "Em atendimento").sum(),
                "Concluídos": (df["Status"] == "Resolvido").sum() + (df["Status"] == "Fechado").sum() +
                              (df["Status"] == "Cancelado").sum()
             }
        )
        suporte = df.query("Status == 'Em atendimento' or Status == 'Aguardando' and "
                           "Justificativa == 'Enviado para Análise' ")["Status"].count()

        cliente = df.query("Status == 'Aguardando' and Justificativa == 'Retorno do "
                           "cliente' or Justificativa == 'Validação do Cliente'")["Status"].count()

        dev = df.query("Status == 'Aguardando' and Justificativa == 'Equipe de desenvolvimento' "
                       "or Justificativa == 'Liberação de versão'")["Justificativa"].count()

        infra = df.query("Status == 'Aguardando' and Justificativa == 'Infraestrutura'")["Status"].count()

        melhorias = df.query("Status == 'Aguardando' and Justificativa == 'Aprovação de orçamento'"
                             "or Justificativa == 'Elaboração de Requisitos'")["Status"].count()

        metric_row(
            {
                "Cliente": cliente,
                "Suporte": suporte,
                "Desenvolvimento": dev,
                "Infraestrutura": infra,
                "Requisitos": melhorias,

             }
        )

        retorno = df.query("Status == 'Aguardando' and Justificativa == 'Retorno do cliente'")["Status"].count()
        validacao = df.query("Status == 'Aguardando' and Justificativa == 'Validação do Cliente'")["Status"].count()

        atendimento = df.query("Status == 'Em atendimento'")["Status"].count()
        analise = df.query("Status == 'Aguardando' and Justificativa == 'Enviado para Análise' ")["Status"].count()

        desenv = df.query("Status == 'Aguardando' and Justificativa == 'Equipe de desenvolvimento'")["Justificativa"].count()

        liberacao = df.query("Status == 'Aguardando' and Justificativa == 'Liberação de versão'")["Justificativa"].count()

        # KPIs de informação dos chamados
        # col_kpi_1, col_kpi_2, col_kpi_3 = st.beta_columns(3)
        # with col_kpi_1:
            # st.write(f"Retorno do cliente: {retorno}")
            # st.write(f"Validação do cliente: {validacao}")

        # with col_kpi_2:
            # st.write(f"Em atendimento: {atendimento}")
            # st.write(f"Em análise: {analise}")

        #with col_kpi_3:
            # st.write(f"Desenvolvendo: {desenv}")
            # st.write(f"Liberado: {liberacao}")

        # st.write("* Suporte: tickets Em atendimento, Aguardando Retorno do Cliente e Aguardando Validação do Cliente")
        # st.write("* Requisitos: tickets Em análise, Elaboração de requisitos e Aprovação de orçamentos.")

    # atributos para serem exibidos por padrão
    defaultcols = ["Ticket", "Empresa", "Assunto", "Status", "Categoria", "Data"]

    # Exibir o dataframe dos chamados
    with st.beta_expander("Descrição dos chamados:", expanded=True):
        texto = st.text_input("Pesquisar por assunto: ")
        filtro = df.Assunto.str.contains(texto, case=False, regex=False)
        df = df.loc[filtro]
        cols = st.multiselect("", df.columns.tolist(), default=defaultcols)
        # Dataframe
        st.dataframe(df[cols].sort_values(by="Ticket", ascending=False).set_index("Ticket"))

    # Ações do chamado
    #with st.beta_expander("Ações do ticket:"):
    #    ticket_input = st.text_input("Insira o número do ticket", "")
    #    acoes = consulta_acoes(ticket_input)
    #    st.write(acoes)
        # print(acoes)
        # for i in acoes:
        #    print(i)

    with st.beta_expander("Análise Gráfica dos dados:"):
        # defindo atributos a partir do multiselect
        brush = alt.selection_multi()

        cont_status_chart = alt.Chart(df).mark_bar().encode(
            alt.Y("Status", bin=False, title="Status", sort=alt.SortField("order", order="descending"),),
            alt.X("count():Q", title="Contagem de Chamados")
        ).properties(
            # width=700,
            height=300
        ).configure_mark(
            opacity=0.8,
            color='#04a2ca',
            cornerRadius=4,
            tooltip=True,
        ).add_selection(
            brush
        ).transform_filter(
            brush
        )

        # st.write(cont_status_chart)

        # st.subheader("Origem dos Chamados")
        origem_chart = alt.Chart(df).mark_bar().encode(
            alt.Y("Origem", bin=False, title="Origem", sort=alt.SortField("order", order="descending")),
            alt.X("count()", title="Contagem de Chamados")
        ).properties(
            # width=400,
            height=300
        ).configure_mark(
            opacity=0.8,
            color='#4b9484',
            cornerRadius=4,
            tooltip=True,
        )
        # st.write(origem_chart)

        # st.subheader("Chamados por Mes")
        qtde_dia_chart = alt.Chart(df).mark_bar().encode(
            alt.X("MesNome", bin=False, title="Mês",  sort=alt.SortField("order", order="descending")),
            alt.Y("count()", title="Contagem de Chamados")
        ).properties(
            width=900,
            height=300
        ).configure_mark(
            opacity=0.8,
            color='#1f77b4',
            cornerRadius=4,
            tooltip=True
        )
        # st.write(qtde_dia_chart)

        # st.subheader("Chamados por empresa")
        empresa_chart = alt.Chart(df).mark_bar().encode(
            alt.Y("Empresa", bin=False, title="Empresa"),
            alt.X("count()", title="Contagem de Chamados", sort=alt.SortField("order", order="descending"))
        ).properties(
            # width=700,
            height=300
        ).configure_mark(
            opacity=0.8,
            color='#dd8452',
            cornerRadius=4,
            tooltip=True
        )
        # st.write(empresa_chart)

        # st.subheader("Chamados por Responsável")
        resp_chart = alt.Chart(df).mark_bar().encode(
            alt.Y("Responsavel", bin=False, title="Responsavel"),
            alt.X("count()", title="Contagem de Chamados", sort=alt.SortField("order", order="descending"))
        ).properties(
            # width=700,
            height=300
        ).configure_mark(
            opacity=0.8,
            color='#ff3f3f',
            cornerRadius=4,
            tooltip=True
        )
        # st.write(resp_chart)

        # Chamados por dia da Semana
        # st.write(f"Dia da Semana: {df.DiaSemana.count()}")
        cont_dia_semana = alt.Chart(df).mark_bar().encode(
            alt.X("DiaSemana", bin=False, title="Status"),
            alt.Y("count()", title="Contagem de Chamados")
        ).properties(
            width=400,
            height=300
        ).configure_mark(
            opacity=0.8,
            color='#04a2ca',
            cornerRadius=4,
            tooltip=True,
        )

        # divide as plotagens em colunas
        col1, col2 = st.beta_columns(2)

        # Coluna 1
        with col1:
            st.subheader("Status dos Chamados")
            st.write(cont_status_chart)

            st.subheader("Chamados por Responsável")
            st.write(resp_chart)

            # st.subheader("Dia da Semana")
            # st.write(cont_dia_semana)

        # Coluna 2
        with col2:
            st.subheader("Origem dos Chamados")
            st.write(origem_chart)

            st.subheader("Chamados por empresa")
            st.write(empresa_chart)

        # Este gráfico fica de fora da divisão das colunas
        st.subheader("Chamados por Mês")
        st.write(qtde_dia_chart)

    # Fim da Página Principal

    # Análise Estatística

    with st.beta_expander("Análise Estatística dos Chamados:"):

        # divide em 3 colunas
        col3, col4 = st.beta_columns(2)
        # col3, col4, col5 = st.beta_columns((1, 1, 1))
        with col3:
            st.write("Quantidade máxima de dias para resolução do chamado")
            max_dias = df.groupby("Empresa")["QtdeDiasChamado"].max().sort_values(ascending=False)
            max_dias = max_dias.fillna("-")
            st.write(max_dias)

            st.write("Média de dias entre a última ação e o fechamento")
            ult_acao_fech = df.groupby("Empresa")["DifUltimaAçaoFechamento"].mean().sort_values(ascending=False).round()
            ult_acao_fech = ult_acao_fech.fillna("-")
            st.write(ult_acao_fech)

        with col4:
            st.write("Média de dias para resolução do Chamado")
            med_resol = df.groupby("Empresa")["QtdeDiasChamado"].mean().sort_values(ascending=False).round()
            med_resol = med_resol.fillna("-")
            st.write(med_resol)

            st.write("Média de ações em cada ticket")
            med_acoes = df.groupby("Empresa")["ContagemAções"].mean().sort_values(ascending=False).round()
            med_acoes = med_acoes.fillna("-")
            st.write(med_acoes)

        st.write("Dias com maior número de chamados")
        st.write(df.groupby("Data")["Empresa"].count().sort_values(ascending=False).head(5))

    # Fim da Análise Estatística

    # Acessar a pesquisa de Satisfação
    with st.beta_expander("Pesquisa de Satisfação:"):

        # Fazendo o merge com o df principal e o de resposta da pesquisa de satisfação
        df2 = df.merge(df_satis, how="left", left_on="Ticket", right_on='Ticket')

        btn_satisfacao = st.button("Exibir a Pesquisa de Satisfação")

        if btn_satisfacao:
            # atributos para serem exibidos por padrão
            df2 = df2.query("Valor == 'Satisfeito' or Valor == 'Insatisfeito'")
            colunas_satis = ["Ticket", "Empresa", "Responsavel", "Valor",  "Comentario"]

            # defindo atributos a partir do multiselect
            cols = st.multiselect("", df2.columns.tolist(), default=colunas_satis)

            # Dataframe
            st.dataframe(df2[cols].sort_values(by="Ticket", ascending=False).set_index("Ticket"))
            satisfeitos = df2.query("Valor == 'Satisfeito'")["Valor"].count()
            insatisfeitos = df2.query("Valor == 'Insatisfeito'")["Valor"].count()

            metric_row(
                {
                    "Satisfeitos": satisfeitos,
                    "Insatisfeitos": insatisfeitos,
                }
            )

    # Criando uma nuvem de palavras
    with st.beta_expander("Wordcloud:"):
        st.write("Nuvem de palavras dos assuntos dos chamados:")
        btn_wordcloud = st.button("Gerar nuvem de palavras")

        if btn_wordcloud:
            st.image("images/wordcloud.png")



# inserindo um botão na tela
btn_relatorio = st.sidebar.button("Gerar Relatório")
# btn_reload = st.sidebar.button("Atualizar")


# Download em formato csv
def get_table_download_link(df):
    csv = df.to_csv(index=False, encoding="utf-8")
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="Relátorio-' \
           f'{pd.to_datetime("today")}.csv">Download do relatório em CSV</a>'

    return href


# Download em formato excel
def create_download_link_excel(df, title="Download do relatório em Excel", filename="file.xlsx"):
    # to_excel() does not work to string buffer directly
    output = io.BytesIO()
    # Use the BytesIO object as the filehandle
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    # Write the data frame to the BytesIO object and save it
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data)
    payload = b64.decode()
    html = '<a download="{filename}" href="data:text/xml;base64,{payload}" target="_blank">{title}</a>'
    html = html.format(payload=payload, title=title, filename=filename)
    return html


# verifica se o botão foi acionado
if btn_relatorio:
    st.sidebar.markdown(get_table_download_link(df), unsafe_allow_html=True)
    st.sidebar.markdown(create_download_link_excel(df), unsafe_allow_html=True)
    # my_report = sv.analyze(df)
    # my_report.show_html()


if btn_reload:
    apiMovidesk.etl()
    caching.clear_cache()









# Form (Conteiner)
# with st.form("my_form"):
#   st.write("Inside the form")
#   slider_val = st.slider("Form slider")
#   checkbox_val = st.checkbox("Form checkbox")

# Every form must have a submit button.
#   submitted = st.form_submit_button("Submit")
#   if submitted:
#       st.write("slider", slider_val, "checkbox", checkbox_val)

# st.write("Outside the form")


# upload de arquivo
# uploaded_file = st.file_uploader("Choose a file")
# if uploaded_file is not None:
    # To read file as bytes:
#    bytes_data = uploaded_file.getvalue()
#    st.write(bytes_data)

    # To convert to a string based IO:
#    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
#    st.write(stringio)

    # To read file as string:
#    string_data = stringio.read()
#    st.write(string_data)

    # Can be used wherever a "file-like" object is accepted:
#    dataframe = pd.read_csv(uploaded_file, sep=",")
#    st.dataframe(dataframe)


# Slider  numerico
# age = st.slider('How old are you?', 0, 130, 25)
# st.write("I'm ", age, 'years old')

# values = st.slider(
#    'Select a range of values',
#    0.0, 100.0, (25.0, 75.0))
# st.write('Values:', values)

# Slider de time
# from datetime import time
# appointment = st.slider(
#    "Schedule your appointment:",
#     value=(time(11, 30), time(12, 45)))
# st.write("You're scheduled for:", appointment)

# Slider de Data
# from datetime import datetime
# start_time = st.slider(
#    "When do you start?",
#    value=datetime(2021, 1, 1, 9, 30),
#    format="MM/DD/YY - hh:mm")
# st.write("Start time:", start_time)




# executar a aplicação: streamlit run appMovidesk.py

# publicar no Heroku: https://charlesalves.com.br/2020/04/26/streamlit/
# customização dos gráficos: https://altair-viz.github.io/user_guide/customization.html
# https://altair-viz.github.io/user_guide/generated/toplevel/altair.Chart.html
# Alteração de temas: https://blog.streamlit.io/introducing-theming/
# https://docs.streamlit.io/en/stable/theme_options.html
# layout de colunas
# https://blog.jcharistech.com/2020/10/10/how-to-add-layout-to-streamlit-apps/
# https://ichi.pro/pt/visualizacao-de-dados-interativos-python-com-altair-198755622258936
# https://bleepcoder.com/pt/altair/310626175/sort-channel-not-working-when-i-add-text-on-top-of-my-bars
# https://altair-viz.github.io/user_guide/interactions.html
#
# https://docs.streamlit.io/en/stable/api.html#magic-commands
# https://docs.streamlit.io/en/latest/streamlit_configuration.html#view-all-configuration-options
# https://blog.streamlit.io/introducing-new-layout-options-for-streamlit/
# lista de emojis: https://raw.githubusercontent.com/omnidan/node-emoji/master/lib/emoji.json

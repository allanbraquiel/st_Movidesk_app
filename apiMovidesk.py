import warnings
import pandas as pd
import requests
from pandas import json_normalize
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

warnings.filterwarnings('ignore')


# Esta função consome a API do Movidesk, faz as transformações no conjunto de dados e retorna um arquivo .xlsx
def etl():
    # Registros de 2020
    def request_movidesk20():
        resposta_2020 = requests.get(
            "https://api.movidesk.com/public/v1/tickets?token=a0ea48b9-a491-4e9e-97e1-dfb7ffdc3fcc&$select=id,type,"
            "subject,origin,actionCount,createdDate,createdBy,clients,category,urgency,lastActionDate,closedIn,"
            "status,justification,&$expand=owner($select=businessName),createdBy($select=businessName),"
            "clients($select=organization;$expand=organization($select=businessName))&filter=createdDate ge "
            "2020-01-01T00:00:00.00z&$top=921 "
        )
        return resposta_2020.json()

    # Registros de 2021
    def request_movidesk21():
        resposta_2021 = requests.get(
            "https://api.movidesk.com/public/v1/tickets?token=a0ea48b9-a491-4e9e-97e1-dfb7ffdc3fcc&$select=id,type,"
            "subject,origin,actionCount,createdDate,createdBy,clients,category,urgency,lastActionDate,closedIn,"
            "status,justification,&$expand=owner($select=businessName),createdBy($select=businessName),"
            "clients($select=organization;$expand=organization($select=businessName))&$filter=createdDate gt "
            "2021-01-01T00:00:00.00z&$top=992"
        )
        return resposta_2021.json()

    # Registros de 2022
    def request_movidesk22():
        resposta_2022 = requests.get(
            "https://api.movidesk.com/public/v1/tickets?token=a0ea48b9-a491-4e9e-97e1-dfb7ffdc3fcc&$select=id,type,"
            "subject,origin,actionCount,createdDate,createdBy,clients,category,urgency,lastActionDate,closedIn,"
            "status,justification,&$expand=owner($select=businessName),createdBy($select=businessName),"
            "clients($select=organization;$expand=organization($select=businessName))&$filter=createdDate gt "
            "2021-11-29T00:00:00.00z "
        )
        return resposta_2022.json()

    # Usando o json_normalize (esta função entra dentro da estrutura do json)
    df20 = json_normalize(request_movidesk20())
    df21 = json_normalize(request_movidesk21())
    df22 = json_normalize(request_movidesk22())

    # Unificnado os arquivos
    df = pd.concat([df20, df21, df22])

    # Mesmo após usar o json normalize a coluna "clients" não não foi carregada corretamente,
    # então vamos usar uma função para criar uma nova
    # coluna extraindo a informação desta coluna para retirar o nome da empresa

    def empresa(item):
        if "ABDI" in str(item):
            return "ABDI"
        elif "EMGETIS" in str(item):
            return "EMGETIS"
        elif "TCE - MS" in str(item):
            return "TCE - MS"
        elif "SEBRAE - MS" in str(item):
            return "SEBRAE - MS"
        elif "CREA - RJ" in str(item):
            return "CREA - RJ"
        elif "MÚTUA" in str(item):
            return "MÚTUA"
        elif "CNSESI" in str(item):
            return "CNSESI"
        elif "PGE - SP" in str(item):
            return "PGE - SP"
        elif "Prevcom" in str(item):
            return "PREVCOM"
        elif "Dataeasy" in str(item):
            return "DATAEASY"
        elif "ELETROBRAS - AMAZONAS" in str(item):
            return "ELET. - AMAZONAS"
        elif "SEBRAE - BA" in str(item):
            return "SEBRAE - BA"
        elif "VERT" in str(item):
            return "VERT"
        elif "PREFEITURA DE SÃO LUÍS" in str(item):
            return "PREF. DE SÃO LUÍS"
        elif "SEBRAE - CE" in str(item):
            return "SEBRAE - CE"
        elif "SEBRAE - PE" in str(item):
            return "SEBRAE - PE"
        elif "SEBRAE - TO" in str(item):
            return "SEBRAE - TO"
        elif "SEBRAE - AC" in str(item):
            return  "SEBRAE - AC"
        elif "SANEAGO" in str(item):
            return "SANEAGO"
        elif "FIETO" in str(item):
            return "FIETO"
        elif "SERPRO" in str(item):
            return "SERPRO"
        elif "RORAIMA ENERGIA" in str(item):
            return "RORAIMA ENERGIA"
        elif "REDEMOB" in str(item):
            return "REDEMOD"
        elif "EQUATORIAL PIAUI" in str(item):
            return "EQUATORIAL PIAUI"
        elif "ELETROBRAS - RONDONIA" in str(item):
            return "ELETROBRAS - RONDONIA"
        elif "ELETROBRAS - ACRE" in str(item):
            return "ELETROBRAS - ACRE"
        elif "IT2B" in str(item):
            return "IT2B"

        else:
            return "Sem empresa"

    df["Empresa"] = df["clients"].apply(empresa)

    # Separando a data das horas
    df["Data"] = df['createdDate'].str.partition('T')[[0]]
    df["closedIn"] = df['closedIn'].str.partition('T')[[0]]
    df["lastActionDate"] = df['lastActionDate'].str.partition('T')[[0]]

    # Alterando o formato da coluna Data para Ano/Mes/Dia
    df['Data'] = pd.to_datetime(df['Data'], format="%Y-%m-%d")

    # Alternado o formato das colunas closedIn e lastActionDate para datetime
    df['closedIn'] = pd.to_datetime(df['closedIn'], format="%Y-%m-%d")
    df['lastActionDate'] = pd.to_datetime(df['lastActionDate'], format="%Y-%m-%d")

    # Tipo do ticket: 1 = Interno 2 = Público.
    def tipo_ticket(item):
        if item == 1:
            return "Interno"
        else:
            return "Publico"

    df["type"] = df["type"].apply(tipo_ticket)

    # Nomeando a origem dos tickets
    def origem_ticket(item):
        if item == 1:
            return "Cliente"
        elif item == 2:
            return "Agente"
        elif item == 5:
            return "Chat Online"
        elif item == 3:
            return "Email"
        elif item == 6:
            return "Chat Offline"
        elif item == 8:
            return "Fórmulário"

    # Definindo a origem dos tickets
    df["origin"] = df["origin"].apply(origem_ticket)

    # Renomeando as colunas
    df.rename(columns={'justification': "Justificativa", 'status': "Status",
                       'closedIn': "DataFechamento", 'lastActionDate': "DataUltimaAcao",
                       'urgency': "Urgencia", 'category': "Categoria", "origin": "Origem", 'subject': "Assunto",
                       'type': "Tipo", 'actionCount': "ContagemAções", 'id': "Ticket",
                       'createdBy.businessName': "Cliente",
                       'owner.businessName': "Responsavel"}, inplace=True)

    # Excluindo as colunas que não serão mais utilizadas
    df.drop(columns=["createdDate", "clients"], inplace=True)

    # Criando uma coluna de Mês e dia
    df["Mes"] = df["Data"].dt.month
    df["Dia"] = df["Data"].dt.day
    df['MesNome'] = pd.to_datetime(df['Mes'], format='%m').dt.month_name().str.slice(stop=3)
    df["DiaSemana"] = df.Data.dt.day_name()

    # df['Data'] = df['Data'].dt.strftime("%Y/%m/%d")

    # Caso haja algum ticket sem responsável será alterado para não informado
    df["Responsavel"] = df["Responsavel"].fillna("Não Informado")

    # Encurtando os nomes dos Reponsáveis deixando somente o primeiro nome
    def abrevia_nome(nome):
        resultado = nome.split()[0]
        return resultado

    # Aplicando a função de abreviar o nome
    df["Responsavel"] = df["Responsavel"].apply(abrevia_nome)

    # Reduzindo os caracteres do assunto
    def limita_assunto(assunto):
        limite = assunto[0:150]
        return limite

    # Redefine o campo assunto com apenas 150 caracteres
    df["Assunto"] = df["Assunto"].apply(limita_assunto)

    # função para retirar os espaços em branco no começo e no final
    def tira_espaco(assunto):
        espaco = assunto.strip()
        return espaco

    # Retira os espaços em branco
    df["Assunto"] = df["Assunto"].apply(tira_espaco)

    # Criação de uma coluna com contagem de dias em cada ticket ate o fechamento

    # A data de fechamento possui alguns valores em branco porque os ticket ainda estão abertos
    df["DataFechamento"] = df["DataFechamento"].fillna(datetime.today().strftime('%Y-%m-%d'))
    df['DataFechamento'] = pd.to_datetime(df['DataFechamento'], format="%Y-%m-%d")

    df["QtdeDiasChamado"] = (df["DataFechamento"] - df["Data"]).dt.days

    # Criação de uma coluna com contagem de dias em cada ticket ate a última ação
    df["QtdeDiasUltimaAçao"] = (df["DataUltimaAcao"] - df["Data"]).dt.days

    # Diferença de dias entre a ultima ação e o fechamento
    df["DifUltimaAçaoFechamento"] = (df["DataFechamento"] - df["DataUltimaAcao"]).dt.days

    # Limpando os dados nulos
    df["Categoria"] = df["Categoria"].fillna("Não Categorizado")
    df["Justificativa"] = df["Justificativa"].fillna(" ")
    df["Urgencia"] = df["Urgencia"].fillna("Baixa")


    # Reordenando as colunas
    coluna_ordenada = ['Ticket', 'Tipo', 'Assunto', 'Data', 'Mes', 'MesNome', 'Dia', 'DiaSemana', 'Empresa',
                       'Cliente', 'Responsavel', 'Categoria', 'Urgencia', 'Origem', 'ContagemAções',
                       'DataFechamento', 'DataUltimaAcao', 'QtdeDiasChamado', 'QtdeDiasUltimaAçao',
                       'DifUltimaAçaoFechamento', 'Status', 'Justificativa']

    df = df[coluna_ordenada]

    # qtde_dia = df.groupby(by=["MesNome"])["Ticket"].count()

    """ Criando figuras 
    
    # Criando os gráficos em png
    fig1 = plt.figure(figsize=(18, 8))
    fig1 = sns.lineplot(data=qtde_dia, x="MesNome", y=qtde_dia)
    fig1.figure.savefig("images/fig1.png")
    # fig1.figure.savefig("images/fig1.svg", format="svg", dpi=1200)

    fig2 = sns.catplot(x="Categoria", kind="count", palette="Set2", data=df)
    fig2.fig.set_figwidth(20)
    fig2.fig.set_figheight(10)
    # fig2.fig.savefig("fig2.png")

    fig3 = sns.catplot(x="Origem", kind="count", palette="Set2", data=df)
    fig3.fig.set_figwidth(20)
    fig3.fig.set_figheight(10)
    # fig3.fig.savefig("images/fig3.png")

    # Criando um conjunto de imagens
    lista = ['Tipo', 'Mes', 'Empresa', 'Cliente',
             'Responsavel', 'Categoria', 'Urgencia', 'Origem', 'ContagemAções',
             'Status', 'Justificativa']

    for i in lista:
        g = sns.catplot(y=i, kind="count", palette="Set2", data=df)
        g.fig.set_figwidth(20.27)
        g.fig.set_figheight(8.7)
        g.fig.savefig(f"images/{i}.png")
        
    """

    """
    pp = PdfPages("Relatório.pdf")
    
    pp.savefig(images/fig1)
    pp.savefig(images/fig2)
    pp.close()
    """

    # Resetar o index com a coluna Ticket
    df = df.set_index("Ticket")
    df.to_excel("files/appMovidesk.xlsx")

    # Salvar as transformações em excel
    return df

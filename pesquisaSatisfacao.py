import warnings
import pandas as pd
import requests
from pandas import json_normalize

warnings.filterwarnings('ignore')

# Buscando dados da pesquisa de satisfação

# Devido ao fato de que o request traz no máximo 100 registros, será necessário dividir estas consultas
resposta_Satisfacao_2020_1 = requests.get("https://api.movidesk.com/public/v1/survey/responses?token=a0ea48b9-a491"
                                          "-4e9e-97e1-dfb7ffdc3fcc&responseDateGreaterThan=2020-01-01"
                                          "&responseDateLessThan=2020-09-23")

resposta_Satisfacao_2020_2 = requests.get("https://api.movidesk.com/public/v1/survey/responses?token=a0ea48b9-a491"
                                          "-4e9e-97e1-dfb7ffdc3fcc&responseDateGreaterThan=2020-09-23"
                                          "&responseDateLessThan=2020-12-31")

resposta_Satisfacao_2021_1 = requests.get("https://api.movidesk.com/public/v1/survey/responses?token=a0ea48b9-a491"
                                          "-4e9e-97e1-dfb7ffdc3fcc&responseDateGreaterThan=2021-01-01"
                                          "&responseDateLessThan=2021-06-30")

resposta_Satisfacao_2021_2 = requests.get("https://api.movidesk.com/public/v1/survey/responses?token=a0ea48b9-a491"
                                          "-4e9e-97e1-dfb7ffdc3fcc&responseDateGreaterThan=2020-07-01"
                                          "&responseDateLessThan=2021-12-31")

# Converter o resultado do request em Dataframe
df_satis_2020_1 = json_normalize(resposta_Satisfacao_2020_1.json(), record_path="items")
df_satis_2020_2 = json_normalize(resposta_Satisfacao_2020_2.json(), record_path="items")
df_satis_2021_1 = json_normalize(resposta_Satisfacao_2021_1.json(), record_path="items")
df_satis_2021_2 = json_normalize(resposta_Satisfacao_2021_2.json(), record_path="items")

# Concatenar todos dataframes em um só
df_satis = pd.concat([df_satis_2020_1, df_satis_2020_2, df_satis_2021_1, df_satis_2021_2])
# print(df_satis.head())

# Eliminando as colunas que não serão necessárias
df_satis.drop(columns=["id", "questionId", "type", "clientId"], axis=1, inplace=True)
# print(df_satis.head())

# Alterando a coluna responseDate para somente a Data
df_satis["responseDate"] = df_satis['responseDate'].str.partition('T')[[0]]

# alterando o formato para Datetime
df_satis["responseDate"] = pd.to_datetime(df_satis["responseDate"], format="%Y/%m/%d")

# Renomeando as colunas
df_satis.rename(columns={'ticketId': "Ticket", 'responseDate': "Data_Resposta",
                         'commentary': "Comentario", 'value': "Valor"}, inplace=True)


df_satis.Comentario = df_satis.Comentario.fillna("Sem comentários")


# função para alterar os valores da coluna de reposta
def valor_resposta(item):
    if item == 1:
        return "Satisfeito"
    else:
        return "Insatisfeito"


# Chamando a função
df_satis["Valor"] = df_satis["Valor"].apply(valor_resposta)
df_satis.head()

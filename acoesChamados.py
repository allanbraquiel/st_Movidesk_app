import requests
from pandas import json_normalize


def consulta_acoes(ticket_input):
    try:
        resposta_unica = requests.get(f"https://api.movidesk.com/public/v1/tickets?token=a0ea48b9-a491-4e9e-97e1"
                                      f"-dfb7ffdc3fcc&id={ticket_input}")
        df_actions = json_normalize(resposta_unica.json(), record_path="actions")
        acoes = df_actions[["createdBy.businessName", "description"]]
        # acoes = df_actions["description"]
        # acoes = df_actions["htmlDescription"].values
        return acoes
    except:
        return "Ticket não encontrado"

import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from easygui import *
from tkinter import *
import tkinter as tk
from tkinter import filedialog

print("Extracting Information:")
animation = ["[■□□□□□□□□□]", "[■■□□□□□□□□]", "[■■■□□□□□□□]", "[■■■■□□□□□□]", "[■■■■■□□□□□]", "[■■■■■■□□□□]",
             "[■■■■■■■□□□]", "[■■■■■■■■□□]", "[■■■■■■■■■□]", "[■■■■■■■■■■]"]

with requests.Session() as s:
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0'}

    # Dados Cadastrais de Fundos de Investimento
    # Estruturados e Não Estruturados (ICVM 555)

    url = 'http://dados.cvm.gov.br/dataset/fi-cad'
    r = s.get(url, headers=headers).content

    soup = BeautifulSoup(r, "html.parser")
    tags = soup('a')

    for tag in tags:
        goal_url = tag.get('href', None)
        if 'csv' in goal_url:

            '''Realizando o download das informações'''
            for i in range(len(animation)):
                time.sleep(0.2)
                sys.stdout.write("\r" + animation[i % len(animation)])
                sys.stdout.flush()

            print("\n")
            print('Iniciando download do arquivo')

            r = s.get(goal_url, headers=headers)

            my_file = 'Info_cadastral.csv'
            with open(my_file, 'w') as file:
                file.write(r.text)

            file.close()

df_cvm = pd.read_csv(my_file, sep=";", encoding="ISO-8859-1", low_memory=False)

# Removing Funds with status = "Cancelada"
df_cvm = df_cvm[(df_cvm['SIT'] != 'CANCELADA')].copy()

df_cvm = df_cvm.drop(['TP_FUNDO', 'CD_CVM', 'DT_CANCEL', 'DT_INI_SIT',
                      'DT_INI_ATIV', 'DT_FIM_EXERC', 'DT_INI_CLASSE',
                      'FUNDO_COTAS', 'FUNDO_EXCLUSIVO', 'TRIB_LPRAZO',
                      'INVEST_QUALIF', 'INF_TAXA_PERFM', 'INF_TAXA_ADM',
                      'VL_PATRIM_LIQ', 'DT_PATRIM_LIQ', 'DIRETOR', 'RENTAB_FUNDO',
                      'CONDOM', 'ENTID_INVEST', 'TAXA_PERFM', 'TAXA_ADM',
                      'CNPJ_CONTROLADOR', 'CNPJ_CUSTODIANTE', 'CNPJ_AUDITOR',
                      'CNPJ_ADMIN', 'PF_PJ_GESTOR', 'CPF_CNPJ_GESTOR'], axis=1)

df_cvm = df_cvm.reset_index(drop=True)
df_cvm.rename(columns={'CNPJ_FUNDO': 'CNPJ'}, inplace=True)
print('Arquivo CSV baixado com sucesso.')

msg = "Na etapa a seguir, você deve importar uma planilha em Excel com o CNPJ dos fundos\
que deseja buscar, lembrando que o título da coluna deve ser 'CNPJ' (Consultar arquivo modelo_consulta.xlsx)"

title = "System Warning"

if ccbox(msg, title):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()

    df_search = pd.read_excel(file_path)
    df_search['CHECK'] = 'EXTRACT'

    goal_link = pd.merge(df_cvm, df_search, on='CNPJ', how='left')
    final = goal_link[(goal_link['CHECK'] == 'EXTRACT')].copy()

    final = final.reset_index(drop=True)
    final.to_excel('OUTPUT_FUND_INFO.xlsx', index=False)

else:
    print('Favor realizar a importação do seu modelo de consulta')
    sys.exit(0)

    
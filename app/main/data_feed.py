import csv
from io import StringIO
import pandas as pd
import pickle
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

try:
    from ...tools import feed
except:
    from tools import feed




def main(file_name:str, verbose:bool = False) -> pd.DataFrame:

    ###  PARAMETROS DE EJECUCION  ###
    descargar_datos = True
    # esto modifica el content #elimina los hashtags y menciones  del content
    eliminar_datos_adicionales = True
    data_desestructurada = False


    ###  GERENCIAMIENTO DE DIRECTORIOS  ###
    file_name = os.path.join(project_root, file_name)



    ###############
    ## DATA FEED ##
    ###############
    # encoding = "Windows-1252"
    # # UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 in position 888: character maps to <undefined>
    ###  Lista de encoding varios: ["Windows-1252", "UTF-8", 'iso-8859-1']

    encoding = "UTF-8"
    lineterminator = '\r'
    sep = ','
    with open(file_name, 'r', encoding=encoding) as file:
        data = file.read().replace('\0', '')

    reader = csv.reader(StringIO(data), delimiter=sep,
                        lineterminator=lineterminator)

    rows = []
    for row in reader:
        rows.append(row)



    ### MODULO DE VERIFICACION DE CONSISTENCIA EN CANTIDAD DE COLUMNAS  ###
    for i, row in enumerate(rows):
        # usar primera fila como referencia
        if i == 0:
            col_len = len(rows[0])
            rows[i] = row
            continue
        # verificar consistencia
        if len(row) == col_len:
            rows[i] = row
        # cortar elementos sobrantes
        else:
            rows[i] = row[:col_len]
            

    ###  CREACION DEL OBJETO pandas.DataFrame  ###
    df = pd.DataFrame(rows[1:], columns=[rows[0]])
    df['content'] = df['content'].astype(str)
    columnas = [col[0] for col in list(df.columns)]    
    df.columns = columnas
    df = df.reset_index(drop=True)

    if verbose:
        print(f"""
    Resumen de la apertura de .csv:

    {feed.data_info(df)}
    """)

    
    return df
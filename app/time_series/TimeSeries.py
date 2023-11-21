import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

import pandas as pd


def main_df(df, conservar_duplicados=False) -> str:

    nombre = df.name
    if not conservar_duplicados:
        df = df.drop_duplicates(subset=["content"], keep="first")
    
    ### PROCESAMIENTO COLUMNAS  ###
    ### OBTENCION INDICE DE TIEMPO  ###
    # verificamos la existencia de la columna 'date'
    # y sinó utilizamos '@timestamp'
    if "@timestamp" in df.columns:
        timeserie_index = df["@timestamp"]
    elif "date" in df.columns:
        print("No encontramos columna @timestamp")
        timeserie_index = df.date
    else:
        print("No se ha encontrado una columna de fecha válida")
        print("Saliendo de time_series/TimeSeries.py")
        print("programa finalizado erróneamente.")
        sys.exit(0)
        
    ### PROCESAMIENTO INDICE DE TIEMPO - AGREGACION ###
    serie_datetime = pd.to_datetime(timeserie_index, format='%b %d, %Y @ %H:%M:%S.%f')

    df["datetime"] = serie_datetime
    # Obtener la columna de fecha como string
    df["date_str"] = serie_datetime.dt.date.astype(str)
    # Obtener la columna de hora como string
    df["time_str"] = serie_datetime.dt.time.astype(str)

    df.name = nombre
    return df

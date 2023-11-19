## Librerias Nativas de Python y de Terceros
import sys, os, time, pickle
import pandas as pd

## Ubicación de los directorios - dirección
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
app_root = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
shared_resources = os.path.join(os.path.abspath(os.path.join(app_root, '..')), "shared_resources")

sys.path.insert(0, project_root)

## Aplicaciones propias
from app.main.main import timeseries
try:
    from app.time_series.main import main as Main
except:
    from main import main as Main

## Libreria propia
from tools.feature_adjust import eliminar_caracteres_no_imprimibles, aplicar_stopwords
from tools.feed import crear_directorio




  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###
###  ###  ###  ###  ###  ###  PROGRAMA PRINCIPAL  ###  ###  ###  ###  ###  ###
  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###
  
  
# if __name__ == "__main__":
def main(file_name:str=None, verbose=False, conservar_duplicados=False) -> str:
    import time
    start = time.time()
    from datetime import datetime

    fecha_hoy = datetime.now().strftime("%m-%d")
    
    if verbose:
        print("Ejecutando time_series/TimeSeries.py\n")

        ## CARGA DE RECURSOS DESDE APP MAIN MAIN
        ## VARIABLES GENERALES
        print("Cargando configuración...")
        #TODO:BUG
        # resources = timeseries()
        # procesamiento_texto = resources["timeserie_procesamiento_texto"]
        #TODO:BUG

    ## EJECUCION DEL MODULO WORDCLOUD MAIN
    if file_name is None:
        df, path_output = Main()
    else:
        df, path_output = Main(file_name=file_name)
    
    nombre = df.name
    if not conservar_duplicados:
        df = df.drop_duplicates(subset=["content"], keep="first")
    
    ### PROCESAMIENTO TOKEN  ###
    if "token" in df.columns:
        token = True
        batch_ = df.token.to_list()
        try:
            batch_token = [row.replace(",", "").replace("#", "").split(" ") for row in batch_]
        except:
            print("La estructura de token recibida, no es la estandar")
        df['token'] = batch_token
        
    ### PROCESAMIENTO COLUMNAS  ###
    # Para reducir la dimensionalidad del dataset
    # se eliminan todas las columnas finalizadas
    # con la palabra '.keyword'
    if not conservar_duplicados:
        columnas = [columna for columna in df.columns if not columna.endswith(".keyword")]
        df = df.loc[:, columnas]
    
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
        exit()
        
    ### PROCESAMIENTO INDICE DE TIEMPO - AGREGACION ###
    # Convertimos el indice de tiempo en 3 columnas
    # date, time, datetime
    # date_str es un str que representa la fecha
    # time_str es un str que representa la hora
    # datetime es el datetime del timestamp
    
    serie_datetime = pd.to_datetime(timeserie_index, format='%b %d, %Y @ %H:%M:%S.%f')

    df["datetime"] = serie_datetime
    # Obtener la columna de fecha como string
    df["date_str"] = serie_datetime.dt.date.astype(str)
    # Obtener la columna de hora como string
    df["time_str"] = serie_datetime.dt.time.astype(str)

    ## GESTION DE DIRECTORIOS DE DESCARGA
    output_dir = shared_resources
    crear_directorio(output_dir, verbose=False)
    
    # sistema, verificar la existencia de archivos de salida previos
    output_files = os.listdir(output_dir)
    output_files = [file for file in output_files if file.startswith(f"dfts_{nombre}_{fecha_hoy}")]
    if len(output_files) == 0:
        N = 1
    else:
        N = [elemento.split("_")[-1] for elemento in output_files]
        N = [elemento.split(".")[0] for elemento in N]
        N = [int(elemento) for elemento in N if elemento.isdigit()]
        N = max(N) + 1

    output_name = f"dfts_{nombre}_{fecha_hoy}_{N}"  
    output_name = os.path.join(output_dir, output_name)    
    
    
    # descargar df en pickle
    with open(output_name+".pickle", "wb") as file:
        pickle.dump(df, file)
    
    if verbose:
        print("programa finalizado de forma exitosa")
    
    return output_name+".pickle"    
    

if __name__ == "__main__":
    print(main(file_name="panorama-economico.csv"))
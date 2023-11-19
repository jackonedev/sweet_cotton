import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)


from app.main.main import timeseries
from tools.feed import crear_directorio, procesar_file_csv, crear_directorio_salida_numerado

def limpieza_txt(path:str, file: str) -> list:
    "Limpieza y apertura básica de archivos en formato .txt"
    with open(os.path.join(path, file), "r", encoding="UTF-8") as file:
        lista = file.read()
        lista = lista.splitlines()
        lista = [palabra.strip() for palabra in lista]
        lista = [palabra for palabra in lista if palabra != ""]
    return lista

def main(file_name:str=None, verbose=False) -> tuple:
    
    if verbose:
        print("Ejecutando time_series/main.py\n")
    resources = timeseries()
    feed = resources["main_feed"]
    # data_process = resources["main_data_process"]
    # preparation = resources["main_preparation"]
    
    ## USER INPUT
    if not file_name:
        file_name = input("> nombre archivo: ")
    
    if not file_name:#dios
        print("Ejecución interrumpida de forma segura.")
        exit()
    

    nombre, archivo = procesar_file_csv(file_name)
    
    if nombre.endswith("_") or nombre.startswith("_"):
        print("Error en el nombre del archivo.")
        raise Exception("El nombre del archivo no puede comenzar ni terminar en _")
    
    elif "_" in nombre:
        print("Warning: Se recomienda no usar _ en el nombre del archivo.")
        print("Se recomienda usar - en su lugar.")
        print("Continúa la ejecución...")
        # La razón de la advertencia es que cuando creamos las versiones de shared_resources
        # el nombre de la versión va a tomar la primera palabra del archivo antes del primer _
        # entonces, carne_total_precio, queda versionada bajo el nombre carne
        # eso puede traer conflictos si tenemos dos archivos que comiencen con la misma palabra
        # por ejemplo, carne_total_precio y carne_total_cantidad
        # para eso se recomienda usar - en su lugar, carne-total-precio y carne-total-cantidad
        
    
    ## PROGRAMA PRINCIPAL
    df = feed(archivo)
    # df = preparation(df, quitar=True, token_config=True)
    # df = data_process(df)
    df = df.reset_index(drop=True)
    df.name = nombre

    ## GESTION DE DIRECTORIOS
    path_out = os.path.join(project_root , "output")
    path_out = os.path.join(path_out, nombre)
    # path_out = crear_directorio_salida_numerado(path_out, verbose=False)

        
    return df, path_out
    
    
if __name__ == "__main__":
    import time
    
    start = time.time()
    df, path = main()
    end = time.time()
    print("Tiempo de ejecución:", round(end-start, 2)) # data-benchmark: 15 segundos
    print(df.head())

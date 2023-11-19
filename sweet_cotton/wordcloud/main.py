import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)


from app.main.main import wordcloud
from tools.feed import crear_directorio, procesar_file_csv, crear_directorio_salida_numerado

def limpieza_txt(path:str, file: str) -> list:
    "Limpieza y apertura básica de archivos en formato .txt"
    with open(os.path.join(path, file), "r", encoding="UTF-8") as file:
        lista = file.read()
        lista = lista.splitlines()
        lista = [palabra.strip() for palabra in lista]
        lista = [palabra for palabra in lista if palabra != ""]
    return lista

def main(file_name:str=None, verbose=True):
    "Ejecución de wordcloud/main.py"
    print("Ejecutando wordcloud/main.py\n")
    resoruces = wordcloud()
    feed = resoruces["main_feed"]
    data_process = resoruces["main_data_process"]
    preparation = resoruces["main_preparation"]
    
    ## USER INPUT
    #TODO: implementar parametro de funcion que reemplace input
    if not file_name:
        file_name = input("> nombre archivo: ")
    
    if not file_name:
        print("Ejecución interrumpida de forma segura.")
        exit()

    nombre, archivo = procesar_file_csv(file_name)
    
    ## PROGRAMA PRINCIPAL
    df = feed(archivo)
    df = data_process(df)
    df = preparation(df, quitar=True)
    df = df.reset_index(drop=True)
    df.name = nombre

    ## GESTION DE DIRECTORIOS
    path_out = os.path.join(project_root , "output")
    path_out = os.path.join(path_out, nombre)
    path_out = crear_directorio_salida_numerado(path_out, verbose=False)
    if verbose:
        print("Directorio de salida:")
        print(path_out)
        
    return df, path_out
    
    
if __name__ == "__main__":
    import time
    
    start = time.time()
    df, path = main()
    end = time.time()
    print("Tiempo de ejecución:", round(end-start, 2)) # data-benchmark: 15 segundos
    print(df.head())

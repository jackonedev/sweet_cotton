import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)


from app.main.main import tokenizador
from tools.feed import crear_directorio, procesar_file_csv


def main(file_name:str=None, verbose = True):
    if verbose:
        print("Ejecutando tokenizadores/main.py\n")
    resources = tokenizador()
    feed = resources["main_feed"]
    preparation = resources["main_preparation"]
    
    if not file_name:
        file_name = input("> nombre archivo: ")
    if not file_name:
        print("Ejecución interrumpida de forma segura.")
        exit()

    nombre, archivo = procesar_file_csv(file_name)
    
    df = feed(archivo)
    df = preparation(df, quitar=True, token_config=True)
    df.name = nombre
    
    return df
    


if __name__ == "__main__":
    df = main()
    df
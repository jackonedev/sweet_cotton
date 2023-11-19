## Bienvenido al programa que integra la implementación de la serie de aplicaciones desarrolladas
import sys, os, pickle
# from matplotlib.pyplot import figure

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
app_root = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
shared_resources_root = os.path.abspath(os.path.join(project_root, "app", 'shared_resources'))
sys.path.insert(0, project_root)

from tools.feed import procesar_file_csv

from app.main import data_feed
from app.tokenizadores import tokenizador_i
from app.word_cloud import WordCloud
from app.word_cloud_V2 import WordCloud as WordCloud_V2
from app.word_cloud.output_analysis import main as Main



def main_df(df, raw=False, verbose=False) -> None:
    "raw: es para indicar si el archivo ya esta tokenizado o no"

    nombre = df.name
    
    nombre, archivo = procesar_file_csv(nombre)
    
    if raw:
        ## ARCHIVO TOKENIZADO
        dftk = tokenizador_i.main(archivo)# para corregir el curso, aquí debería ser tokenizador_i.main_df(df)
        dftk.name = nombre
        print("archivo TK abierto exitosamente")

        ## 2. WordClouds - content + tokens
        # Creo un DataFrame vectorial 1D
        dfwc = dftk[['content']]
        # Creo una lista de tokens
        tokens =  dftk.loc[:, 'tokens_i'].to_list()
        #TODO:
        #WARNING: Se está pisando token ES
        dfwc.loc[:, "token"] = tokens.copy()
    else:
        dfwc = df.copy()

    dfwc.name = nombre
    print("\nCorriendo modulo word_cloud\n")
    nombre_wc = WordCloud.main_df(dfwc)
    Main(nombre_wc)


# def main_df_V2(df) -> figure:
def main_df_V2(dataframe):
    global df

    """Tengo miedo de confiar en las desventajas de Python
    Pero:
        - Puedo usar esta función para agregar columnas al df de forma implícita
    Pero:
        - funciona

    Como me enfrento al miedo, voy a probar con la sentencia global
    En caso que no funcione, la función va a retornar una tupla

    """

    nombre = dataframe.name
    nombre, archivo = procesar_file_csv(nombre)
    
    ## TOKENIZADOR
    df = tokenizador_i.main_df_V2(dataframe)
    df.name = nombre

    # WORDCLOUD
    filtros = []
    result_list = WordCloud_V2.main_df(df, filtros)
    
    return result_list



def main(file_name:str = None, verbose=False) -> None:

    if file_name is None:
        file_name = input("Ingresar nombre archivo: ")

    if not file_name:
        print("Sin nombre de archivo, se cierra programa de forma segura")
        sys.exit(0)

    nombre, archivo = procesar_file_csv(file_name)
    archivo_root = os.path.join(project_root, archivo)

    if not os.path.exists(archivo_root):
        print("El archivo no existe, se cierra programa de forma segura")
        sys.exit(0)

    ## ARCHIVO ELASTIC SEARCH
    df = data_feed.main(archivo_root)
    df.name = nombre
    print("archivo original abierto exitosamente")

    ## ARCHIVO TOKENIZADO
    dftk = tokenizador_i.main(archivo)
    dftk.name = nombre
    print("archivo TK abierto exitosamente")


    ## 2. WordClouds - content + tokens
    dfwc = dftk[['content']]
    tokens =  dftk.loc[:, 'tokens_i'].to_list()
    dfwc.loc[:, "token"] = tokens
    
    print("\nCorriendo modulo word_cloud\n")
    dfwc.name = nombre

    nombre_wc = WordCloud.main_df(dfwc)
    Main(nombre_wc)


if __name__ == "__main__":
    file_name = "octubre-untitled.csv"
    nombre, archivo = procesar_file_csv(file_name)
    file_path = os.path.join(project_root, archivo)
    
    df = data_feed.main(file_path)
    df.name = nombre
    
    res = main_df_V2(df)
    
    print("Done!")

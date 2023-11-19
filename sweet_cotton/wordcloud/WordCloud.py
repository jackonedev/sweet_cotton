## Librerias Nativas de Python y de Terceros
import sys, os
import numpy as np
import pandas as pd
from typing import List
from wordcloud import WordCloud

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

## Aplicaciones propias
from app.main.main import wordcloud as ingest_resources

try:
    from app.word_cloud_V2.main import limpieza_txt
    from app.word_cloud_V2.output_analysis import final_output
except:
    from main import limpieza_txt
    from output_analysis import final_output

## Libreria propia
from tools.feature_adjust import eliminar_caracteres_no_imprimibles, aplicar_stopwords



  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###
###  ###  ###  ###  ###  ###  FUNCIONES PRINCIPALES  ###  ###  ###  ###  ###  ###
  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###

def load_resources():
    global remover_palabra, procesamiento_texto
    global feed, data_process, preparation

    resources = ingest_resources()
    remover_palabra = resources["wordcloud_remover_palabra"]
    procesamiento_texto = resources["wordcloud_procesamiento_texto"]
    feed = resources["main_feed"]
    data_process = resources["main_data_process"]
    preparation = resources["main_preparation"]

#OK
def word_filters_load(path:str, verbose:bool=False) -> list:  
    """
    Carga los filtros desde los recursos locales del sistema
    que se encuentran en el diretorio "word_cloud_config/"
    Devuelve una lista con dos elementos: [filter_1, filter_2]
    
    Filtro 1: palabras que comienzan con
    Filtro 2: palabras a filtrar
    """
    filename = "_epqcc.txt"#eliminar palabras que comienzan con
    if os.path.isfile(os.path.join(path, filename)):
        eliminar_por_comienzo = limpieza_txt(path, filename)
    else:
        print("No se encontró el archivo '_epqcc.txt' en el directorio APP_utils")
        eliminar_por_comienzo = []
    
    filename = "_epw.txt"# eliminar palabras wordcloud
    if os.path.isfile(os.path.join(path, filename)):
        eliminar_palabra = limpieza_txt(path, filename)
    else:
        print("No se encontró el archivo '_epw.txt' en el directorio APP_utils")
        eliminar_palabra = []
    
    if verbose:
        print(f"\nEliminar palabras: {eliminar_por_comienzo}\nFiltrar palabras: {eliminar_palabra}\n")

    return [eliminar_por_comienzo, eliminar_palabra]


#OK  
def word_filtering(df:pd.DataFrame, filter_1:list, filter_2:list) -> pd.DataFrame:
    """
    Función que nos permite aplicar filtros de palabra de forma manual, por medio de archivos .txt en el directorio /word_cloud_config/
    """
    assert "content_cleaned" in df.columns, "df debe tener una columna content_cleaned"
    
    ###  PROCESAMIENTO BATCH CONTENT  ###
    name = df.name
    df = df.copy()
    df.name = name
    batch_content = df.content_cleaned.to_list()
    ## primero limpiamos conservando simbolos
    batch_content = [eliminar_caracteres_no_imprimibles(parrafo, conservar_simbolos=True) for parrafo in batch_content]
    ## eliminamos palabras que comienzan con
    batch_content = remover_palabra(batch_content, filter_1)
    ## volvemos a limpiar quitando simbolos
    batch_content = [eliminar_caracteres_no_imprimibles(parrafo) for parrafo in batch_content]
    ## filtramos palabras configuradas
    batch_content = procesamiento_texto(batch_content, filter_2)
    
    
    df["content_cleaned"] = batch_content
    return df

#OK
def token_aggregation(df):
    name = df.name
    df = df.copy()
    df.name = name
    
    #OK: Actualiza la columna que recibe
    if "token" in df.columns:
        """
        Actualmente identifica la existencia de la columna y la procesa una por una 
        para reemplazar los "-" por None <- de esto no estoy seguro que esté pasando acá
        y también hace limpieza de ["TODOS LOS TOKENS JUNTOS"] -> ["TODOS","LOS","TOKENS","JUNTOS"]
        y también filtra el símbolo de hashtag
        """
        batch_ = df.token.to_list()
        
        if isinstance(batch_[0], list):
            batch_token = df.token.to_list()
        elif isinstance(batch_[0], str):
            # token elastic: [["token1, token2, token3"], ["token4, token5, token6"], "-", ...]
            # return: [["token1", "token2", "token3""],[...],[None], ...]
            
            batch_token = [row.replace(",", "").replace("#", "").split(" ") for row in batch_ if row != "-"]
        else:
            print("WordCloud: Error en la interpretacion de los tokens")
            sys.exit(0)

        batch_token = [item for sublist in batch_token for item in sublist]
        # assertion si batch_token no es una lista de string
        try:
            assert isinstance(batch_token, list), "batch_token no es una lista"
            assert isinstance(batch_token[0], str), "batch_token no es una lista de strings"
        except AssertionError as error:
            print(error)
            print("Continúa la ejeciución")
            
        df["token"] = batch_token
        
    # Setea (default): la columna en la que se van a ejecutar los WC
    if "tokens_i" in df.columns:
        # No se implementan filtros sobre los tokens
        df["token_wc"] = df.tokens_i
    
    # Utiliza el auxiliar
    else:
        df["token_wc"] = df.token
    
    return df


def stop_words_multithread(batch_content, filtros_bool, max_workers):
    pass  

#OK: devuelve una lista de DataFrames
def stop_words_execution(df:pd.DataFrame, filtros_bool:list=None, max_workers:int=4) -> list:
    """
    Esta funcion recibe 3 parámetros: df: pd.DataFrame, filtros:list = None, max_workers:int = 4
    Devuelve una lista de DataFrames: List[pd.DataFrame]
    
    
    Filtros puede ser una lista vacía o None, en ese caso el return es una lista con 1 DataFrame.
    En cuanto se aplican filtros, la longitud del return cambia.
    Solo acepta filtros booleanos.
    Si la lista tiene 1 elemento, ese elemento es un filtro booleano, y si tiene 2 elementos, cada elemento es un filtro booleano, sucesivamente...
    
    Los DataFrame resultantes tienen agregada una columna llamada "content_cleaned", y ahora otra, "content_wc".
    Dicha columna, y "token_wc" son las que procesa "final_output()".
    
    """
    assert "content_cleaned" in df.columns, "df debe tener una columna content_cleaned"
    assert "token_wc" in df.columns, "df debe tener una columna token_wc"
    
    name = df.name
    df = df.copy()
    df.name = name
    
    if filtros_bool is None:
        filtros_bool = []
        
    if not len(filtros_bool) > 0:
        batch_content = aplicar_stopwords(df.content_cleaned.to_list())
        df["content_wc"] = batch_content
        #TODO: # assert isinstance(df.name, str), "se pierde el nombre"
        dataframes = [df]
    else:#TODO
        print("no está implementado")
        sys.exit(0)
        batch_content = stop_words_multithread(batch_content, filtros_bool, max_workers)
        # multithread; va a ser necesario ordenar los sub-batches del output
    return dataframes



##############################################################################
##############################################################################
##############                PROGRAMA PRINCIPAL                ##############
##############################################################################
##############################################################################

def main_df(df:pd.DataFrame, filtros=None, max_workers=4):# -> List[List[pd.DataFrame], List[WordCloud], List[np.array]]:
    global dataframes
    """
    PROCESOS:
    
    1. Preprocesamiento:
    - Se cargan los recursos enviados desde main/main.py
    - 1er procesamiento: eliminar duplicados del content
    - Se ejecuta preprocesamiento
    def token_aggregations()
    - 2do: procesamiento de los tokens existentes -> token_wc
    - 3ro: filtrado de palabras -> content_cleaned
    - 4to: implementar stop_words -> content_wc
    
    2. Agregaciones en el dataset:
    - todo lo relacionado al proceso de tokenizacion
    - content_wc y token_wc
    
    3. Almacenamiento Instanciación objeto tipo wordcloud.wordcloud.WordCloud
        - el objetivo es brindarle al user acceso a la imagen del wordcloud
        por medio del método .to_image()
        
    4. Almacenamiento de los Array obtenidos por el wordcloud
        - Se hace a través del método .to_array(), y también existe 
        el método .to_svg()
        
    RETURN:
    - List[dataframes, wordcloud_storage, arrayfield_storage]
    - dataframes: List[pd.DataFrame]
    - wordcloud_storage: List[wordcloud.wordcloud.WordCloud]
    - arrayfield_storage: List[wordcloud.wordcloud.WordCloud.to_array()]
   
    """
    load_resources()

    name = df.name
    df = df.copy()
    df.name = name


    df = df.drop_duplicates(subset=["content"], keep="first")
    df.name = name

    # verificar que df tenga name
    df = token_aggregation(df)

    # Recibe una lista de str,y el path donde se encuentran ambos archivos txt (nombres hardcodeados)
    path_utils = os.path.join(project_root, "word_cloud_config")
    df = word_filtering(df, *word_filters_load(path_utils))

    dataframes = stop_words_execution(df)#, filtros, max_workers)

    # CAMBIAR ESTRUCTURA: List[pd.DataFrame] -> List[wordcloud.WordCloud]
    wordcloud_storage = final_output(dataframes)

    # CAMPO VECTORIAL    
    # arrayfield_storage = [wcs.to_array() for wcs in wordcloud_storage]
    # pd.Series(array_wc.flatten()).value_counts()
    
    print(f"{__name__} ended succesfully.")
    return [dataframes, wordcloud_storage]#, arrayfield_storage]

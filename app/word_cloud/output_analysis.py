## Librerias Nativas de Python y de Terceros
from copy import copy
import sys
import os
import ast
from pathlib import Path
from wordcloud import WordCloud
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
from typing import List


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
path_config = os.path.join(project_root, "word_cloud_config")
sys.path.insert(0, project_root)


## Aplicaciones propias
from app.main.main import wordcloud as WC
try:
    from app.word_cloud.main import limpieza_txt
    from app.word_cloud.schemas.config_mascara import WordCloudConfig
except:
    from main import limpieza_txt
    from schemas.config_mascara import WordCloudConfig


def load_resources():
    global remover_palabra, filtrado_palabras
    global content_wc, token_wc
    global content_wc_II, token_wc_II
    global content_wc_III, token_wc_III

    resources = WC()
    remover_palabra = resources["wordcloud_remover_palabra"]
    filtrado_palabras = resources["wordcloud_filtrado_palabras"]

def load_configuration_file(path_config: str, names: list) -> dict:
    global mascara_wordcloud
    #  LOAD CONFIGURATION FROM LOCAL FILE
    # Create wc_params dict from txt file
    with open(os.path.join(path_config,"mascaras_png", "wordcloud_mask_config.txt"), "r", encoding="UTF-8") as file:
        wc_params = file.read()
    # CONFIGURATION STRUCTURE VALIDATION
    try:
        wc_params = ast.literal_eval(wc_params)
        wc_params["mascara"] = Path(os.path.join(path_config, 'mascaras_png', wc_params["mascara"]))

        ## PYDANTIC VALIDATION SCHEMA 
        validation_schema = WordCloudConfig(**wc_params)
        try:# (for V1)
            wc_parmams = validation_schema.dict()
        except:# (and V2)
            wc_parmams = validation_schema.model_dump()
    except Exception as e:
        print("Error en el formato del archivo de configuración.")
        print(e)
        print("Ejecución interrumpida.")
        sys.exit(0)
    # Open .png file with mask shape
    #TODO: reeplace for contex manager
    try:
        print(f"Implementando configuración con Máscara: {wc_params['mascara']}")
        mascara_wordcloud = np.array(Image.open(wc_params["mascara"]))
        wc_params.pop("mascara")
        
    except FileNotFoundError as e:
        print("ERROR DE SISTEMA: Colocar un archivo .png con una mascara en tamaño deseado en la carpeta de configuracion")
        sys.exit(0)
        
    # Personalized configurations
    wc_params_storage = {}
    for name in names:
        default_wc_params = copy(wc_params)
        # Default configuration in function of pd.DataFrame(...).name attribute
        if name.split("-")[-1] in ["positive", "negative"]:
            if name.split("-")[-1].startswith("positive"):
                default_wc_params["color_func"] = (84, 179, 153)
            elif name.split("-")[-1].startswith("negative"):
                default_wc_params["color_func"] = (231, 102, 76)
        
        wc_params_storage.update({name:default_wc_params})
    
    return wc_params_storage

def load_filters(path_config):
    """Fuincion que lee los archivos txt de configuracion y devuelve los resultados en una tupla"""
    file = "eliminar_palabras_que_comiencen_con.txt"
    if os.path.isfile(os.path.join(path_config, file)):
        eliminar_palabras = limpieza_txt(path_config, file)
    else:
        print("Warning! Se identifica la ausencia de word_cloud_config/eliminar_palabras_que_comiencen_con.txt")
        eliminar_palabras = []

    file = "eliminar_palabras_wordcloud.txt"
    if os.path.isfile(os.path.join(path_config, file)):
        filtrar_palabras = limpieza_txt(path_config, file)
    else:
        print("Warning! Se identifica la ausencia de word_cloud_config/eliminar_palabras_wordcloud.txt")
        filtrar_palabras = []

    return (eliminar_palabras, filtrar_palabras)

def apply_filters(batch: list, filter_1, filter_2) -> list:
        batch = remover_palabra(batch, filter_1)
        batch = filtrado_palabras(batch, filter_2)

        return batch

def update_wc_colormap(wc_params_storage, nombres):
    global color_tuple, color_func
    """Funcion alternativa "colormap":
    pinta las palabras de distinto color en funcion del tamaño
    para ello debe eliminarse el parámetro por default "color_func"."""
    for name in nombres:
        wc_params = wc_params_storage[name]
        if "colormap" in wc_params.keys() and wc_params["colormap"] != "":
            wc_params.pop("color_func")
        else:
            color_tuple = wc_params["color_func"]
            color_func = lambda *args, **kwargs: color_tuple
            wc_params.pop("color_func")
        
        wc_params_storage[name] |= wc_params

    return wc_params_storage

def wordcloud_content(subbatch, wc_params):
    import random
    #TODO: BORRAR
    with open(f"diccionario de parametros {random.randint(1,999)}.txt", "w") as f:
        f.write(str(wc_params))

    word_cloud = ""
    for row in subbatch:
        row += " "
        word_cloud+= row

    ## Se cambia el mode de RGBA a RGB y se cambia el background color
    # se añaden las lineas de contorno y color del contorno
    wordcloud = WordCloud(
        mask=mascara_wordcloud,
        collocations=False,
        contour_width=1.0,
        **wc_params)
    
    ## si existe colormap. no existe contour
    if not "colormap" in wc_params.keys():
        wordcloud.color_func=color_func
        wordcloud.contour_color = color_tuple
    else:
        wordcloud.contour_color = (0, 0, 0)
    
    return wordcloud.generate(word_cloud)

def wordcloud_token(subbatch:list, wc_params:dict) -> WordCloud:
    word_cloud = ""
    word_cloud = [word_cloud + " ".join(twc) for twc in subbatch]
    word_cloud = " ".join(word_cloud).strip()
    wordcloud = WordCloud(
        mask=mascara_wordcloud,
        collocations=False,
        contour_width=1.0,
        **wc_params)
    if not "colormap" in wc_params.keys():
        wordcloud.color_func=color_func
        wordcloud.contour_color = color_tuple
    else:
        wordcloud.contour_color = (0, 0, 0)
    
    return wordcloud.generate(word_cloud)


def final_output(dataframes:List[pd.DataFrame]=None) -> List[WordCloud]:
    # from app.main.main import wordcloud
    """
    Esta funcion ejecuta la libreria wordcloud,
    devuelve el objeto tipo WordCloud propio de la libreria wordcloud.
    
    Recibe una lista de DataFrames y devuelve una lista de objetos tipo WordCloud
    
    Respecto al nombre de cada DataFrame:
        - si el archivo de apertura se llama, nombre-arhivo_valores_adicionales.extension
        - 'nombre-archivo' siempre será el comienzo
        - ERROR: 'nombre-archivo_{filtered:optional}': el elemento split('_')[1] define la activación del filtro
        - 'nombre-archivo_{}_{sentiment:optional}': el elemento split('_')[-1] define si se aplican valores por default al df
    """
    
    load_resources()

    # Presets    
    nombres = [d.name for d in dataframes]
    wc_params_storage = load_configuration_file(path_config, nombres)
    
    # Batch Creation: batch = [[batch_content, batch_token], ...]
    batch = []
    for i in range(len(nombres)):
        content = dataframes[i].content_wc.to_list()
        token = dataframes[i].token_wc.to_list()
        batch.append([content, token])
    
    # Filtrado: on/off depends on the content of config files
    filtros = load_filters(path_config)
    ## Si los archivos están vacíos no se aplican filtros
    ## Si los archivos poseen contenido, se activan los filtros
    if (len(filtros[0]) + len(filtros[1])) > 0:
        for i in range(len(nombres)):
            print("Filtros .txt detectados - applying filters")
            batch[i][0] = apply_filters(batch[i][0], *filtros)
            batch[i][1] = apply_filters([" ".join(element) for element in batch[i][1]], *filtros)
            batch[i][1] = [element.split(" ") for element in batch[i][1]]
        
    # Wordcloud params update
    wc_params_storage = update_wc_colormap(wc_params_storage, nombres)
    # plt.figure(figsize=(20,8))

    # Wordcloud object instanciation
    wordcloud_storage = []
    for i, name in enumerate(nombres):
        wc_content = wordcloud_content(batch[i][0], wc_params_storage[name])
        wc_token = wordcloud_token(batch[i][1], wc_params_storage[name])
        wordcloud_storage.append([wc_content, wc_token])

    # Wordcloud config backup
    try:# recomposition of the original configuration
        wc_params_storage[nombres[0]]["color_func"] = color_tuple
    except:
        pass

    output_name = nombres[0].split("-")[:-1]#TODO#TODO# REEMPLAZAR esta lógica por algúna que matchee las palabras en comun que tengan dos frames
    with open(os.path.join(path_config,"mascaras_png", f"{output_name}.txt"), 'w', encoding="UTF-8") as f:
        f.write(str(wc_params_storage[nombres[0]]))
        
    print(f"{__name__} ended succesfully!")
    return wordcloud_storage

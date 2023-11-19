import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)


try:
    import data_feed
    import data_preparation
    import creacion_features
    import shared_resources_feed
    # print("Bloque de ejecución local")
except:
    # print("Bloque de ejecución cuando es importado")
    import app.main.data_feed as data_feed
    import app.main.data_preparation as data_preparation
    import app.main.creacion_features as creacion_features
    import app.main.shared_resources_feed as shared_resources_feed

import pandas as pd
from typing import Union

### 
###     BIENVENIDO AL MODULO PRINCIPAL DE LA APP.MAIN 
###

# CENTRO DE DISTRIBUCION DE RECURSOS

def m1_sentiment():
    resources = {
        "shared_resources_feed": shared_resources_feed,
    }
    return resources

def m2_emotions():
    pass

def m3_emotions():
    pass

def timeseries():
    resources = {
        "main_feed": data_feed.main,
        "main_data_process": data_preparation.main,
        "main_preparation": data_preparation.preprocesamiento,
        "timeserie_procesamiento_texto": creacion_features.procesamiento_texto_ii
    }
    return resources

def wordcloud():
    resources = {
        "main_feed": data_feed.main,
        "main_data_process": data_preparation.main,
        "main_preparation": data_preparation.preprocesamiento,
        "wordcloud_procesamiento_texto": creacion_features.procesamiento_texto,
        "wordcloud_remover_palabra": creacion_features.remover_palabras,
        "wordcloud_identificar_relevantes": creacion_features.identificar_relevantes,
        "wordcloud_filtrado_palabras": creacion_features.filtrado_palabras,
    }
    
    return resources



def tokenizador():
    resources = {
        "main_feed": data_feed.main,
        "main_preparation": data_preparation.preprocesamiento,
    }
    return resources





# def main_function(input: Union[str, None] = None) -> pd.DataFrame:

#     if input is None:
#         user_input = input("> nombre archivo: ")
#     else:
#         user_input = input

#     if user_input.endswith(".csv"):
#         nombre = user_input[:-4]
#         archivo = user_input
#     else:
#         nombre = user_input
#         archivo = user_input + ".csv"

#     df_cruda = data_feed.main(archivo)
#     df_limpia = data_preparation.main(df_cruda)
#     df = data_preparation.preprocesamiento(df_limpia, quitar=True)


#     return df

    

# # Tu código principal aquí
# if __name__ == "__main__":
#     # Este archivo no está pensado para ejecutarse desde el main
#     # Aquí puedes empezar a usar las clases y funciones de los módulos importados.
#     print(f"project_root: {project_root}")
#     print("\nFinalizada de forma exitosa la ejecución del main app\n")

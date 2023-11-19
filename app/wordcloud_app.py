import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from tools.feed import procesar_file_csv

from app.main import data_feed
from app.tokenizadores import tokenizador_i
from app.word_cloud import WordCloud as WC
# from app.wordcloud.output_analysis import main as Main



def main_df(dataframe):
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
    result_list = WC.main_df(df, filtros)
    
    return result_list




if __name__ == "__main__":
    file_name = "octubre-untitled.csv"
    nombre, archivo = procesar_file_csv(file_name)
    file_path = os.path.join(project_root, archivo)
    
    df = data_feed.main(file_path)
    df.name = nombre
    
    res = main_df(df)
    
    print("Done!")

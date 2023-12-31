import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from tools.feed import procesar_file_csv

from app.main import data_feed
from app.tokenizadores import tokenizador_i
from app.word_cloud import WordCloud as WC



def main_df(dataframe, filtros:dict=None):
    global df

    """
    TODO: 

    """

    nombre = dataframe.name
    nombre, archivo = procesar_file_csv(nombre)
    
    ## TOKENIZADOR
    if not "tokens_i" in dataframe.columns:
        df = tokenizador_i.main_df_V2(dataframe)
    else:
        df = dataframe
    df.name = nombre
    
    # WORDCLOUD
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

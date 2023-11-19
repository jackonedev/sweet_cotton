import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


import pickle
import pandas as pd
import multiprocessing as mp


from tools.feed import procesar_file_csv
from app.main import data_feed
from app.m1_sentiment import M1_sentiment, M1_sentiment_ii, M1_sentiment_iii
from app.m2_emotions import M2_emotions
from app.m3_emotions import M3_emotions


def run_func(func, args, results):
    results.append(func(args[0]))

def main_transformers(df:pd.DataFrame):
    nombre = df.name
    parallel_funcs = [main_df_M2, main_df_M3]
    
    def run_processes(funcs: list, dataframe):
        "Multiprocesos, paralelismo: Ejecuta multiples funciones, con el mismo argumento"
        # assert isinstance(dataframe, type(pd.DataFrame()))
        
        if len(funcs) > 4:
            print("La función asignará un proceso por cada función")
            print("simultáneamente, sin lista de espera.")
            print("Error de developer. Límite máximo de funciones es 4.")
            raise SystemError
        
        with mp.Manager() as manager:
            results = manager.list()
            operations = []
            for func in funcs:
                process = mp.Process(target=run_func, args=(func, (dataframe,), results))
                process.start()
                operations.append(process)
            for op in operations:
                op.join()
            
            return list(results)

    result = run_processes(parallel_funcs, df)
    # result.name = nombre
    with open(f"_{__name__}_results.pkl", "wb") as f:
        pickle.dump(result, f)
    return result










def main_df_M1(args):
    m1 = M1_sentiment
    return m1.main_df(args)

def main_df_M2(args):
    m2 = M2_emotions
    return m2.main_df(args)

def main_df_M3(args):
    m3 = M3_emotions
    return m3.main_df(args)






if __name__ == "__main__":
    
    mp.freeze_support()
    
    file_name = "octubre-untitled.csv"
    nombre, archivo = procesar_file_csv(file_name)
    file_path = os.path.join(project_root, archivo)
        
    df = data_feed.main(file_path)
    df.name = nombre



    output = main_transformers(df)
    print("Done!")





def main_from_local(file_name:str = None, verbose=False, backup=True) -> pd.DataFrame:

    def obtener_dfts(file_name:str =None) -> pd.DataFrame:
        
        if file_name is None:
            file_name = input("Ingresar nombre de archivo: ")


        if not file_name:
            print("Sin input, se cierra programa de forma segura")
            sys.exit(0)
        
        nombre, archivo = procesar_file_csv(file_name)
        archivo_root = os.path.join(project_root, archivo)

        if not os.path.exists(archivo_root):
            print("El archivo no existe, se cierra programa de forma segura")
            sys.exit(0)


        ## ARCHIVO TIMESERIES
        dfts_path = TimeSeries.main(archivo)
        with open(dfts_path, "rb") as file:
            dfts = pickle.load(file)
            # print("archivo TS abierto exitosamente")

        dfts.name = nombre
        return dfts
    
    dfts = obtener_dfts(file_name)
    nombre = dfts.name
    print("archivo TS abierto exitosamente")
    df_1 = M1_sentiment.main_df(dfts)
    print("Modelo 1 ejecutado exitosamente")
    ## Estos dos modelos de abajo podrían correr en pararlelo
    df_2 = M2_emotions.main_df(dfts, verbose=verbose)
    print("Modelo 2 ejecutado exitosamente")
    df_3 = M3_emotions.main_df(dfts, verbose=verbose)
    print("Modelo 3 ejecutado exitosamente")
    
    
    dfts = dfts.reset_index(drop=True)

    df_1 = df_1.filter(["sentiment_i", "score_sentiment_i"]).reset_index(drop=True)
    df_2 = df_2.reset_index(drop=True)
    df_3 = df_3.reset_index(drop=True)
    
    result = pd.concat([dfts, df_1, df_2, df_3], axis=1)

    ## Reemplazo de las etiquetas Neutral por la segunda opción más probable
    mask_neutral = (result["emotions_26_max_label"] == "neutral").values
    new_label = [row[0][1] for row in result.loc[mask_neutral,["emotions_26_labels"]].values]
    result.loc[mask_neutral, "emotions_26_max_label"] = new_label
    
    if backup:
        with open(os.path.join(shared_resources_root, f"{nombre}.pickle"), "wb") as file:
            pickle.dump(result, file)
        if verbose:
            print("Predicciones almacenadas exitosamente")

    # si recibe un str, devuelve un file, si recibe obj, return obj
    result.name = nombre
    return result
    

import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


import pickle
import pandas as pd
import multiprocessing as mp

from tools.feed import procesar_file_csv

from main import data_feed
from m1_sentiment import M1_sentiment, M1_sentiment_ii, M1_sentiment_iii
from m2_emotions import M2_emotions
from m3_emotions import M3_emotions


def run_func(func, args, results):
    print(f'Iniciando proceso en paralelo para "{func.__name__}" ...')
    results.append(func(args[0]))

def parallel_excecutions(df:pd.DataFrame, parallel_funcs):
    nombre = df.name
    
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
    #TODO: descarga del tipo backup - debe eliminarse
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


def main_transformers(df):
    
    try:
        nombre = df.name
    except:
        print("Warning: El DataFrame no posee un atributo 'name'")
        
    output = M1_sentiment_iii.main_df(df)
    with open(f"_{__name__}_M1_III.pkl", "wb") as f:
        pickle.dump(output, f)


if __name__ == "__main__":
    
    mp.freeze_support()
    
    file_name = "octubre-untitled.csv"
    nombre, archivo = procesar_file_csv(file_name)
    file_path = os.path.join(project_root, archivo)
        
    df = data_feed.main(file_path)
    # df = df.head(300)
    df.name = nombre
    
    main_transformers(df)
    parallel_funcs = [main_df_M2, main_df_M3]
    print("arrancando predicciones de emociones en paralelo")
    output = parallel_excecutions(df, parallel_funcs)
    print("Done!")

import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


import pickle
import pandas as pd
import multiprocessing as mp

from tools.feed import procesar_file_csv


try:
    from app.main import data_feed
    from app.m1_sentiment import M1_sentiment, M1_sentiment_ii, M1_sentiment_iii
    from app.m2_emotions import M2_emotions
    from app.m3_emotions import M3_emotions
except:
    from main import data_feed
    from m1_sentiment import M1_sentiment, M1_sentiment_ii, M1_sentiment_iii
    from m2_emotions import M2_emotions
    from m3_emotions import M3_emotions


def run_func(func, args, results):
    print(f'Iniciando proceso en paralelo para "{func.__name__}" ...')
    with open("Los_args.pkl", "wb") as f:
        pickle.dump(args, f)
    results.append(func(*args))

def parallel_excecutions(df:pd.DataFrame, target, parallel_funcs):
    nombre = df.name
    
    def run_processes(funcs: list, *args):
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
                process = mp.Process(target=run_func, args=(func, args, results))
                process.start()
                operations.append(process)
            for op in operations:
                op.join()
            
            return list(results)

    result = run_processes(parallel_funcs, df, target)
    # result.name = nombre
    return result


def main_df_M1_I(*args):
    m1 = M1_sentiment
    return m1.main_df(*args)
def main_df_M1_II(*args):
    m1 = M1_sentiment_ii
    return m1.main_df(*args)
def main_df_M1_III(*args):
    m1 = M1_sentiment_iii
    return m1.main_df(*args)

def main_df_M2(*args):
    m2 = M2_emotions
    return m2.main_df(*args)

def main_df_M3(*args):
    m3 = M3_emotions
    return m3.main_df(*args)


def main_transformers(df, target):
    
    try:
        nombre = df.name
    except:
        print("Warning: El DataFrame no posee un atributo 'name'")
        
    print("Arrancando predicciones de Sentimiento en paralelo")
    parallel_funcs = [main_df_M1_I, main_df_M1_II, main_df_M1_III]
    sentiment = parallel_excecutions(df, target, parallel_funcs)
    
    print("Arrancando predicciones de Emociones en paralelo")
    parallel_funcs = [main_df_M2, main_df_M3]
    emotions = parallel_excecutions(df, target, parallel_funcs)
    
    outputs =  [sentiment, emotions]
    #TODO: descarga del tipo backup - debe eliminarse
    with open(f"{__name__}-outputs.pkl", "wb") as f:
        pickle.dump(outputs, f)
    results = [pd.concat(sublista, axis=1) for sublista in outputs]
    results = pd.concat(results, axis=1)
    results = results.dropna()
    return results


if __name__ == "__main__":
    
    mp.freeze_support()
    
    file_name = "octubre-untitled.csv"
    nombre, archivo = procesar_file_csv(file_name)
    file_path = os.path.join(project_root, archivo)
        
    df = data_feed.main(file_path)
    # print(f'La forma de df es {df.shape}')
    df = df.head(351)
    df.name = nombre
    
    results = main_transformers(df, target="@timestamp")
    print("Done!")
    #TODO: descarga del tipo backup - debe eliminarse
    with open(f"{__name__}-test.pkl", "wb") as f:
        pickle.dump(results, f)
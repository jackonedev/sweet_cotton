import sys, os, time, concurrent
import pandas as pd
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from datasets import Dataset
from tqdm import tqdm
import numpy, pickle
import torch
from typing import Any

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
app_root = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
sys.path.insert(0, project_root)

# https://github.com/huggingface/transformers/issues/22387





# define data streamer
def data_stream(data:Any, target:str = 'content'):
    try:
        if isinstance(data, list):
            data = pd.DataFrame(data).T
            data.columns = [target]
    except AttributeError:
        assert isinstance(data, pd.DataFrame), "data must be a pandas DataFrame"
    
    dataset = Dataset.from_pandas(data)    
        
    for i in range(dataset.num_rows):
        yield dataset[target][i]




def predictions_features(predicciones:dict, m_datasets:list, max_workers:int) -> pd.DataFrame:
    
    for i in range(len(predicciones)):
        # Ordenamos el output de las predicciones
        resultado = pd.DataFrame(predicciones[i])

        m_datasets[i].loc[:, "max_similarity_i"] = resultado.labels.apply(lambda x: x[0])
        m_datasets[i].loc[:, "similarity_i"] = resultado.labels
        m_datasets[i].loc[:, "score_similarity_i"] = resultado.scores
      
    results = pd.DataFrame()
    for i in range(max_workers):
        results = pd.concat([results, m_datasets[i]])

    results = results.reset_index(drop=True)

    print("Ajuste de las features finalizada.")
    return results



def main_df(df: pd.DataFrame, topicos:list, max_workers:int=4) -> pd.DataFrame:

    start = time.time()

    MODEL = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


    tokenizer_i = AutoTokenizer.from_pretrained(MODEL)
    model_i = AutoModelForSequenceClassification.from_pretrained(MODEL)
    # model = pipeline("zero-shot-classification", model=model_i, tokenizer=tokenizer_i, device=device)
    model = pipeline("zero-shot-classification", model=model_i, tokenizer=tokenizer_i)

    ## CONFIGURACION DEL DATASET
    content_batch = df.content.to_list()
    nx = len(content_batch) // max_workers
    m_examples = [content_batch[i_antiguo:i] for i_antiguo, i in zip(range(0, len(content_batch), nx), range(nx, len(content_batch)+nx, nx))]
    m_datasets = [df.iloc[i_antiguo:i] for i_antiguo, i in zip(range(0, len(content_batch), nx), range(nx, len(content_batch)+nx, nx)) if i != 0]
    m_datasets = [dataset.reset_index(drop=True) for dataset in m_datasets]

    
    
    ## FUNCION QUE EJECUTA ITERATIVAMENTE EL HILO
    predicciones = {}
    def predecir(inputs, position):
        with torch.no_grad():
            output = model(inputs, topicos, multi_label=True)
            predicciones[position] = output
        print(f"Transformers Nº {position} finalizado")


    print("INICIANDO PREDICCIONES")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for I in range(len(m_examples)):
            print(f"Procesando batch numero: {I+1}")
            futures = {executor.submit(predecir, *(m_examples[I], I)): I}

        for future in concurrent.futures.as_completed(futures):
            i = futures[future]
            try:
                result = future.result()
            except Exception as e:
                print(f"Error in prediction: {e}")
                predicciones[i] = result

    predicciones = dict(sorted(predicciones.items()))
    print("PREDICCIONES COMPLETADAS")
    
    
    end = time.time()
    print(f"tiempo de ejecución: {end - start} segs")

    return predictions_features(predicciones, m_datasets, max_workers)
    

    
    






##########################################################################################################################################
if __name__ == "__main__":
    # start = time.time()
    file_name = "rd-comentarios-facebook.csv"
    df = pd.read_csv(os.path.join(project_root, file_name))


    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    topicos = ["seguridad", "economia", "salud", "educacion", "politica", "medio ambiente", "sociedad", "tecnologia"]


    predicciones = main_df(df, topicos)
    
    predicciones.to_csv("resultados_similarity.csv")
    
    
    print(predicciones)
    print()
    print()

    print("Proceso finalizado exitosamente.")
    
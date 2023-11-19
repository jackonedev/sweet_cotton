import concurrent.futures
from transformers import pipeline
import pandas as pd
import torch
import sys, os, time, pickle
import pandas as pd

## Ubicación de los directorios - dirección
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
app_root = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
shared_resources = os.path.join(os.path.abspath(os.path.join(app_root, '..')), "shared_resources")

sys.path.insert(0, project_root)

try:
    from app.m1_sentiment.main import main as Main
except:
    from main import main as Main

from tools.feed import data_info

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# identificacion de los dispositivos físicos disponibles
try:
    num_gpus = torch.cuda.device_count()
    for ix in range(num_gpus):
        # select the latest recognized gpu
        device_id = f'cuda:{ix}'
        device = torch.device(device_id)
        print(f"GPU disponible, otorgada mediante el id: {device_id}")

except:
    print("Esto debería imprimirse si no existen GPUs disponibles")
    


###   ###   ######   ###   ######   ###   ######   ###   ######   ###   ######   ###   ######   ###   ###
###   ###   ###                                                                         ###   ###   ###
###   ###   ###                         PROGRAMA PRINCIPAL                              ###   ###   ###
###   ###   ###                                                                         ###   ###   ###
###   ###   ######   ###   ######   ###   ######   ###   ######   ###   ######   ###   ######   ###   ###





def main_df(df:pd.DataFrame, max_workers:int=4) -> pd.DataFrame:

    ## IMPLEMENTACION DEL MODELO
    start_i = time.time()
    MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
    content_batch = df.content.to_list()
    nx = len(content_batch) // max_workers
    
    m_examples = [content_batch[i_antiguo:i] for i_antiguo, i in zip(range(0, len(content_batch), nx), range(nx, len(content_batch)+nx, nx))]

    m_datasets = [df.iloc[i_antiguo:i] for i_antiguo, i in zip(range(0, len(content_batch), nx), range(nx, len(content_batch)+nx, nx)) if i != 0]
    m_datasets = [dataset.reset_index(drop=True) for dataset in m_datasets]


    print(f"Ejecutando modelo optimizado con {max_workers} hilos...")
    # print(f"Modelo - clasificación de sentimientos: {MODEL}")
    model = pipeline("sentiment-analysis", model=MODEL, tokenizer=MODEL, device=device, top_k=None)

    predicciones = {}
    def predecir(inputs, position):
        with torch.no_grad():
            output = model(inputs, padding= True, truncation= True, max_length= 512)
            predicciones[position] = output

    OUTPUT = []
    #TODO (!) WARNING (!) Fijate que estás creando un pool por batch y que a cada hilo del pool le haces predecir un solo registro del batch por vez
    for I in range(len(m_examples)):
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(predecir, *(input_ids, i)): i for i, input_ids in enumerate(m_examples[I])}

            for future in concurrent.futures.as_completed(futures):
                i = futures[future]
                try:
                    result = future.result()
                except Exception as e:
                    print(f"Error in prediction: {e}")
                    predicciones[i] = result

        OUTPUT.append(predicciones)

    end_i = time.time()

    print("Tiempo de ejecución del modelo: ", end_i - start_i)
    # print("Ensamble de las predicciones")

    for i in range(len(OUTPUT)):
        # Ordenamos el output de las predicciones
        OUTPUT[i] = dict(sorted(OUTPUT[i].items()))

        ##TODO:DRY
        if device == "cpu":
            resultado = {}
            for value_list in OUTPUT[i].values():
                for value_dict in value_list:
                    for label, score in value_dict.items():
                        resultado.setdefault(label, []).append(score)

            # Actualizamos objeto output
            m_datasets[i].loc[:, "sentiment_i"] = pd.DataFrame(resultado).label
            m_datasets[i].loc[:, "score_sentiment_i"] = pd.DataFrame(resultado).score
        ##TODO:DRY
        else:
        # creamos objeto de predicciones en formato columna
            resultado = {}
            for value_list in OUTPUT[i].values():
                for value_dict in value_list:
                    for label, score in value_dict[0].items():
                        resultado.setdefault(label, []).append(score)

            # Actualizamos objeto output
            m_datasets[i].loc[:, "sentiment_i"] = pd.DataFrame(resultado).label
            m_datasets[i].loc[:, "score_sentiment_i"] = pd.DataFrame(resultado).score
        ##TODO:DRY
        
        
    results = pd.DataFrame()
    for i in range(max_workers):
        results = pd.concat([results, m_datasets[i]])

    results = results.reset_index(drop=True)

    print("Predicción de sentimientos finalizada.")
    return results












# no implementada la correccion
def main_shared_resources(file_name:str=None, max_workers:int=4) -> pd.DataFrame:
    
    # if file_name:
    #     df = Main(file_name)
    # else:
    #     df = Main()
        

    df = Main(file_name) if file_name else Main()

    ## IMPLEMENTACION DEL MODELO
    start_i = time.time()
    MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
    content_batch = df.content.to_list()
    nx = len(content_batch) // max_workers
    
    m_examples = [content_batch[i_antiguo:i] for i_antiguo, i in zip(range(0, len(content_batch), nx), range(nx, len(content_batch)+nx, nx))]

    m_datasets = [df.iloc[i_antiguo:i] for i_antiguo, i in zip(range(0, len(content_batch), nx), range(nx, len(content_batch)+nx, nx)) if i != 0]
    m_datasets = [dataset.reset_index(drop=True) for dataset in m_datasets]
    # # reiniciar indices de cada uno
    # for i, dataset in enumerate(m_datasets):
    #     m_datasets[i] = dataset.reset_index(drop=True)

    print(f"Ejecutando modelo optimizado con {max_workers} hilos...")
    print(f"Modelo - clasificación de sentimientos: {MODEL}")
    model = pipeline("sentiment-analysis", model=MODEL, tokenizer=MODEL, device=device, top_k=None)##TODO TODO TODO TODO: Verificar porque me cambia la estructura de datos del output
    # model = pipeline("sentiment-analysis", model=MODEL, tokenizer=MODEL)

    predicciones = {}
    def predecir(inputs, position):
        with torch.no_grad():
            output = model(inputs, padding= True, truncation= True, max_length= 512)
            predicciones[position] = output

    OUTPUT = []
    for I in range(len(m_examples)):
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(predecir, *(input_ids, i)): i for i, input_ids in enumerate(m_examples[I])}

            for future in concurrent.futures.as_completed(futures):
                i = futures[future]
                try:
                    result = future.result()
                except Exception as e:
                    print(f"Error in prediction: {e}")
                    predicciones[i] = result

        OUTPUT.append(predicciones)

    end_i = time.time()
    
    print("Tiempo de ejecución del modelo: ", end_i - start_i)
    print("Ensamble de las predicciones")
    
    for i in range(len(OUTPUT)):
        
        # Ordenamos el output de las predicciones
        OUTPUT[i] = dict(sorted(OUTPUT[i].items()))
        
        ##TODO:DRY
        if device == "cpu":
            resultado = {}
            for value_list in OUTPUT[i].values():
                for value_dict in value_list:
                    for label, score in value_dict.items():
                        resultado.setdefault(label, []).append(score)

            # Actualizamos objeto output
            m_datasets[i].loc[:, "sentiment_i"] = pd.DataFrame(resultado).label
            m_datasets[i].loc[:, "score_sentiment_i"] = pd.DataFrame(resultado).score
        ##TODO:DRY
        else:
        # creamos objeto de predicciones en formato columna
            resultado = {}
            for value_list in OUTPUT[i].values():
                for value_dict in value_list:
                    for label, score in value_dict[0].items():
                        resultado.setdefault(label, []).append(score)

            # Actualizamos objeto output
            m_datasets[i].loc[:, "sentiment_i"] = pd.DataFrame(resultado).label
            m_datasets[i].loc[:, "score_sentiment_i"] = pd.DataFrame(resultado).score
        ##TODO:DRY
        
    results = pd.DataFrame()
    for i in range(max_workers):
        results = pd.concat([results, m_datasets[i]])

    results = results.reset_index(drop=True)

    print("Predicción de sentimientos finalizada.")
    return results



if __name__ == "__main__":
    main_shared_resources()
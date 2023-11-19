## ESTE ES PORQUE QUIERO PROBAR DE CORRER UN SCRIPT EN CADA TERMINAL EN FORMA SIMULTANEA
# UNA ESPECIA DE OPTIMIZACION MULTI-PROCESOS HECHO DE FORMA MANUAL
import sys, os, time
import pandas as pd
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from datasets import Dataset
from tqdm import tqdm
import numpy, pickle
import torch

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
app_root = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
sys.path.insert(0, project_root)

#warning# Rompiendo el diseño de la arquitectura

try:
    from app.main.shared_resources_feed import menu
except:
    from main.shared_resources_feed import menu

from tools.messure import cronometro

# define data streamer
def data_stream(samples: Dataset, target:str = 'content'):
    for i in range(samples.num_rows):
        yield samples[target][i]




# classifier function with batching option
def classify_tweets(model:pipeline, data:pd.DataFrame, target:str = "content") -> list:

    try:
        if isinstance(data, list):
            data = pd.DataFrame(data).T
            data.columns = [target]
    except AttributeError:
        assert isinstance(data, pd.DataFrame), "data must be a pandas DataFrame"
        


    # convert to huggingface dataset for batching
    dataset = Dataset.from_pandas(data)

    # Classify tweets for each target
    res = []
    for result in model(data_stream(dataset, target=target), padding= True, truncation= True, max_length= 512):
        res.append(result)

    # # recode results to integers
    # for column in tqdm(label_col_names, desc="Re-coding results"):
    #     data.loc[:,column] = data[column].replace(to_replace = {'supports':-1, 'opposes':1, 'does not express an opinion about': 0})
    # # Fill NaN values with zero
    # data[label_col_names] = data[label_col_names].fillna(0)
    # # Create columns for liberal and conservative classifications
    # data[label_columns + '_lib'] = [1 if label <= -1 else 0 for label in data[label_col_names].sum(axis = 1)]
    # data[label_columns + '_con'] = [1 if label >= 1 else 0 for label in data[label_col_names].sum(axis = 1)]
    

    return res


def predictions_features(predictions:list) -> pd.DataFrame:
    # Crear una lista para almacenar los datos de cada columna
    label_columns = []
    score_columns = []
    max_label_column = []

    # Recorrer la lista de predicciones
    for prediction in predictions:
        labels = []
        scores = []
        max_score = 0
        max_label = ''

        # Recorrer cada predicción dentro de la lista
        for pred in prediction:
            label = pred['label']
            score = pred['score']

            labels.append(label)
            scores.append(score)

            # Actualizar la etiqueta con el mayor puntaje
            if score > max_score:
                max_score = score
                max_label = label

        label_columns.append(labels)
        score_columns.append(scores)
        max_label_column.append(max_label)

    # Crear el DataFrame con las columnas correspondientes
    df = pd.DataFrame(
    {
        'sentiment_iii_max_label': max_label_column,
        'sentiment_iii_labels': label_columns,
        'sentiment_iii_scores': score_columns
        }
    )

    return df

@cronometro
def main_df(df: pd.DataFrame, verbose:bool=False) -> pd.DataFrame:

    start = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    MODEL = "lxyuan/distilbert-base-multilingual-cased-sentiments-student"
    tokenizer_i = AutoTokenizer.from_pretrained(MODEL)
    model_i = AutoModelForSequenceClassification.from_pretrained(MODEL)

    pipeline_i = pipeline('text-classification', model=model_i, tokenizer=tokenizer_i, device=device, top_k=None)

    # Realizar predicción y ajustar resultados
    predictions = classify_tweets(pipeline_i, df, target="content")

    predictions = predictions_features(predictions)

    # update dataset
    # df = pd.concat([df, predictions], axis=1)
    
    end = time.time()
    if verbose:
        print(f"tiempo de ejecución: {end - start} segs")
    
    return predictions


if __name__ == "__main__":

    file_name = "octubre-untitled.csv"
    df = pd.read_csv(os.path.join(project_root, file_name))


    predictions = main_df(df, verbose=True)
    # MODEL = "lxyuan/distilbert-base-multilingual-cased-sentiments-student"
    # tokenizer = AutoTokenizer.from_pretrained(MODEL)
    # model = AutoModelForSequenceClassification.from_pretrained(MODEL)

    # pipeline_i = pipeline('text-classification', model=model, tokenizer=tokenizer, device=0, top_k=None)#batch_size=16

    # df = menu()

    # user_input = input("presione N para abortar el proceso, cualquier otra tecla para continuar: ")
    # if user_input.lower() == "n":
    #     print("Ejecución interrumpida de forma segura.")
    #     exit()
    
    # # define targets to be classified and labels to use
    # predictions = classify_tweets(pipeline_i, df, target="content")
    
    # with open("M2_OUTPUT.pickle", "wb") as file:
    #     pickle.dump(predictions, file)
        
    print("Proceso finalizado exitosamente.")
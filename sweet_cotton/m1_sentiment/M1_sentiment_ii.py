import sys, os, time
import torch
import pandas as pd
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from datasets import Dataset
from tqdm import tqdm
import numpy, pickle

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
app_root = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
sys.path.insert(0, project_root)


# #warning# Rompiendo el diseño de la arquitectura
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
    with torch.no_grad():
        for result in model(data_stream(dataset, target=target), padding= True, truncation= True, max_length= 512):#), batch_size = 32):
            res.append(result)

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
        'sentiment_ii_max_label': max_label_column,
        'sentiment_ii_labels': label_columns,
        'sentiment_ii_scores': score_columns
        }
    )

    return df


@cronometro
def main_df(df: pd.DataFrame, verbose:bool=False) -> pd.DataFrame:

    start = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    MODEL = "edumunozsala/bertin_base_sentiment_analysis_es"
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

    # file_name = "RD_fb-cumplevegano-rocio.csv"## Dataset que tiene problemas
    file_name = "RD_fb-cumplevegano-rocio.csv"
    df = pd.read_csv(os.path.join(project_root, file_name))

    # predictions = main_df(df, verbose=True) # FUNCION QUE SE DEBE IMPLEMENTAR CORRECTAMENTE

    df = df.copy()
    df["content"] = df.content.fillna("ELIMINAR")


    MODEL = "edumunozsala/bertin_base_sentiment_analysis_es"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)

    pipeline_i = pipeline('text-classification', model=model, tokenizer=tokenizer, padding= True, truncation= True, max_length= 512)#batch_size=16

    ## APERTURA DE DF DE FORMA MANUAL
    # df = menu()
    # user_input = input("presione N para abortar el proceso, cualquier otra tecla para continuar: ")
    # if user_input.lower() == "n":
    #     print("Ejecución interrumpida de forma segura.")
    #     exit()
    
    # define targets to be classified and labels to use
    predictions = classify_tweets(pipeline_i, df, target="content")
    
    # with open("M2_OUTPUT.pickle", "wb") as file:
    #     pickle.dump(predictions, file)
        
    print("Proceso finalizado exitosamente.")
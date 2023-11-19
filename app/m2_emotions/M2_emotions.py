import sys, os
import torch
import time

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
app_root = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
sys.path.insert(0, project_root)

# modelo 6 emociones: daveni/twitter-xlm-roberta-emotion-es
# emociones: sadness, anger, surprise, joy, disgust, fear + others

#
# ======================================================================================================================
# from transformers import pipeline
# classifier = pipeline("text-classification",model='daveni/twitter-xlm-roberta-emotion-es', top_k=None)
# ======================================================================================================================
# ======================================================================================================================
# ======================================================================================================================
# https://github.com/huggingface/transformers/issues/22387
# Es buenísimo:
# MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli

import pandas as pd
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from datasets import Dataset
from tqdm import tqdm
import numpy, pickle


#warning# Rompiendo el diseño de la arquitectura
try:
    from app.main.shared_resources_feed import menu
except:
    from main.shared_resources_feed import menu



# define data streamer
def data_stream(samples: Dataset, target:str = 'content'):
    for i in range(samples.num_rows):
        yield samples[target][i]




# classifier function with batching option
def classify_tweets(model:pipeline, data:pd.DataFrame, target:str = "content", batching:bool = False) -> list:
    """
    Classify tweets based on given targets and labels using a HuggingFace pipeline.

    Args:
    - targets: list of targets in the data frame that will be classified
    - labels: list of labels that will be passed to the template
    - label_columns: name of the label columns
    - classifier: HuggingFace pipeline object
    - data: pandas DataFrame that contains the tweets to classify
    - batching: whether to use batching or not

    Returns:
    - pandas DataFrame with modified columns

    """

    # # Create label column names # HARDCODED
    # label_col_names = ["sadness", "anger", "surprise", "joy", "disgust", "fear", "others"]

    try:
        if isinstance(data, list):
            data = pd.DataFrame(data).T
            data.columns = [target]
    except AttributeError:
        assert isinstance(data, pd.DataFrame), "data must be a pandas DataFrame"
    
    # vamos a trabajar con 8 batches
    # tamaño de la muestra:
    m = data.shape[0] // 8


    # convert to huggingface dataset for batching
    dataset = Dataset.from_pandas(data)

    # Classify tweets for each target
    res = []
    if batching:
        for result in model(data_stream(dataset, target=target), batch_size=m):
            res.append(result)
    else:
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

def emotions_features(predictions:list) -> pd.DataFrame:
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
        'emotions_6_max_label': max_label_column,
        'emotions_6_labels': label_columns,
        'emotions_6_scores': score_columns
        }
    )

    return df

def main_df(df: pd.DataFrame, verbose:bool=False) -> pd.DataFrame:

    start = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    MODEL = "02shanky/finetuned-twitter-xlm-roberta-base-emotion"
    tokenizer_i = AutoTokenizer.from_pretrained(MODEL)
    model_i = AutoModelForSequenceClassification.from_pretrained(MODEL)

    pipeline_i = pipeline('text-classification', model=model_i, tokenizer=tokenizer_i, device=device, top_k=None)

    # Realizar predicción y ajustar resultados
    predictions = classify_tweets(pipeline_i, df, target="content")

    predictions = emotions_features(predictions)

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
    # MODEL = "02shanky/finetuned-twitter-xlm-roberta-base-emotion"
    # tokenizer = AutoTokenizer.from_pretrained(MODEL)
    # model = AutoModelForSequenceClassification.from_pretrained(MODEL)

    # pipeline_i = pipeline('text-classification', model=model, tokenizer=tokenizer, device=0, top_k=None)#batch_size=16

    # df = menu()
    
    # file_name = df.name

    # user_input = input("presione N para abortar el proceso, cualquier otra tecla para continuar: ")
    # if user_input.lower() == "n":
    #     print("Ejecución interrumpida de forma segura.")
    #     exit()
    
    # # define targets to be classified and labels to use
    # start_i = time.time()
    # predictions_no_batching = classify_tweets(pipeline_i, df, target="content", batching=False)
    # end_i = time.time()
    # predictions = classify_tweets(pipeline_i, df, target="content")
    # end_ii = time.time()
    
    # print(f"Tiempo de ejecución sin batching: {end_i - start_i}")
    # print(f"Tiempo de ejecución con batching: {end_ii - end_i}")
    
    
    # ## MODULO DE GUARDADO DE DATOS
    # #por las dudas
    # # file_name = "".join(file_name.split(".")[0])
    # try:
    #     print("guardando datos... en M2_OUTPUT_{}.pickle".format(file_name))
    #     with open(f"M2_OUTPUT_{file_name}.pickle", "wb") as file:
    #         pickle.dump(predictions, file)
    # except:
    #     with open("M2_OUTPUT.pickle", "wb") as file:
    #         pickle.dump(predictions, file)
    #         print("datos guardados en M2_OUTPUT.pickle")
    
        
    print("Proceso finalizado exitosamente.")
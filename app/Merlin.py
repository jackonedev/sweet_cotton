import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

import random
import pandas as pd
from tools.feature_treatment import create_sparse_feature, resample_dataset_s
from tools.visual_bokeh import fit_data, plot_ratios
from tools.visual_plotly import grafico_torta
from tools.colors import colores
import warnings
warnings.filterwarnings("ignore")



## FILTROS BOOLEANOS PARA WORDCLOUD EN FUNCION DE PREDICCIONES

def filtros_booleanos(df):
    sentiment_model = ["sentiment_i", "sentiment_ii_max_label", "sentiment_iii_max_label"][random.randint(a=0, b=2)]

    if "Positivo" in df[sentiment_model].unique():
        filter_pos = df[sentiment_model].map({"Positivo":True, "Negativo":False})
        filter_neg = df[sentiment_model].map({"Positivo":False, "Negativo":True})
    else:
        filter_pos = df[sentiment_model].map({"positive":True, "negative":False}).fillna(False)
        filter_neg = df[sentiment_model].map({"positive":False, "negative":True}).fillna(False)

    sentiment_filters = {"positive": filter_pos, "negative":filter_neg}

    # Filtro de Emociones

    emotion_6_top2 = df["emotions_6_max_label"].value_counts().head(2).index.to_list()
    emotion_26_top4 = df["emotions_26_max_label"].value_counts().head(4).index.to_list()

    filter_26_top1 = df["emotions_26_max_label"] == emotion_26_top4[0]
    filter_26_top2 = df["emotions_26_max_label"] == emotion_26_top4[1]
    filter_26_top3 = df["emotions_26_max_label"] == emotion_26_top4[2]
    filter_26_top4 = df["emotions_26_max_label"] == emotion_26_top4[3]

    filter_6_top1 = df["emotions_6_max_label"] == emotion_6_top2[0]
    filter_6_top2 = df["emotions_6_max_label"] == emotion_6_top2[1]

    emotion_filters = {
        emotion_6_top2[0]: filter_6_top1,
        emotion_6_top2[1]: filter_6_top2,
        emotion_26_top4[0]: filter_26_top1,
        emotion_26_top4[1]: filter_26_top2,
        emotion_26_top4[2]: filter_26_top3,
        emotion_26_top4[3]: filter_26_top4
    }

    return sentiment_filters | emotion_filters



def obtener_graficos(df):
        
    have_datetime = False
    if "datetime" in df.columns:
        have_datetime = True
        df = df.set_index("datetime").sort_index(ascending=True)

    # sentiment_model = ["sentiment_i", "sentiment_ii_max_label", "sentiment_iii_max_label"][random.randint(a=0, b=2)]
    titulos = ["sentiment","emotion_6","emotion_26"]
    features = ["sentiment_i", "emotions_6_max_label", "emotions_26_max_label"]

    # Radio interno, radio externo del gráfico de dona
    """Los umbrales son distintos: 
        - umbral = 1.05 significa que el gráfico radial va a eliminar las categorías que no superen el 5% de la distancia entre el radio interno y el externo
        - umbral_torta = 1 significa que va a eliminar todas las emociones que tengan menos de 1% de participación en el total de emociones
    """
    ri, re = 90, 360
    umbral = 1.05
    umbral_torta = 0.5 # 0.5% para abajo se borra

    ## Creación de la mascara para implementación de umbral torta + (linea)
    emotion_pct = (df[["emotions_26_max_label"]].value_counts() / df[["emotions_26_max_label"]].value_counts().sum() *100)
    emotion_mask = emotion_pct.values > umbral_torta
    ## boolean array:
    emotion_filter = emotion_pct[emotion_mask].to_frame().reset_index()["emotions_26_max_label"].values
    emotion_sample = df.emotions_26_max_label.isin(emotion_filter).values


    ## crear sparse_matrix
    f_list = [create_sparse_feature(df, feature) for feature in features]
    # Ajustes sobre la feature: emotions_26_max_label
    f_list[-1] = create_sparse_feature(df.loc[emotion_sample, ["emotions_26_max_label"]], features[-1])
    # Ajustes sobre la feature: sentiment_i
    try:
        f_list[0] = f_list[0].drop(columns=["sentiment_i_nan"])
    except:
        pass


    ## CORRECCION LABELS, RENOMBRAR COLUMNAS
    for i, element in enumerate(f_list):
        df_aux = f_list[i]
        df_aux.columns = ["{}_{}".format(elemento.split("_")[-1], i+1) for elemento in df_aux.columns]
        f_list[i] = df_aux


    ## fit_data para gráficos radiales
    f_list_ratios = [fit_data(feature, inner_radius=ri, outer_radius=re, umbral=umbral) for feature in f_list]
    # f11, f21, f31 = f_list_ratios
    if have_datetime:
        f3_12h = resample_dataset_s(f_list[-1], "15T", period="12H")
        f_list = [resample_dataset_s(elemento, "15T") for elemento in f_list]

        f31_12h = fit_data(f3_12h, inner_radius=ri, outer_radius=re, umbral=umbral)
        titulos += ["emotion_26_12h"]
        f_list.append(f3_12h)
        f_list_ratios.append(f31_12h)


    ## seteo de colores
    color_sequence = []
    for ix, feature in enumerate(f_list):
        ix += 1
        # obtener una lista con los keys que terminan con el valor de ix
        keys = [colores[key] for key in colores.keys() if key.endswith(str(ix))]
        
        if len(keys) == 0 and ix > 1:
            keys = last_key
        
        last_key = keys
        color_sequence.append(keys)

    ### Figuras graficos torta
    vf_list_torta = []
    for i in range(3):
        if i == 2:
            vf_list_torta.append(grafico_torta(df.loc[emotion_sample], i, color_sequence=color_sequence[i]))
        else:
            vf_list_torta.append(grafico_torta(df, i, color_sequence=color_sequence[i]))


    ## figures para graficos radiales
    vf_list_ratios = []
    for i, feature in enumerate(f_list_ratios):
        vf_list_ratios.append(plot_ratios(feature, ri, re, title=titulos[i]))


    ## figures para gráfico de linea
    vf_list_line = []

    for i, f in enumerate(f_list):
        if have_datetime:
            vf_list_line.append(f.ewm(span=9).mean().plot(
                kind="line", title=titulos[i], 
                width=1000, height=600, 
                color_discrete_sequence=color_sequence[i],
                template="plotly_dark"))
        else:
            vf_list_line.append(f.ewm(span=55).mean().plot(
                kind="line", title=titulos[i],
                widht=1000, height=600,
                color_discrete_sequence=color_sequence[i],
                template="plotly_dark"))

    return {"linea": vf_list_line, "radiales":vf_list_ratios, "torta": vf_list_torta}





## CORRECCION DE ETIQUETAS PARA MODIFICAR COLORES GRAFICOS
## Correccion de los colores para graficos de torta
correcion_labels_sentiment = {
    "negative": "negative_1",
	"neutral": "neutral_1",
	"positive": "positive_1"
 }

correcion_labels_emotions_6 = {
    "anger": "anger_2",
    "fear": "fear_2",
    "joy": "joy_2",
    "love": "love_2",
    "sadness": "sadness_2",
    "surprise": "surprise_2"
    }

correccion_labels_emotion_26 = {
    "neutral": "neutral_3",
    "approval": "approval_3",
    "realization": "realization_3",
    "caring": "caring_3",
    "curiosity": "curiosity_3",
    "confusion": "confusion_3",
    "disapproval": "disapproval_3",
    "desire": "desire_3",
    "annoyance": "annoyance_3",
    "gratitude": "gratitude_3",
    "excitement": "excitement_3",
    "pride": "pride_3",
    "remorse": "remorse_3",
    "disappointment": "disappointment_3",
    "relief": "relief_3",
    "admiration": "admiration_3",
    "anger": "anger_3",
    "amusement": "amusement_3",
    "embarrassment": "embarrassment_3",
    "joy": "joy_3",
    "surprise": "surprise_3",
    "nervousness": "nervousness_3",
    "love": "love_3",
    "sadness": "sadness_3",
    "grief": "grief_3",
    "disgust": "disgust_3",
    "optimism": "optimism_3",
    "fear": "fear_3"}
import pandas as pd
import numpy as np

def categorizar_standard_i(df):
    umbral = (0, 0.25, 0.5, 1)
    etiqueta = ["nulo", "bajo", "afirmativo"]

    nuevo_data = {}

    for columna in df.columns:
        for i in range(len(umbral) - 1):
            min_umbral = umbral[i]
            max_umbral = umbral[i + 1]
            label = f'{columna}_{etiqueta[i]}'
            nuevo_data[label] = np.where((df[columna] >= min_umbral) & (df[columna] < max_umbral), df[columna], 0.0)

    nuevo_df = pd.DataFrame(nuevo_data)
    return nuevo_df


if __name__ == "__main__":

    data = {'Columna1': [0.1, 0.3, 0.6, 0.9],
            'Columna2': [0.1, 0.2, 0.3, 0.4]}
    
    df = pd.DataFrame(data)
    resultado = categorizar_standard_i(df)
    resultado
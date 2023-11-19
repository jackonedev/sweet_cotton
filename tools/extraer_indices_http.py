import pandas as pd
import re


def extraer_http(data: pd.Series) -> list:
    """Función que devuelve los índices de los registros que contienen la palabra 'http'."""
    # Utilizamos el método str.contains con una expresión regular para buscar 'http'
    mask = data.str.contains(r'http', flags=re.IGNORECASE, regex=True)

    # Devolvemos los índices donde la condición es verdadera
    return data.index[mask].tolist()


def eliminar_https(data: pd.DataFrame, label: str, indices_http: list) -> pd.DataFrame: # TODO: malas prácticas - documentar
    for idx in indices_http:
        content = data.at[idx, label]
        content_sin_http = re.sub(r'http\S+', '', content)
        data.at[idx, label] = content_sin_http

    return data




if __name__ == "__main__":
    # Ejemplo de uso
    data = pd.Series(
        ['me quede solito http://example.com', 'ahttps://www.google.com', 'python', 'HTTP is a protocol'])
    indices_http = extraer_http(data)
    print(indices_http)
    # la funcion no está probada acá
    

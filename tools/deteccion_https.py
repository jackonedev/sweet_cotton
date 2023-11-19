import pandas as pd
import re

def identificar_http(data: pd.Series) -> dict:
    """Función que devuelve un diccionario con los índices de los registros y la lista de usuarios mencionados en el comentario."""
    http_regex = r'(http[s]?:\/\/\S+)'
    http_dict = {}  # Diccionario para almacenar los resultados

    for idx, comentario in enumerate(data):
        https_encontrados = re.findall(http_regex, comentario)
        if https_encontrados:
            assert isinstance(https_encontrados, list), "La función findall debe devolver una lista"
            http_dict[idx] = https_encontrados

    return http_dict


def remover_http(data: pd.Series, menciones: dict) -> pd.Series:
    """Función que elimina los usuarios mencionados de los comentarios."""
    for idx, user in menciones.items():
        for mencion in user:
            data[idx] = data[idx].replace(mencion, '').strip()

    return data

if __name__ == "__main__":
    
    # Ejemplo de uso
    data = pd.Series(['me quede solito http://example.com',
                      'python',
                      'ahttps://www.google.com',
                      'HTTP is a protocol'])

    links = identificar_http(data)
    data = remover_http(data, links)
    print(links)
    print(data)

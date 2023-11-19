import pandas as pd
import re

def extraer_hashtags(data: pd.Series) -> dict:
    """Función que devuelve un diccionario con los índices de los registros y la lista de hashtags encontrados en el comentario."""
    hashtag_regex = r'#(\w+)'
    hashtags_dict = {}  # Diccionario para almacenar los resultados

    for idx, comentario in enumerate(data):
        hashtags_encontrados = re.findall(hashtag_regex, comentario)
        if hashtags_encontrados:
            hashtags_dict[idx] = ['#' + hashtag for hashtag in hashtags_encontrados]

    return hashtags_dict



def eliminar_hashtags(data: pd.Series, hashtags: dict) -> pd.Series:
    """Función que elimina los hashtags de los comentarios."""
    for idx, hashes in hashtags.items():
        for hashtag in hashes:
            data[idx] = data[idx].replace(hashtag, '').strip()

    return data



if __name__ == "__main__":
    # Ejemplo de uso
    data = pd.Series(["#sergiounac  es una burla la salud pública en san juan, hiciste un hospital, el hospital marcial quiroga...",
                      "fuerza bebecito!!!",
                      "#juanvazquezcfp la pregunta es: qué festejan uñac y gioja en san juan? #pepito",
                      "python"])
    
    hash_tags = extraer_hashtags(data)

    data = eliminar_hashtags(data, hash_tags)
    print(hash_tags)
    print(data)



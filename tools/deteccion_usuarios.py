import pandas as pd
import re

def extraer_usuarios(data: pd.Series) -> dict:
    """Función que devuelve un diccionario con los índices de los registros y la lista de usuarios mencionados en el comentario."""
    usuario_regex = r'@(\w+)'
    usuarios_dict = {}  # Diccionario para almacenar los resultados

    for idx, comentario in enumerate(data):
        usuarios_encontrados = re.findall(usuario_regex, comentario)
        if usuarios_encontrados:
            usuarios_dict[idx] = ['@' + usuario for usuario in usuarios_encontrados]

    return usuarios_dict


def eliminar_menciones(data: pd.Series, menciones: dict) -> pd.Series:
    """Función que elimina los usuarios mencionados de los comentarios."""
    for idx, user in menciones.items():
        for mencion in user:
            data[idx] = data[idx].replace(mencion, '').strip()

    return data

if __name__ == "__main__":
    
    # Ejemplo de uso
    data = pd.Series(["@sergiounac  es una burla la salud pública en san juan, hiciste un hospital, el hospital marcial quiroga...",
                      "fuerza bebecito!!!",
                      "@juan_vazquezcfp la pregunta es: qué festejan uñac y gioja en san juan? @pepito",
                      "python"])

    usuarios_tags = extraer_usuarios(data)
    print(usuarios_tags)
    data = eliminar_menciones(data, usuarios_tags)
    print(data)

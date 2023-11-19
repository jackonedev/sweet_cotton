import pandas as pd

def extraer_rt(data: pd.Series) -> list:
    """Función que devuelve los índices de los registros cuyos dos primeros caracteres son 'rt'. La funcion considera que los inputs solo pueden estar en minúsculas"""
    # Utilizamos una expresión lambda para aplicarla a cada elemento de la Serie y verificar los dos primeros caracteres
    
    mask = data.apply(lambda x: str(x).lower()[:2] == 'rt')
    
    # Devolvemos los índices donde la condición es verdadera
    return data.index[mask].tolist()



if __name__ == "__main__":
    # Ejemplo de uso
    data = pd.Series(['http://example.com rt', 'RT https://www.google.com', 'rt python', 'HTTP is a protocol'])
    indices_rt = extraer_rt(data)
    print(indices_rt)

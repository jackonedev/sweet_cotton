import sys
import os
import pandas as pd
import re

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)


from tools.feature_adjust import eliminar_caracteres_no_imprimibles


def filtrado_palabras(data: list, lista_eliminar: list) -> list:
    """Función para filtrar palabras de una lista de strings"""
    
    final_batch = []
    for comentario in data:
        if not isinstance(comentario, str):
            continue
        # Verificar que el twit tenga al menos 2 palabras
        comentario = comentario.strip()
        
        lista_palabras = comentario.split()
        
        # remove empty strings
        if not lista_palabras:
            continue

        # # remove config words
        lista_palabras = [palabra for palabra in lista_palabras if palabra not in lista_eliminar]
        final_batch.append(" ".join(lista_palabras))

    return final_batch

def procesamiento_texto(batch: list, lista_eliminar: list) -> list:
    """Procesamiento (convencional) para comentarios en Twitter
    Elimina palabras por medio de parámetros y realiza limpieza
    
    """
    def tokenize(text):
        tokens = [word for word in text.split(" ")]
        return tokens
    
    final_batch = []
    for comentario in batch:
        if not isinstance(comentario, str):
            continue
        
        # Verificar que el twit tenga al menos 2 palabras
        comentario = comentario.strip()
        # si el comentario tiene 2 palabras o menos se descarta
        
        lista_palabras = comentario.split()
        
        
        # remove digits
        lista_palabras = [palabra for palabra in lista_palabras if not palabra.isdigit()]

        final_batch.append(" ".join(lista_palabras))
        
    ## remove config words
    if bool(lista_eliminar) != False:
        final_batch = filtrado_palabras(final_batch, lista_eliminar)

    return final_batch


def procesamiento_texto_ORIGINAL(batch: list, lista_eliminar: list) -> list:
    """
    Elimina registros durante la limpieza

    Procesamiento (convencional) para comentarios en Twitter
    Elimina palabras por medio de parámetros y realiza limpieza
    
    """
    def tokenize(text):
        tokens = [word for word in text.split(" ")]
        return tokens
    
    final_batch = []
    for comentario in batch:
        if not isinstance(comentario, str):
            continue
        
        # Verificar que el twit tenga al menos 2 palabras
        comentario = comentario.strip()
        # si el comentario tiene 2 palabras o menos se descarta
        tokens = tokenize(comentario)
        if len(tokens) <= 2:
            continue
        
        lista_palabras = comentario.split()
        # remove words with less than 1 characters # río - si y no
        lista_palabras = [palabra for palabra in lista_palabras if len(palabra) >= 2]
        
        # remove empty strings
        if not lista_palabras:
            continue
        # remove digits
        lista_palabras = [palabra for palabra in lista_palabras if not palabra.isdigit()]#TODO: la eliminacion de digitos debe hacerse antes de eliminar los simbolos, cosa de conservar los $120 y 15%

        final_batch.append(" ".join(lista_palabras))
        
    ## remove config words
    if bool(lista_eliminar) != False:
        final_batch = filtrado_palabras(final_batch, lista_eliminar)

    return final_batch

def procesamiento_texto_ii(batch: list, lista_eliminar: list=[], conservar_simbolos=False) -> dict:
    """(Obsoleto) Idéntico a la función superior, pero devuelve un diccionario con índices
    
El uso de esta función fue pensada para wordcloud y conservar la estructura de la data.
La verdad es que es muy dificil sostener la consistencia de la estructura de la data
por lo tanto se utiliza la versión de arriba, que en vez de devolver un diccionario,
devuelve una lista.    
    """
    stopword_batch = {}
    for i, comentario in enumerate(batch):
        if not isinstance(comentario, str):
            continue
        # Verificar que el twit tenga al menos 2 palabras
        comentario = comentario.strip()
        
        comentario = eliminar_caracteres_no_imprimibles(comentario, conservar_simbolos=conservar_simbolos)
        
        
        lista_palabras = comentario.split()
        # remove words with less than 4 characters
        lista_palabras = [palabra for palabra in lista_palabras if len(palabra) >= 4]
        
        # if not lista_palabras:
        #     continue
        # # remove digits
        # lista_palabras = [palabra for palabra in lista_palabras if not palabra.isdigit()]

        # # remove common words
        lista_palabras = [palabra for palabra in lista_palabras if palabra not in lista_eliminar]
        stopword_batch[i] = " ".join(lista_palabras)

    return stopword_batch






#################################################################################################
#################################################################################################
###                                     FUNCIONES NUEVAS
#################################################################################################
#################################################################################################

def remover_palabras(data: list, comienzos: list) -> list:
    """Función para detectar palabras que comienzan con un comienzo determinado y eliminar la palabra del string."""
    
    # Crear patrón regex para coincidir con palabras que comienzan con los comienzos especificados
    # [ORIGINAL] patron = re.compile(rf'\b({"|".join(map(re.escape, comienzos))})\S*\b', flags=re.IGNORECASE)
    comienzos = [r'\.+'+comienzo[1:]+"\w+" if comienzo.startswith(".") else comienzo for comienzo in comienzos]
    patron = r'|'.join(comienzos)    

    # Inicializar una lista para almacenar los resultados corregidos
    resultados_corregidos = []
    
    # Iterar a través de los elementos en la serie
    for texto in data:#TODO: optimizar
        # Utilizar el patrón regex para reemplazar las palabras que comienzan con los comienzos especificados con una cadena vacía
        # [ORIGINAL] texto_corregido = patron.sub('', texto)
        texto_corregido = re.sub(patron, '', texto)
        texto_corregido = texto_corregido.replace("  ", " ")# reemplazar los dobles espacios por espacios simples
        resultados_corregidos.append(texto_corregido)
    
    # Crear una nueva serie con los resultados corregidos
    return resultados_corregidos


def identificar_relevantes(data: pd.Series, temas: list) -> pd.Series:
    """Función que identifica temas relevantes y devuelve una columna booleana"""
    
    # Crear patrones regex para cada tema
    patrones = [re.compile(rf'\b{tema}\b', flags=re.IGNORECASE) for tema in temas]
    
    # Inicializar una lista para almacenar los resultados
    resultados = {}
    
    # Iterar a través de los elementos en la serie
    for i, texto in enumerate(data):
        encontrado = False
        
        # Iterar a través de los patrones y verificar si alguno coincide
        for patron in patrones:
            if patron.search(texto):
                encontrado = True
                break  # Si se encuentra una coincidencia, salir del bucle
            
        resultados[i] = encontrado # aca iba append
    
    # Crear una nueva serie booleana a partir de los resultados
    serie_booleana = pd.Series(resultados, name='relevante')
    
    return serie_booleana


if __name__ == "__main__":
    # Crear data de prueba
    data_prueba = [
        "Este es un tweet sobre www.derechos.humanos",
        "La economía mundial está experimentando cambios importantes",
        "La educación es clave para el futuro de la sociedad",
        "El sistema de justicia debe ser transparente y eficiente",
        "El medio ambiente necesita ser protegido",
        "Hablemos de política y probidad en el gobierno",
        " http://www.ejemplo.com Visita nuestro sitio web en",
        "Seguridad y transporte son temas cruciales",
        "Este es un texto sin temas relevantes"
    ]

    temas_interes = ["Derechos humanos", "economia", "educación", "justicia", "medio ambiente", "politica", "probidad", "transparencia", "Seguridad", "transporte"]
    eliminar_palabras_que_comiencen_con = ["http", "www"]

    # Ejecutar las funciones
    serie_sin_palabras = remover_palabras(data_prueba, eliminar_palabras_que_comiencen_con)
    serie_relevantes = identificar_relevantes(data_prueba, temas_interes)

    # Mostrar los resultados
    print("Serie con palabras eliminadas:")
    print(serie_sin_palabras)

    print("\nSerie de temas relevantes:")
    print(serie_relevantes)

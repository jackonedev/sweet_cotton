
## Librerias Nativas de Python y de Terceros
import tiktoken
from tqdm import tqdm
import pandas as pd
from datasets import Dataset
import re
from nltk.tokenize import word_tokenize
import sys, os, time, pickle

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
app_root = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
sys.path.insert(0, project_root)

try:
    from app.main.main import tokenizador as Resources
    from app.tokenizadores.main import main as Main
except:
    from main.main import tokenizador as Resources
    from main import main as Main

from tools.tokenizer import preprocesamiento, procesamiento, extraccion_emoji, creacion_emoji_feature
from tools.extraccion_muestras import nombres_propios

#######################################################################







def tokenizador(batch: list, verbose=False) -> pd.DataFrame:
    def data_stream(samples: Dataset, target:str = 'content'):
        for i in range(samples.num_rows):
            yield samples[target][i]

    # CONTENT
    # texto = "lloviznando lloviznandoo lloviznandooo lloviznandoooo lloviznandooooo"
    # batch = [texto, "Honnla Maria!", "bastaannaannaaa pedro", "massa vuellvo paiis argentina hijos 🙏 🙏", "🙏🙏🙏"]
    

    # PREPROCESSING
    batch = preprocesamiento(batch)

    # EXTRACCION DE MUESTRAS 1
    # NER:extracción de nombres propios
    i_nombres_propios = nombres_propios(batch)

    # 2
    try:
        if isinstance(batch, list):
            data = pd.DataFrame(batch)
            data.columns = ['content']
    except AttributeError:
        assert isinstance(data, pd.DataFrame), "data must be a pandas DataFrame"

    except ValueError:
        print ("Length mismatch: Expected axis has 5 elements, new values have 1 elements")



    # EXTRACCION DE MUESTRAS 2
    ## EMOJIS  ##
    feature_emoji = creacion_emoji_feature(batch)
    batch = extraccion_emoji(batch)

    # PROCESAMIENTO PREVIO A LA TOKENIZACION
    batch = procesamiento(batch)

    ##  CREACION DEL DATAFRAME DE TRABAJO  ##
    df = pd.DataFrame({'content': batch, "emojis": feature_emoji , 'i_nombre_propios': i_nombres_propios})


    # # checkpoint para inspeccionar el dataframe
    # with open("dftk_oct_unt.pickle", "wb") as f:
    #     pickle.dump(df, f)
    if verbose:
        print("checkpoint 1: DataFrame previo a la tokenizacion")


    ##  TIKTOKEN  ##
    encoding_base = tiktoken.get_encoding("cl100k_base")



    batch_tokenizado = [encoding_base.encode(content) for content in batch]
    batch_decodificado_bytes = [[encoding_base.decode_single_token_bytes(token) for token in content] for content in batch_tokenizado]

    # print(texto_decodificado_bytes)
    """
    Notas tokenizador transcripcion.ipynb: 
        - en el bucle de tratamiento es que se realiza la decodificacion_str
        - eso era porque algunos caracteres no se podian decodificar
        - como en este tokenizador ya hemos extraido los emojis, no deberia haber problema
    """
    batch_decodificado_str = []
    for content in batch_decodificado_bytes:
        
        
        # content = [token.decode('UTF-8') for token in content]
        for i, token in enumerate(content):
            try:
                content[i] = token.decode('UTF-8')
            except:
                content[i] = " "
                # quedan caracteres que no se pueden decodificar
                pass
                
        
        
        batch_decodificado_str.append(content)

    # Corrección token cero
    for i, content in enumerate(batch_decodificado_str):
        if content == []:
            continue
        content[0] = " " + content[0]
        batch_decodificado_str[i] = content

    # texto_decodificado_str = [token.decode('UTF-8') for token in texto_decodificado_bytes]

    # print(batch_decodificado_str)




    #### TRATAMIENTO TOKENIZADOR  ####
    TOKENS = {} # {0: [tc, ti], 1: [tc, ti], 2: [tc, ti], 3: [tc, ti], ... key_m: [tc, ti]} / key: index, m: cantidad de comentarios -1 (muestra) # porque arranca contando de cero

    for key, content in tqdm(enumerate(batch_decodificado_str), "Tokenizando"):

        tokens_c = [] # hace referencia a tokens_compuestos
        tokens_i = [] # hace referencia a tokens_independientes

        TOKENS[key] = []

        last_token = ""
        cache = []

        for ix, token in enumerate(content):
            
            if ix == 0:
                last_token = token
                continue

            ##  MODULO DE PALABRAS TOKENS COMPUESTOS  ##
            if not token.startswith(" ") and last_token.startswith(" "):
                cache.append(last_token)#primer token compuesto
            elif not token.startswith(" ") and not last_token.startswith(" "):
                cache.append(last_token)# caso entre medio
            elif token.startswith(" ") and not last_token.startswith(" "):# and i != 1: # Como corregimos el token 0, es innecesario. esto es para que no se rompa? o porque tiene una función lógica?
                cache.append(last_token)# caso ultimo token
                tokens_c.append("".join(cache).strip())
                cache = []
                last_token = token
                continue

            ##  MODULO DE PALABRAS TOKEN INDEPENDIENTE  ##
            if token.startswith(" ") and last_token.startswith(" "):
                if len(last_token.strip()) < 3:
                    last_token = token
                    continue
                tokens_i.append(last_token.strip())

            last_token = token

        ## MODULO ULTIMO TOKEN ## #TODO: analizar si last_token debe actualizar a cero junto con la caché
        if len(cache) > 0:
            cache.append(last_token)#TODO# VERIFICAR
            tokens_c.append("".join(cache).strip())
        # si es un token compuesto lo guardamos, sinó se pierde    
        # elif len(last_token.strip()) > 0:# la caché es cero y no last_token: el ultimo token es un token compuesto y no se limpia el last_token, por lo tanto el ultimo token del token compuesto se guardaría
        #     tokens_i.append(last_token.strip())

        TOKENS[key] = [tokens_c, tokens_i]



    if verbose:
        print("checkpoint 2: tokenizacion finalizada")
    # with open("tk_oct_unt.pickle", "wb") as f:
    #     pickle.dump(TOKENS, f)

    token_feature = pd.DataFrame(TOKENS).T
    token_feature.columns = ["tokens_i", "tokens_ii"]

    df = pd.concat([df, token_feature], axis=1)


    if verbose:
        print("programa finalizado de forma exitosa")

    return df


"""
TOKENIZADOR POR TIKTOKEN

AHORRO DE TIEMPO DE PROCESAMIENTO:
    - eliminar tildes
    - pasar todo a minusculas no afecta a los nombre propios pero si a la palabra "Conclusion". Con clus ion vs conclus ion
    - eliminar las palabras escritas todas en mayúsculas

CASO EMOJIS



ETAPAS PREPROCESAMIENTO:
    -1- Eliminacion de caracteres no imprimibles
    -2- Tratemiento para los guiones medios "-"
    -3- Tratamiento de múltiples espacios en blanco
    -4- Extracción de muestras de nombres propios
    -5- Eliminación de tildes y pasar todo a minúsculas
    -6- Extraccion de Emojis
    

ETAPAS TOKENIZADOR:
    -6- Tokenizar
    -7- aplicar filtro miss-spelling
    
    
    
-es verdad que hace falta dos tokenizadores-    
    
""";

def main_df(df:pd.DataFrame, verbose=False) -> pd.DataFrame:
    # el tokenizador se encarga de obtener previa de hastags, links y usuarios mencionados
    assert "content" in df.columns, "df debe tener una columna content"
    
    preparation = Resources()["main_preparation"]    
        
    df = preparation(df, quitar=True, token_config=True) # extraccion de features I
    batch = df["content"].tolist()
    dftk = tokenizador(batch, verbose=verbose)# extraccion de features II y limpieza de content
    
    df["content"] = dftk["content"]
    dftk = dftk.drop("content", axis=1)
    features = ["content", "usuarios_mencionados", "hashtags", "links"]# (1)
    
    return pd.concat([df[features], dftk], axis=1)


def main_df_V2(df:pd.DataFrame, verbose=False) -> pd.DataFrame:
    # el tokenizador se encarga de obtener previa de hastags, links y usuarios mencionados
    assert "content" in df.columns, "df debe tener una columna content"
    
    preparation = Resources()["main_preparation"]    
        
    df = preparation(df, quitar=True, token_config=True) # extraccion de features I
    batch = df["content"].tolist()
    dftk = tokenizador(batch, verbose=verbose)# extraccion de features II y limpieza de content
    
    df["content_cleaned"] = dftk["content"]
    dftk = dftk.drop("content", axis=1)
    features = ["content", "content_cleaned", "usuarios_mencionados", "hashtags", "links"]
    
    return pd.concat([df[features], dftk], axis=1)


def main(file_name:str=None, verbose = False)-> pd.DataFrame:
    ##TODO: Esta función tiene implementada la main_preparation dentro del Main()
    # esta función podría seres un wrapper de main_df
    #"No está pensada para hacer agregación por (1), devuelve un modelo personalizado del CSV"
    if verbose:
        print("Ejecutando tokenizadores/tokenizador_i.py\n")
    
    df = Main(file_name=file_name, verbose=verbose)# el main aplica data_feed
    nombre = df.name
    if verbose:
        print("Saliendo de tokenizadores/main.py\n")
    
    assert "content" in df.columns, "df debe tener una columna content"
    
    batch = df["content"].tolist()
    
    ##TODO: extracción de usuarios mencionados y hashtags y links
    
    dftk = tokenizador(batch, verbose=verbose)# acá preprocsamiento y procesamiento
    
    df["content"] = dftk["content"]
    dftk = dftk.drop("content", axis=1)
    
    
    features = ["content", "usuarios_mencionados", "hashtags", "links"]# (1)
    
    return pd.concat([df[features], dftk], axis=1)
    
import unicodedata, re
from typing import List
import emoji

def eliminacion_caracteres_innecesarios(content: str) -> str:
    """Etapas preprocesamiento:
    - Eliminación de caracteres no imprimibles
    - Reemplazo de caracteres por espacios en blanco
    - Reestructuración de texto para eliminar multiples espacios en blanco
    """
    cleaned_content = ''.join(
        ' ' if c in "&'()*+‘<=>[]^·•`{|}~ýª!?¿¡.,/⁉️‼…:\"-“”;«»" else c
        for c in content
    )
    return re.sub("\s+", " ", cleaned_content)



def eliminacion_tildes(content: str) -> str:
    return ''.join(
        unicodedata.normalize('NFD', c)[0]
        if c in 'áéíóúÁÉÍÓÚàèìòùÀÈÌÒÙâêîôûÂÊÎÔÛãẽĩõũÃẼĨÕŨäëïöÄËÏÖçÇ'
        else c
        for c in content
    )

def preprocesamiento(batch: List[str]) -> list:
    assert isinstance(batch, list), "El argumento batch debe ser una lista"
    assert isinstance(batch[0], str), "El argumento batch debe ser una lista de strings"

    return [eliminacion_caracteres_innecesarios(content) for content in batch]

def procesamiento(batch: list) -> list:
    assert isinstance(batch, list), "El argumento batch debe ser una lista"
    assert isinstance(batch[0], str), "El argumento batch debe ser una lista de strings"

    
    batch = [eliminacion_tildes(content) for content in batch]
    batch = [content.lower().strip() for content in batch]
    
    return batch

            
def extraccion_emoji(batch: list) -> list:
    assert isinstance(batch, list), "El argumento batch debe ser una lista"
    assert isinstance(batch[0], str), "El argumento batch debe ser una lista de strings"
    
    return [emoji.replace_emoji(content, "") for content in batch]

def identificar_emoji_list(batch:list) -> list:
    assert isinstance(batch, list), "El argumento batch debe ser una lista"
    assert isinstance(batch[0], str), "El argumento batch debe ser una lista de strings"
    
    return [emoji.emoji_list(content) for content in batch]

def creacion_emoji_feature(batch:list) -> list:
    assert isinstance(batch, list), "El argumento batch debe ser una lista"
    assert isinstance(batch[0], str), "El argumento batch debe ser una lista de strings"
    
    emoji_list = identificar_emoji_list(batch)
    result = []
    for content in emoji_list:
        if len(content) == 0:
            result.append([])
        else:
            result.append([match["emoji"] for match in content])
    
    return result
    



if __name__ == "__main__":
    texto = "José Jose joseeee     Patricia! -Bullrich PATRICIA-BULLRICH (patricia) bullrich\
        !!!!!! Este es otro ejemplo de tokenizadorrrrr tokenizador basado!! en palabras.\
            Conclusión. Conclusion. conclusion conclusión"
            
    print("tratemiento_i")
    print(eliminacion_caracteres_innecesarios(texto))
    # print("correccion palabras")
    # print(correccion_de_palabras(texto))
    print("preprocesamiento")
    batch = preprocesamiento([texto])
    print(batch)
    
    print("procesamiento")
    print(procesamiento(batch))
    
    
    
    ##########################
    batch = [texto, "Hola Mundo!", "bastaaaaaaa", "massa vuelvo pais hijos 🙏 🙏", "🙏🙏🙏"]
    
    result = identificar_emoji_list(batch)
    print(result)
    feature = creacion_emoji_feature(batch)
    print(feature)
    clean_content = extraccion_emoji(batch)
    print(clean_content)
    ##########################
    batch = [texto, "Hola Mundo!", "bastaaaaaaa", "massa vuelvo pais hijos 🙏 🙏", "🙏🙏🙏"]
    
    batch = procesamiento(preprocesamiento(batch))
    
    content = extraccion_emoji(batch)
    feature_emoji = creacion_emoji_feature(batch)
    print(content)
    print(feature_emoji)
    
    
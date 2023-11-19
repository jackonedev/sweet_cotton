import emoji


def nombres_propios(batch: list) -> list:
    "Devuelve un listado de todas las palabras que comienzan con mayúsculas"
    result = []
    
    for parrafo in batch:
        muestras = [palabra for palabra in parrafo.split(" ") if (palabra.istitle() and len(palabra.strip()) > 3)]#nombres de 4 letras
        result.append(muestras)
    return result




## tiene que ser simple, pero tiene que rápido

def extraer_emoji(batch: list) -> tuple:
    
    """Recibe una lista de comentarios y devuelve una tupla:
    batch, batch_emoji: 
    batch: lista de comentarios sin emojis
    batch_emoji: lista de emojis encontrados en los comentarios
    """
    ##TODO: La estructura que devuelve no condice con la estructura de entrada
    emoji_batch = []
    for comment in batch:
        # emoji_batch.append(emoji.get_emoji_regexp().findall(comment))
        for word in comment.split(" "):
            if emoji.is_emoji(word):
                emoji_batch.append(word)
    ##TODO: La estructura que devuelve no condice con la estructura de entrada

    batch = [emoji.replace_emoji(string, replace='') for string in batch]

    return batch, emoji_batch



if __name__ == "__main__":
    texto = 'José Jose joseeee Patricia Bullrich PATRICIA BULLRICH patricia bullrich Este es otro ejemplo de tokenizadorrrrr tokenizador basado en palabras Conclusión Conclusion conclusion conclusión'
    batch = [texto, "massa vuelvo pais hijos 🙏 🙏", "🙏🙏🙏"]
            
    # print("nombres propios")
    # print(nombres_propios(batch))
    # OUTPUT: [['José', 'Jose', 'Patricia', 'Bullrich', 'Este', 'Conclusión', 'Conclusion'], [], []]
    # OK
    
    
    # # extraer_emoji(batch)
    
    # identificar_emojis(texto)
    print(emoji.is_emoji("🙏🙏🙏".split("")))
    
    batch, emoji_batch = extraer_emoji(batch)
    print(batch)
    print(emoji_batch)
    
    print("programa finalizado de forma exitosa")
    
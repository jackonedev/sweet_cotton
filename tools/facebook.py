def clean_facebook_comments(batch: list) -> list:
    new_batch = []
    for comment in batch:
        
        
        # Eliminar registros vacios
        if list(zip(comment)) in ["", " "]:
            continue
        # Eliminar registros trolls
        if not len(list(zip(comment))) > 3: # cualquier comentario que esté escrito utilizando solo 3 caracteres
            continue
        
        # Filtro 1: registros estandar
        if comment in ["Me gusta", "Responder", "ver mas","Ver más", "Editado", "Fan destacado", "·", "empty"] or comment.isnumeric():
            continue
        
        # Filtro 2: Hora de publicacion
        # ## quitar los comentarios numéricos. Ej: 13 17, 14 00
        comment_ = comment.split(":")
        ok = False
        for elemento in comment_:
            if not elemento.isnumeric():
                ok = True
                break
        if not ok:
            continue
        
        # Filtro 3: remover los usuarios. Ej: user15905495087
        if len(comment.split("user")) != 1:
            continue
        
                
        comment = comment.split(" ")
        
        # Filtro 4: registros que tienen patrón "# h" excluídos
        if len(comment)==2 and comment[1] in ['h', "min", "d", "sem", "respuesta", "respuestas"]:
            continue

        if len(comment)==3 and comment[1].isnumeric():
            continue

        # Filtro 5: eliminar autores
        # filter_3 = [False if word.istitle() else True for word in comment]
        filter_3 = [not word.istitle() for word in comment]
        
        if any(filter_3):
            new_batch.append(" ".join(comment))

    return new_batch


if __name__ == "__main__":
    """Pendiente de resolver en fb-matamorostema1-rocio.csv:
     'Felipa de Anda'
      'Karina Hernandez  ·',
       'Jany de la Rosa',
       'Arem Esquivel AE'
        'ManoLo Medina',
        'Yahaira HdZz',
        
        
    Pendiente de resolver en fb-matamorostema2-rocio.csv:
        'Sandy AV',
        'Lydia Adame de Garcia',
        
        """
def clean_instagram_comments(batch: list) -> list:
    new_batch = []
    for comment in batch:
        
        # Filtro 1
        if comment in ["Me gusta", "Responder", "Editado", "Fan destacado", "Ver traducción", "Ocultar todas las respuestas"] or comment.isnumeric():
            continue
        
        
        comment = comment.split(" ")

        if len(comment) == 1:
            continue
        
        # Filtro 2: registros que tienen patrón "# h" excluídos
        if len(comment)==2 and comment[1] in ['h', "d", "sem", "respuesta", "respuestas"]:
            continue
        
            
        # filtros  "hresponder", "dresponder"
        if len(comment) == 2 and comment[0].isnumeric():
            continue


        elif len(comment) == 3 and comment[1] in ["respuestas"]:
            continue

        elif len(comment) == 3 and comment[0].isnumeric() and " ".join(comment[1:]) in ["Me gusta"]:
            # caso: "41 Me gusta"
            continue
            
       
        elif len(comment) == 4 and comment[3] in ["gustaResponder"]:
            continue
        
        elif len(comment) == 4 and comment[2].isnumeric() and comment[-1] in ["respuestas"]:
            # caso: "Ver las 4 respuestas"
            continue
        
        
        # Filtro 3: eliminar autores
        # filter_3 = [False if word.istitle() else True for word in comment]
        filter_3 = [not word.istitle() for word in comment]
        


        if any(filter_3):
            new_batch.append(" ".join(comment))

    return new_batch
## Librerias Nativas de Python y de Terceros
from copy import copy
import sys
import os
import ast
from pathlib import Path
from wordcloud import WordCloud
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
from typing import List


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
path_config = os.path.join(project_root, "word_cloud_config")
sys.path.insert(0, project_root)


## Aplicaciones propias
from app.main.main import wordcloud
try:
    from app.word_cloud.main import limpieza_txt
    from app.word_cloud.schemas.config_mascara import WordCloudConfig
except:
    from main import limpieza_txt
    from schemas.config_mascara import WordCloudConfig


def load_resources():
    global remover_palabra, filtrado_palabras
    global content_wc, token_wc
    global content_wc_II, token_wc_II
    global content_wc_III, token_wc_III

    resources = wordcloud()
    remover_palabra = resources["wordcloud_remover_palabra"]
    filtrado_palabras = resources["wordcloud_filtrado_palabras"]
    
    content_wc = [
        "aclaro vote bullrich decime milei fascista",
        "vote bullrich pedo voto corrupto verbal milei",
        "bullrich señalada alutara asoc legt usuarios armas fuego desarmista peligro l militaron campaña milei piparo cambiemos gestion pesima anmac seguiran apoyando lla",
        "valores ucr",
        "patricia bullrich apoyara javier milei balotaje diferencia socios juntos cambio",
        "mano macri miley bullrich aseguro vos salvas cuidado libertad proponen libertad llenarse guita seria 2da fuga macri olvides pagando entraria represion",
        "bullrich respaldara milei balotaje definira encuentro anoche candidato libertario macri apoyo pro lña libertad avanza significara ruptura juntos cambio",
        "distinto ganar demostro mugre mendigando votantes bullrich aliandose macri destruyo pais dejo deuda enorme seguimos sufriendo fecha tomatela peluca",
        "patricia bullrich apoyara javier milei balotaje diferencia socios juntos cambio",
        "esperando conferencia patricia bullrich apoyara javier milei candidata presidencia viene reunirse integrantes juntos cambio dira minutos juegan viene juntos libertad",
        "radicales antipodas milei bullrich macri justamente luchar ideas politicas nacimos partido causa regimen derechas peligrosamente desinhibidas",
        "casamiento arreglado x macri milei bullrich sincero q tuvimos oposicion sentido radicalismo peronismo aberracion gualeguachu salga salga cartas mesa",
        "baby etchecopar enojado bullrich milei milei coptado cambiemos",
        "señor pida disculpas publicas señora patricia bullrich veremos dueño voto",
        "patricia bullrich luis petri punto anunciar apoyo javier milei estallar pacto juntos cambio radicales resisten sector elisa carrio sostienen apoyaran milei prescindencia libertad",
        "patricia bullrich luis petri punto anunciar apoyo javier milei estallar pacto juntos cambio radicales resisten sector elisa carrio sostienen apoyaran milei prescindencia libertad",
        "deberia salir publicamente pedir disculpas dichos señora bullrich dando razones comprensibles armar henkidama",
        "javier milei necesita apoyo bullrich cornejo gente calienta opinion politicos radicalismo pro apoyan perjudicados seran radicalismo pro ceder exigencias apoyar balotaje",
        "patricia bullrich desmarca cargos juntos cambio apoyara javier milei balotaje"
    ]
    token_wc = [
        ['gano', 'bullrich', 'ignorante', 'rebaja', 'argentino', 'rebaja', 'elecciones', 'democraticas', 'vergüenza'],
        ['patricia', 'bullrich', 'luis', 'petri', 'hablando', 'representacion', 'apoyan', 'milei', 'patria', 'peligro', 'licito', 'excepto', 'defenderla'],
        ['impresionante', 'discurso', 'patriotico', 'patricia', 'bullrich', 'valiosa', 'presencia', 'luis', 'petri', 'representante', 'radicalismo', 'mendocino', 'neutralidad', 'sirve', 'riesgo', 'libertad', 'muerte'],
        ['habla', 'patricia', 'bullrich', 'patria', 'peligro', 'critica', 'cfk', 'milei', 'diferencias', 'obligacion', 'neutrales', 'ayer', 'reunio', 'libertario', 'perdonamos', 'mutuamente'],
        ['diluvio', 'lloriqueo', 'rojetes', 'argentinos'],
        ['impresionante', 'discurso', 'patriotico', 'patricia', 'bullrich', 'valiosa', 'presencia', 'luis', 'petri', 'representante', 'radicalismo', 'mendocino', 'neutralidad', 'sirve', 'riesgo', 'libertad', 'muerte'],
        ['patricia', 'gato', 'macri', 'acaban', 'estrellar', 'juntos', 'faltaba'],
        ['bullrich', 'adelante', 'elecciones', 'demuestran', 'irresponsabilidad', 'populismo', 'ganar', 'eleccion', 'politico', 'sucido', 'compartimos'],
        ['bullrich', 'termino', 'firmar', 'ruptura', 'jxc', 'declaracion', 'penosa', 'espero', 'radicalismo', 'deje', 'tirada', 'separe', 'vergüenza', 'postura'],
        ['bullrich', 'acaba', 'concepto', 'liberalismo', 'encuentro'],
        ['bullrrich', 'patria', 'peligro', 'milei', 'estaremos', 'peligro', 'decepcionaste', 'despues', 'denigrante', 'milei'],
        ['confio', 'patricia', 'bullrich', 'radicalismo', 'carrio', 'ricardito', 'alfonsin', 'abajo', 'trabajaron', 'kichnerismo', 'sigo', 'republica', 'corrupcion'],
        ['jajajajaja', 'saluden', 'milei', 'brazo', 'bullrich'],
        ['habra', 'ofrecido', 'miley', 'bullrich', 'diga', 'apoya', 'regalo', 'armado', 'seguramente', 'lla', 'pierde', 'diputados', 'tambien', 'pierde', 'coherencia', 'politica', 'tranza', 'casta'],
        ['bullrich', 'argentina', 'cfk', 'argentinos', 'unimos', 'terminar', 'preso'],
        ['campaña', 'milei', 'patricia', 'bullrich', 'correcto', '19', '11', 'juntos', 'sacar', 'peor', 'tuvo'],
        ['millon', 'socialismo', 'radicalismo', 'santafesino', 'fingir', 'demencia', 'elecciones', 'nacionales', 'unirse', 'bullrich', 'apoyaran', 'milei', 'basado', 'quita', 'autoritarismo', 'privatizacion', 'habitan'],
        ['millon', 'socialismo', 'radicalismo', 'santafesino', 'fingir', 'demencia', 'elecciones', 'nacionales', 'unirse', 'bullrich', 'apoyaran', 'milei', 'basado', 'quita', 'autoritarismo', 'privatizacion', 'habitan'],
        ['bullrich', 'resolvieron', 'apoyar', 'milei', 'elecciones', 'presidenciales', 'patria', 'peligro', 'permitido', 'defenderla', 'libertad', 'kichnerismo']
    ]

    content_wc_II = [
        "obvio bullrich iba milei derecha problema dejar diferencias unirse izquierda esperemos votantes pro tengan criterio",
        "info bullrich petri apoyarian milei",
        "politicos venezolanos aprender pais prioridad dejar ego soberbia estupidez politica navegar aguas",
        "bullirch anunciar apoya millei rompe juntos cambio peronismo ratoooo",
        "pensar investigo millones votos votaron massa patricia bullrich milei salieron corruptos necios kirchneristas habidos delito trampa investiguen favor fraude argenzuela k lpm",
        "bullrich gana kirchnerismo juntos cambio camino disolucion conocemos practicas extorsiones ingobernabilidad posicion reves permitiendo jxc quede presa",
        "petri amenazada cuchillo pedir votar massa darle apoyo explicito milei",
        "imaginan bullrich petri salgan pedir voto massa sueño",
        "macri animal politica liquido rivales internos saca radicalismo apoyo milei entierra bullrich haciendole comer sapo publico pacto cargos amigos gabinete milei casta debo",
        "macri obligar bullrich aceptar miedo carpeta filmacion mmmmm",
        "radicalismo afuera coalicion civica afuera larreta afuera afuera tibios cagones corruptos",
        "confirma mauricio macri patricia bullrich reunieron javier milei",
        "pelado acaba confirmar anoche juntaron personalmente milei macri bullrich viene frente",
        "patricia bullrich apoyara milei balotaje diferencia socios juntos cambio via",
        "lei salir pato apoya milei vuelta libertarios digo fiscalicen lacra pais massa capaz vender hijo fiscalicen",
        "mediodia termina partido politico bullrich anunciara oficialmente apoyo hara larreta fuego amigo desesperado macrista locura muchachos",
        "patricia bullrich anuncia mauricio macri apoyaran javier milei balotaje massa decision deja borde fractura juntos cambio decision tomaron reunion ex presidente ex ministra seguridad milei",
        "bullrich confirma apoyo pro javier milei balotaje ucr coalicion civica pedian neutralidad acusan macri romper juntos cambio",
        "macri bullrich reunieron javier milei mira video deja comentario"
    ]
    token_wc_II = [
        ['pato', 'bullrich', 'conto', 'radicalismo', 'apoyara', 'milei'],
        ['brutos', 'pendejos', 'pobres', 'votaron', 'milei', 'trabajadores', 'informales', 'pobres', 'albañil', 'plomero', 'jardinero', 'bullrich', 'famosos', 'pobres', 'derecha'],
        ['gano', 'milei', 'milei', 'ganaba', 'bullrich', 'iba', 'bullrich', 'kirchnerismo'],
        ['bullirch', 'anunciar', 'apoya', 'millei', 'rompe', 'juntos', 'peronismo', 'ratoooo'],
        ['20', 'preguntarle', 'pedir', 'perdon', 'bullrich', 'mierda', 'hicieron', '30', 'operaciones', 'dispuesto', 'borron', 'ustedes', 'siguen', 'insistiendo'],
        ['radicales', 'antipodas', 'milei', 'bullrich', 'macri', 'justamente', 'luchar', 'politicas', 'nacimos', 'derechas', 'peligrosamente', 'desinhibidas'],
        ['deberia', 'macri', 'bullrich', 'milei', 'traidores', 'radicalismo', 'perdio', 'bullrich', 'brazos'],
        ['estamos', 'quiebre', 'ruptura', 'definitiva', 'juntos', 'demostrarse', 'traidores', 'bullrich', 'milei'],
        ['anuncio', '12', 'bullrich', 'luis', 'petri', 'anoche', 'reunieron', 'macri', 'milei', 'apoyo', 'explicito', 'libertario', 'esquema', 'gobernabilidad', 'conjunta'],
        ['macri', 'reunio', 'milei', 'ahi', 'reunir', 'bullrich', 'suspende', 'jxc', 'bullrich', 'conferencia', 'prensa', 'petri'],
        ['bullrich', 'confirma', 'apoyo', 'javier', 'milei', 'balotaje', 'ucr', 'coalicion', 'civica', 'pedian', 'neutralidad', 'acusan', 'macri', 'romper', 'juntos'],
        ['necesitamos', 'pregunten', 'apoyo', 'bullrich', 'petri', 'miley', 'responda', 'votos'],
        ['larreta', 'carrio', 'radicales', 'complicaron', 'gobernabilidad', 'macri', 'iban', 'traicionar', 'bullrich', 'perdonarlos', 'echarlos'],
        ['milei', 'ofrecio', 'atras', 'bullrich', 'ministerio'],
        ['patricia', 'bullrich', 'conferencia', 'prensa', 'mediodia', 'anticipan', 'anunciara', 'apoyara', 'javier', 'milei', 'balotaje'],
        ['bullrich', 'pego', 'paliza', 'larreta', 'cambiemos', 'purifico', 'sacaron', 'traidores'],
        ['trataban', 'casta', 'bullrich', 'milei', 'metiendo', 'casta', 'odiaba', 'quedamos'],
        ['juntos', 'razon', 'rompio', '2019', '2020', 'carrio', 'morales', 'larreta', 'lusto', 'sellaron', 'excluia', 'excluian', 'recien', 'iba', '41%', 'andas'],
        ['bullrich', 'anuncio', 'apoyara', 'javier', 'ballotage']
    ]

    content_wc_III =[
        "hora sucedio merecen escarmiento jamas volveran acercar puedes ayudarme hora",
        "esperamos ofrecemos servicios gratuitos orientacion tramites municipales martes noviembre presidencia mpal am trabaja cumple avanza ciudadania",
        "gobierno san pedro cholula ponen disposicion centros acopio apoyar sumate favor familias afectadas huracan horario hrs",
        "obra intermunicipal toca gobernador puebla llama gobernador",
        "ciudadanos recordamos horarios recoleccion basura hrs lunes",
        "detienen octubre presuntos delincuentes infractores informa resultados mensuales estrategias combate delincuencia",
        "tardes mensaje directo envianos nombre direccion numero contrato motivo solicitud",
        "detenidos mes octubre resultados derivado diversas estrategias procurar entorno paz informacion",
        "tenia cholula sirven infracciones fotomultas",
        "revisamos damos continuidad temas trabajando brindar atencion calidad familias cholultecas alianza compromiso trabaja cumple avanza mejores servicios",
        "detenidos resultados ssc cholula octubre",
        "inaugura calle oriente barrio jesus tlatempa",
        "esperamos jornada integral atencion ciudadana ofrecemos servicios gratuitos orientacion tramites municipales martes noviembre presidencia mpal am alianza ciudadania",
        "positiva reactivacion economica municipio san pedro cholula acciones impulso alcaldesa atiende alta demanda materia educativa temas ocupan respuesta mano",
        "cholula ⃣ municipios puebla acreditado elementos certificado unico policial trabajamos cumplimos avanzamos tranquilidad familias",
        "recuerda areas gobierno cholula brindando servicio publico sabados am pm esperamos gusto seguir trabajo conjunto beneficia familias",
        "sorteo perteneces clase remisos acude presentando cartilla noviembre mañana complejo cultural cholula av pte",
        "cuida ambiente evita montoneros organismo operador servicio limpia san pedro cholula informa horas recoleccion basura",
        "lamentamos molestias permitenos apoyarte levantamiento reporte envianos mensaje directo siguientes datos favor numero contrato nombre titular direccion telefono contacto"
    ]
    token_wc_III = [
        ['animo', 'nooo'],
        ['cholula', '1', '22', 'municipios', 'puebla', 'acreditado', 'certificado', 'unico', 'policial', 'trabajamos', 'cumplimos', 'avanzamos', 'tranquilidad', 'familias'],
        ['pues', 'municipio', 'camionetas', 'nadie', 'manifestacion', 'injusto', 'extorsionando', 'municipio'],
        ['cholula', 'traves', 'bienestar', 'cosme', 'texintla', 'invita', 'elaboracion', 'figuras', 'navideñas', 'podras', 'desarrollar', 'habilidades', 'emprender', 'informacion', '221', '596', '0249'],
        ['visitamos', '3ra', 'allende', 'entepontla', 'invertimos', '2', '3', 'mdp', 'adoquinarla', 'instalar', '9', 'luminarias', 'banquetas', 'guarniciones', 'beneficiar', 'primaria', 'vecina', 'trabajamos', 'cumplimos', 'avanzamos'],
        ['traves', 'secretaria', 'infraestructura', 'dimos', 'mantenimiento', 'poda', 'deshierbe', 'barrido', 'calles', 'cuachayotla', 'circuito', 'ciclismo', 'trabaja', 'cumple', 'avanza', 'impulsando', 'deporte'],
        ['sera', 'difundan', 'conductores', 'anden', 'cuidado', 'recta'],
        ['cuidemos', 'presentacion', 'patrimonios', 'mantengamos'],
        ['vives', 'pedro', 'cholula', 'vaya', 'horarios', 'colonia', 'escucha', 'camion', 'saca', 'basura', 'barre', 'banqueta', 'evita', 'atascar', 'alcantarillas', 'operador', 'limpia', 'pedro', 'cholula'],
        ['sorteo', '2023', 'perteneces', '2005', 'remisos', 'acude', 'presentando', 'cartilla', '12', 'noviembre', '9', '00', 'complejo', 'cholula', '4', 'pte'],
        ['cholula', '1', '22', 'municipios', 'puebla', 'acreditado', 'certificado', 'unico', 'policial', 'trabajamos', 'cumplimos', 'avanzamos', 'tranquilidad', 'familias'],
        ['caera', 'preciado', 'liquido', '2'],
        ['igual', 'ayer', 'cobrar', 'estan', 'buenos'],
        ['buenas', 'tardes', 'directo', 'envianos'],
        ['organismo', 'operador', 'limpia', 'pedro', 'cholula', 'invita', 'cholultecos', 'sumarse'],
        ['sabado', '4', 'noviembre', 'barrio', 'maria', 'xixitla', 'lleva', 'chingada'],
        ['pedro', 'cholula', 'ponen', 'disposicion', '2', 'centros', 'acopio', 'apoyar', 'sumate', 'familias', 'afectadas', 'huracan', 'horario', '8', '30', '15', '30'],
        ['organismo', 'operador', 'limpia', 'pedro', 'cholula', 'limpia', 'chula', 'cholula', 'dejamos', 'separar', 'comercializacion'],
        ['ojala', 'puras', 'habladurias', 'señora', 'angon']
    ]

def load_configuration_file(path_config: str, names: list) -> dict:
    global mascara_wordcloud
    #  LOAD CONFIGURATION FROM LOCAL FILE
    # Create wc_params dict from txt file
    with open(os.path.join(path_config,"mascaras_png", "wordcloud_mask_config.txt"), "r", encoding="UTF-8") as file:
        wc_params = file.read()
    # CONFIGURATION STRUCTURE VALIDATION
    try:
        wc_params = ast.literal_eval(wc_params)
        wc_params["mascara"] = Path(os.path.join(path_config, 'mascaras_png', wc_params["mascara"]))

        ## PYDANTIC VALIDATION SCHEMA 
        validation_schema = WordCloudConfig(**wc_params)
        try:# (for V1)
            wc_parmams = validation_schema.dict()
        except:# (and V2)
            wc_parmams = validation_schema.model_dump()
    except Exception as e:
        print("Error en el formato del archivo de configuración.")
        print(e)
        print("Ejecución interrumpida.")
        sys.exit(0)
    # Open .png file with mask shape
    #TODO: reeplace for contex manager
    try:
        print(f"Implementando configuración con Máscara: {wc_params['mascara']}")
        mascara_wordcloud = np.array(Image.open(wc_params["mascara"]))
        wc_params.pop("mascara")
        
    except FileNotFoundError as e:
        print("ERROR DE SISTEMA: Colocar un archivo .png con una mascara en tamaño deseado en la carpeta de configuracion")
        sys.exit(0)
        
    # Personalized configurations
    wc_params_storage = {}
    for name in names:
        default_wc_params = copy(wc_params)
        # Default configuration in function of pd.DataFrame(...).name attribute
        if name.split("-")[-1] in ["positive", "negative"]:
            if name.split("-")[-1] == "positive":
                default_wc_params["color_func"] = (84, 179, 153)
            elif name.split("-")[-1] == "negative":
                default_wc_params["color_func"] = (231, 102, 76)
        
        wc_params_storage.update({name:default_wc_params})
    
    return wc_params_storage

def load_filters(path_config):
    # leer archivos txt de configuracion y correr modulo de filtrado
    file = "eliminar_palabras_que_comiencen_con.txt"
    if os.path.isfile(os.path.join(path_config, file)):
        eliminar_palabras = limpieza_txt(path_config, file)
    else:
        if False:
            print("No se encontró el archivo 'eliminar_palabras_que_comiencen_con.txt' en el directorio de APP_utils")
        eliminar_palabras = []

    file = "eliminar_palabras_wordcloud.txt"
    if os.path.isfile(os.path.join(path_config, file)):
        filtrar_palabras = limpieza_txt(path_config, file)
    else:
        if False:
            print("No se encontró el archivo 'eliminar_palabras_wordcloud.txt' en el directorio de APP_utils")
        filtrar_palabras = []

    return (eliminar_palabras, filtrar_palabras)

def apply_filters(batch: list, filter_1, filter_2) -> list:
        
        batch = remover_palabra(batch, filter_1)
        batch = filtrado_palabras(batch, filter_2)
        
        return batch

def update_wc_colormap(wc_params_storage, nombres):
    global color_tuple, color_func
    """Funcion alternativa "colormap":
    pinta las palabras de distinto color en funcion del tamaño
    para ello debe eliminarse el parámetro por default "color_func"."""
    for name in nombres:
        wc_params = wc_params_storage[name]
        if "colormap" in wc_params.keys() and wc_params["colormap"] != "":
            wc_params.pop("color_func")
        else:
            color_tuple = wc_params["color_func"]
            color_func = lambda *args, **kwargs: color_tuple
            wc_params.pop("color_func")
        
        wc_params_storage[name] |= wc_params

    return wc_params_storage

def wordcloud_content(subbatch, wc_params):
    word_cloud = ""
    for row in subbatch:
        row += " "
        word_cloud+= row

    ## Se cambia el mode de RGBA a RGB y se cambia el background color
    # se añaden las lineas de contorno y color del contorno
    wordcloud = WordCloud(
        mask=mascara_wordcloud,
        collocations=False,
        contour_width=1.0,
        **wc_params)
    
    ## si existe colormap. no existe contour
    if not "colormap" in wc_params.keys():
        wordcloud.color_func=color_func
        wordcloud.contour_color = color_tuple
    else:
        wordcloud.contour_color = (0, 0, 0)
    
    return wordcloud.generate(word_cloud)

def wordcloud_token(subbatch:list, wc_params:dict) -> WordCloud:
    print("Hola Mundo!")
    word_cloud = ""
    word_cloud = [word_cloud + " ".join(twc) for twc in subbatch]
    word_cloud = " ".join(word_cloud).strip()
    print(f"Lo más preciado que tengo es saber que True == 1 == {len(word_cloud)}")
    print(f"""
     index_0:     {type(word_cloud[0])}
     
     index_-1 =   {word_cloud[-1]}
          """)
    wordcloud = WordCloud(
        mask=mascara_wordcloud,
        collocations=False,
        contour_width=1.0,
        **wc_params)
    if not "colormap" in wc_params.keys():
        wordcloud.color_func=color_func
        wordcloud.contour_color = color_tuple
    else:
        wordcloud.contour_color = (0, 0, 0)
    
    return wordcloud.generate(word_cloud)


def final_output(dataframes:List[pd.DataFrame]=None) -> List[WordCloud]:
    from app.main.main import wordcloud
    """
    Esta funcion ejecuta la libreria wordcloud,
    devuelve el objeto tipo WordCloud propio de la libreria wordcloud.
    
    Recibe una lista de DataFrames y devuelve una lista de objetos tipo WordCloud
    
    Respecto al nombre de cada DataFrame:
        - si el archivo de apertura se llama, nombre-arhivo_valores_adicionales.extension
        - 'nombre-archivo' siempre será el comienzo
        - 'nombre-archivo_{filtered:optional}': el elemento split('_')[1] define la activación del filtro
        - 'nombre-archivo_{}_{sentiment:optional}': el elemento split('_')[-1] define si se aplican valores por default al df
    """
    
    load_resources()

    #HARDCODED DATA
    if dataframes is None:
        df_1 = pd.DataFrame({"content_wc":content_wc, "token_wc":token_wc})
        df_2 = pd.DataFrame({"content_wc":content_wc_II, "token_wc":token_wc_II})
        df_3 = pd.DataFrame({"content_wc":content_wc_III, "token_wc":token_wc_III})

        df_1.name = "octubre-untitled"
        df_2.name = "octubre-untitled_filtered"
        df_3.name = "tw-cholula-sofia_positive"

        dataframes = [df_1, df_2, df_3]

    # Presets    
    nombres = [d.name for d in dataframes]
    wc_params_storage = load_configuration_file(path_config, nombres)
    
    # Batch Creation: batch = [[batch_content, batch_token], ...]
    batch = []
    for i in range(len(nombres)):
        content = dataframes[i].content_wc.to_list()
        token = dataframes[i].token_wc.to_list()
        batch.append([content, token])
    
    # Filtrado: on/off depends on the name of dataframes
    filtros = load_filters(path_config)
    for i in range(len(nombres)):
        nombre = nombres[i].split("_")
        if len(nombre) > 1:
            if nombre[1] == "filtered":
                print("activando filtros para: ",nombre[0])#TODO: Borrar
                batch[i][0] = apply_filters(batch[i][0], *filtros)
                batch[i][1] = apply_filters(batch[i][1], *filtros)

    # Wordcloud params update
    wc_params_storage = update_wc_colormap(wc_params_storage, nombres)
    # plt.figure(figsize=(20,8))

    # Wordcloud object instanciation
    #TODO: optimization
    wordcloud_storage = []
    for i, name in enumerate(nombres):
        wc_content = wordcloud_content(batch[i][0], wc_params_storage[name])
        wc_token = wordcloud_token(batch[i][1], wc_params_storage[name])
        wordcloud_storage.append([wc_content, wc_token])

    # Wordcloud config backup
    try:# recomposition of the original configuration
        wc_params_storage[nombres[0]]["color_func"] = color_tuple
    except:
        pass

    output_name = nombres[0].split("_")[0]
    with open(os.path.join(path_config,"mascaras_png", f"{output_name}.txt"), 'w', encoding="UTF-8") as f:
        f.write(str(wc_params_storage[nombres[0]]))
        
    print(f"{__name__} ended succesfully!")
    return wordcloud_storage

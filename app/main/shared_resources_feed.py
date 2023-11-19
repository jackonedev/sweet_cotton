
# funciones para que las apps puedan acceder a los recursos compartidos
# los recursos compartidos se encuentran en el directorio de la app
# : project_root/app/shared_resources
# este modulo se encuentra en el directorio main de las apps
# : project_root/app/main/shared_resources_feed.py
# los ficheros que vamos a leer son pickle serializados

# primero debemos importar todos los modulos
import sys, os, pickle, datetime
import pandas as pd
# obtener las variables de path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
app_root = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
shared_resources = os.path.join(os.path.abspath(os.path.join(app_root, '..')), "shared_resources")

sys.path.insert(0, project_root)


"""
El formato de los nombres es el siguiente:
{objeto}_{nombre}_{mes}_{dia}_{id}.pickle


Ejemplo:
- dfts_melcogatev2_10_20_1.pickle
- dfts_melcogatev2_10_20_2.pickle

Hace referencia a:
- dfts: dataframe de time series
- melcogatev2: nombre de la data
- 10: mes Octubre
- 20: dia 20
- 1: primer procesamiento


""";

# obtener un listado de los nombres de los ficheros
def obtener_listado_ficheros():
    # obtener el listado de los ficheros
    listado_ficheros = os.listdir(shared_resources)
    # obtener el listado de los ficheros pickle
    listado_ficheros = [fichero for fichero in listado_ficheros if fichero.endswith(".pickle")]
    return listado_ficheros


# extraer de los nombres de los ficheros la fecha de creacion
def obtener_informacion_ficheros(file_list:list) -> dict:
    
    file_list = [file.rsplit(".", 1) for file in file_list]
    file_list = [file[:-1][0] for file in file_list]
    file_list = [file.split("_") for file in file_list]
    
    # fecha
    mes_dia = [elemento[-2] for elemento in file_list]
    mes_dia = list(set(mes_dia))
    
    # nombre del fichero
    nombre_fichero = [["_" if elemento == "" else elemento for elemento in lista[:-1]] for lista in file_list]
    nombre_fichero = ["_".join(lista) for lista in nombre_fichero]
    nombre_fichero = list(set(nombre_fichero))
    
    # nombre de las versiones versiones
    versiones_fechas = []
    for lista in file_list:
        for ix, fichero in enumerate(lista):
            if fichero == "":
                fichero = "_"
                lista[ix] = fichero
        versiones_fechas.append('_'.join(lista))
        
    result = {
        "mes_dia": mes_dia,
        "nombre_fichero": nombre_fichero
    }
    
    versiones = {'versiones': {}}
    for fecha in mes_dia:
        versiones['versiones'] |= {fecha: {}}
        for fichero in nombre_fichero:
            label = fichero.split("_")[1]
            if label not in versiones['versiones'][fecha]:
                versiones['versiones'][fecha] |= {label: []}
            for version in versiones_fechas:
                fecha_version = version.split("_")[-2]
                if version.startswith(fichero) and fecha_version == fecha:
                    versiones['versiones'][fecha][label].append(version)
    result |= versiones
    return result
                

# leer el fichero y devolver el contenido
def return_file(file_name:str) -> pd.DataFrame:
    if not file_name.endswith(".pickle"):
        file_name += ".pickle"
        
    if file_name not in obtener_listado_ficheros():
        print("El fichero no existe.")
        print("Ejecución interrumpida de forma segura.")
        exit()
        
    with open(os.path.join(shared_resources, file_name), "rb") as file:
        df = pickle.load(file)
    
    return df

# crear un mensaje informativo para el usuario
def menu(file_name:str = None) -> pd.DataFrame:
    # para que pueda ingresar por medio de un input el archivo que desea
    # luego elije la version que desea (default la ultima version)
    if not file_name:
        files = obtener_informacion_ficheros(obtener_listado_ficheros())
        print("Seleccione el archivo que desea leer:")
        
        fechas = list(files["mes_dia"])
        fechas = sorted(fechas)
        default = fechas[-1]

    
        # sistema, devolverle al usuario un listado de carpetas dentro del output del archivo
        # usuario, tener por default el último archivo que se haya procesado 
        msg = """Elija una fecha: 
\t\t - {}

default: {}   (presione enter para seleccionar el default)
seleccionar fecha: """

        # y solicitar al usuario una respuesta
        user_input = input(msg.format("\n\t\t - ".join(fechas), default))
        # print(msg.format("\n\t\t - ".join(fechas), default))
        if not user_input:
            user_input = default
        if user_input not in fechas:
            print("Input ingresado es erróneo.")
            print("Ejecución interrumpida de forma segura.")
            exit()
        else:
            fecha = user_input
        print(f"Seleccionado: {fecha}\n")
        
        ## Nombre del fichero
        nombres = list(files["versiones"][fecha].keys())
        nombres = [fichero for fichero in nombres if files["versiones"][fecha][fichero]]
        default = nombres[0]
                
        print("Seleccione el nombre del fichero que desea leer:")
        default = nombres[0]
        msg = """Elija un nombre:
\t\t - {}
        
default: {}   (presione enter para seleccionar el default)
seleccionar nombre: """
        
        user_input = input(msg.format("\n\t\t - ".join(nombres), default))
        if not user_input:
            user_input = default
        if user_input not in nombres:
            print("Input ingresado es erróneo.")
            print("Ejecución interrumpida de forma segura.")
            exit()
        else:
            nombre = user_input
        
        print(f"Seleccionado: {nombre}\n")
        
        ## Version del fichero
        versiones = files["versiones"][fecha][nombre]
        versiones = sorted(versiones)
        default = versiones[-1]
        
        print("Seleccione la versión del fichero que desea leer:")
        msg = """Elija una versión:
\t\t - {}

default: {}   (presione enter para seleccionar el default)
seleccionar versión: """
        
        user_input = input(msg.format("\n\t\t - ".join(versiones), default))
        
        if not user_input:
            user_input = default
            
        if user_input not in versiones:
            print("Input ingresado es erróneo.")
            print("Ejecución interrumpida de forma segura.")
            exit()
        else:
            version = user_input
        print(f"Seleccionado: {version}\n")
        
        file_name = version + ".pickle"
        
    print("Leyendo fichero...")
    
    try:
        df = return_file(file_name)
        print("Fichero leído con éxito.\n")
    except:
        print("Error al leer el fichero.")
        print("Ejecución interrumpida de forma segura.")
        exit()
    
    df.name = file_name#TODO: Existe una funcion para obtener "nombre" y "archivo".
    
    return df
    


if __name__ == "__main__":
    estructura_de_datos = obtener_informacion_ficheros(obtener_listado_ficheros())
    
    menu()
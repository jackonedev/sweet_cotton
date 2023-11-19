import sys, os

## Ubicación de los directorios - dirección
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
app_root = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
shared_resources = os.path.join(os.path.abspath(os.path.join(app_root, '..')), "shared_resources")

sys.path.insert(0, project_root)

from app.main.main import m1_sentiment
from tools.feature_adjust import eliminar_caracteres_no_imprimibles, aplicar_stopwords

def main(file_name:str=None):
    
    ## CARGA DE RECURSOS DESDE APP MAIN MAIN
    ## VARIABLES GENERALES
    print("Cargando configuración...")
    resources = m1_sentiment()
    shared_resources_feed = resources["shared_resources_feed"]
    
    if file_name:
        df = shared_resources_feed.menu(file_name)
    else:
        df = shared_resources_feed.menu()
    
    content_batch = df.content.to_list()
    content_batch = [eliminar_caracteres_no_imprimibles(row, conservar_simbolos=True) for row in content_batch]
    
    df['content'] = content_batch
    
    return df
    
if __name__ == "__main__":
    main()
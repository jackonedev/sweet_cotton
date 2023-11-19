from typing import Tuple, Optional
from pydantic import BaseModel, FilePath
from pathlib import Path
import os

class WordCloudConfig(BaseModel):
    mascara: FilePath
    relative_scaling: float
    max_words: int
    colormap: Optional[str] = None
    color_func: Tuple[int, int, int]
    min_font_size: int
    max_font_size: int
    mode: str = "RGBA"
    background_color: Optional[str] = None
    min_word_length: int
    prefer_horizontal: float




if __name__ == "__main__":
    print("hola mundo")
    
    ## obtener el path de este file
    
    # abrimos txt

    file_dir = os.path.dirname(__file__)
    mascara = Path(os.path.join(file_dir, "rectangulo.png"))#value del key
    
    # actualizamos key con el path
    
    config = WordCloudConfig(
        mascara=mascara,
        relative_scaling=0.12,
        max_words=77,
        colormap="Wistia",
        color_func=(35, 76, 229),
        min_font_size=14,
        max_font_size=120,
        mode="RGBA",
        background_color=None,
        min_word_length=5,
        prefer_horizontal=0.99
    )
    
    print()
    print(config.model_dump())
    print()
    
    print("programa finalizado de forma exitosa")
Notas:
1) Además de intalar las dependencias del archivo requirements.txt, instalar el siguiente modelo por consola:
```python -m spacy download es_core_news_sm```

2) La activación de filtros es automática, siempre que los ficheros de configuración correspondientes contengan palabras. Los filtros se aplican tanto al batch content como al de tokens.

3) Consideraciones: Los ficheros de configuración para filtros de palabras deben ser completados todos con palabras mínusculas y sin tíldes.
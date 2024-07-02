from fastapi import FastAPI, HTTPException, Query
from typing import List
import json
import yaml
from fastapi.responses import Response


# CREAR APP
app = FastAPI(
    title="API de Búsqueda de Componentes de Bantotal",
    description="Esta API permite buscar información sobre distintos componentes que conforman el software de Bantotals.",
    version="1.0.0",
    servers=[
        {"url": "https://127.0.0.1:8000", "description": "Servidor local"},
        {"url": "https://mi-servidor-produccion.com", "description": "Servidor de producción"}
    ]
)



# GENERAR OPENAPI
@app.get("/openapi.yaml", summary="Obtener especificación OpenAPI en YAML")
def get_openapi_yaml():
    """
    Retorna la especificación OpenAPI en formato YAML.
    """
    openapi_json = app.openapi()
    openapi_json['openapi'] = '3.0.3'  # Especificar la versión de OpenAPI
    openapi_yaml = yaml.dump(openapi_json, allow_unicode=True)
    return Response(content=openapi_yaml, media_type="application/x-yaml")

#  APLICACION DE TABLAS

## Cargar el archivo JSON con la codificación adecuada
with open('./data/tablas.json', encoding='utf-8') as f:
    tablas = json.load(f)


## Definir funcion de de buscar tablas
@app.get("/tablas/buscar_tablas", summary="Buscar por Tabla", description="Busca una tabla específica en el archivo JSON.")
def search_by_table(query: str = Query(..., description="String a buscar dentro de los nombres de las tablas")):
    """
    Busca una tabla específica en el archivo JSON.

    Parámetros:
    - **query**: String a buscar dentro de los nombres de las tablas.

    Retorna la tabla que coincide con la búsqueda o un error 404 si no se encuentra.
    """
    for tabla in tablas:
        if query.lower() in tabla['tabla'].lower():
            return tabla
    raise HTTPException(status_code=404, detail="Table not found")


## Definir funcion de de buscar atributos
@app.get("/tablas/buscar_atributo", summary="Buscar por Atributo", description="Busca un atributo específico en el archivo JSON. Puede filtrar por tabla.")
def search_by_attribute(
    query: str = Query(..., description="String a buscar dentro de los códigos de los atributos"),
    table_filter: str = Query("", description="Opcional. Filtra los resultados de búsqueda solo para la tabla especificada")
):
    """
    Busca un atributo específico en el archivo JSON. Puede filtrar por tabla.

    Parámetros:
    - **query**: String a buscar dentro de los códigos de los atributos.
    - **table_filter**: Opcional. Filtra los resultados de búsqueda solo para la tabla especificada.

    Retorna una lista de atributos que coinciden con la búsqueda o un error 404 si no se encuentran.
    """
    results = []
    for tabla in tablas:
        if table_filter and table_filter.lower() not in tabla['tabla'].lower():
            continue
        for atributo in tabla['atributos']:
            if query.lower() in atributo['codigo'].lower():
                results.append({
                    "tabla": tabla['tabla'],
                    "atributo": atributo
                })
    if not results:
        raise HTTPException(status_code=404, detail="Attribute not found")
    return results



# LANZAR APP
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


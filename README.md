# Conversor de TCX a GPX en Python

Este es un script sencillo y eficiente en Python para convertir archivos de actividad **.tcx** (Garmin Training Center) al formato estándar **.gpx**, manteniendo intactos los datos de geolocalización, tiempo, altitud y **frecuencia cardíaca (pulsaciones)**.

## Características
- 🚀 **Sin dependencias externas:** Solo utiliza la librería nativa de Python (`xml.etree.ElementTree`). No necesitas instalar nada con `pip`.
- ❤️ **Mantiene las pulsaciones:** Exporta la frecuencia cardíaca utilizando la extensión estándar de Garmin (`gpxtpx:hr`), compatible con Strava, MapMyRun, etc.
- 🧹 **Código limpio:** El archivo GPX generado incluye indentación para que sea fácilmente legible.

## Requisitos
- Python 3.9 o superior.

## Uso
1. Coloca tu archivo `.tcx` en la misma carpeta que el script `conversor.py`.
2. Edita las últimas líneas de `conversor.py` para poner el nombre de tu archivo:
   ```python
   archivo_origen = "tu_entrenamiento.tcx"
   archivo_destino = "resultado.gpx"

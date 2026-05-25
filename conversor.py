import xml.etree.ElementTree as ET
from datetime import datetime

def tcx_a_gpx(ruta_tcx, ruta_gpx):
    # Namespaces del archivo TCX (Garmin)
    ns_tcx = {'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
    
    try:
        tree = ET.parse(ruta_tcx)
        root = tree.getroot()
    except Exception as e:
        print(f"Error al leer el archivo TCX: {e}")
        return

    # Creamos la estructura base del archivo GPX
    gpx = ET.Element('gpx', {
        'version': '1.1',
        'creator': 'Python TCX to GPX Converter',
        'xmlns': 'http://www.topografix.com/GPX/1/1',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:schemaLocation': 'http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd '
                               'http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd',
        'xmlns:gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'
    })
    
    # Añadimos metadatos básicos con la hora actual
    metadata = ET.SubElement(gpx, 'metadata')
    time_meta = ET.SubElement(metadata, 'time')
    time_meta.text = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Creamos el elemento Track (trk) y el Track Segment (trkseg)
    trk = ET.SubElement(gpx, 'trk')
    trkseg = ET.SubElement(trk, 'trkseg')
    
    puntos_convertidos = 0

    # Buscamos todos los Trackpoints en el TCX
    for pt in root.findall('.//ns:Trackpoint', ns_tcx):
        lat_elem = pt.find('.//ns:LatitudeDegrees', ns_tcx)
        lon_elem = pt.find('.//ns:LongitudeDegrees', ns_tcx)
        time_elem = pt.find('ns:Time', ns_tcx)
        ele_elem = pt.find('ns:AltitudeMeters', ns_tcx)
        hr_elem = pt.find('.//ns:HeartRateBpm/ns:Value', ns_tcx)
        
        # Saltamos el punto si no tiene coordenadas (a veces pasa al pausar el GPS)
        if lat_elem is None or lon_elem is None:
            continue
            
        # Creamos el punto de track (trkpt) en el GPX
        trkpt = ET.SubElement(trkseg, 'trkpt', {
            'lat': lat_elem.text,
            'lon': lon_elem.text
        })
        
        # Añadimos la hora si existe
        if time_elem is not None:
            t = ET.SubElement(trkpt, 'time')
            t.text = time_elem.text
            
        # Añadimos la elevación/altitud si existe
        if ele_elem is not None:
            ele = ET.SubElement(trkpt, 'ele')
            ele.text = ele_elem.text
            
        # Si tiene pulsaciones, las metemos en las extensiones del GPX (compatible con Strava/Garmin)
        if hr_elem is not None:
            extensions = ET.SubElement(trkpt, 'extensions')
            gpxtpx = ET.SubElement(extensions, 'gpxtpx:TrackPointExtension')
            hr = ET.SubElement(gpxtpx, 'gpxtpx:hr')
            hr.text = hr_elem.text

        puntos_convertidos += 1

    # Guardamos el archivo GPX resultante con indentación
    tree_gpx = ET.ElementTree(gpx)
    try:
        ET.indent(tree_gpx, space="  ", level=0) # Para que el XML quede bonito y legible
        tree_gpx.write(ruta_gpx, encoding='utf-8', xml_declaration=True)
        print(f"¡Conversión exitosa! Se han procesado {puntos_convertidos} puntos.")
        print(f"Archivo guardado en: {ruta_gpx}")
    except Exception as e:
        print(f"Error al escribir el archivo GPX: {e}")

# --- EJECUCIÓN DEL SCRIPT ---
# Cambia estos nombres por tus archivos reales
archivo_origen = "mi_actividad.tcx"
archivo_destino = "mi_actividad.gpx"

tcx_a_gpx(archivo_origen, archivo_destino)

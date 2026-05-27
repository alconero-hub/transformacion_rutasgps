import xml.etree.ElementTree as ET
from datetime import datetime

def tcx_a_gpx_y_kml(ruta_tcx, ruta_gpx, ruta_kml):
    # Namespaces del archivo TCX (Garmin)
    ns_tcx = {'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
    
    try:
        tree = ET.parse(ruta_tcx)
        root = tree.getroot()
    except Exception as e:
        print(f"Error al leer el archivo TCX: {e}")
        return

    # -------------------------------------------------------------------------
    # 1. ESTRUCTURA BASE PARA GPX
    # -------------------------------------------------------------------------
    gpx = ET.Element('gpx', {
        'version': '1.1',
        'creator': 'Python TCX Converter',
        'xmlns': 'http://www.topografix.com/GPX/1/1',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:schemaLocation': 'http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd '
                               'http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd',
        'xmlns:gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'
    })
    
    metadata = ET.SubElement(gpx, 'metadata')
    time_meta = ET.SubElement(metadata, 'time')
    time_meta.text = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    trk = ET.SubElement(gpx, 'trk')
    trkseg = ET.SubElement(trk, 'trkseg')

    # -------------------------------------------------------------------------
    # 2. ESTRUCTURA BASE PARA KML
    # -------------------------------------------------------------------------
    kml = ET.Element('kml', {'xmlns': 'http://www.opengis.net/kml/2.2'})
    document = ET.SubElement(kml, 'Document')
    
    # Nombre de la ruta en KML
    name_kml = ET.SubElement(document, 'name')
    name_kml.text = f"Ruta convertida - {datetime.now().strftime('%Y-%m-%d')}"
    
    # Estilo de la línea en Google Earth (Color rojo, ancho de línea 4)
    style = ET.SubElement(document, 'Style', {'id': 'lineaRoja'})
    line_style = ET.SubElement(style, 'LineStyle')
    color = ET.SubElement(line_style, 'color')
    color.text = 'ff0000ff'  # Formato AABBGGRR (Opacidad, Azul, Verde, Rojo) -> Rojo opaco
    width = ET.SubElement(line_style, 'width')
    width.text = '4'
    
    placemark = ET.SubElement(document, 'Placemark')
    style_url = ET.SubElement(placemark, 'styleUrl')
    style_url.text = '#lineaRoja'
    
    line_string = ET.SubElement(placemark, 'LineString')
    # Activamos la altitud absoluta para que se dibuje correctamente en 3D
    altitude_mode = ET.SubElement(line_string, 'altitudeMode')
    altitude_mode.text = 'absolute'
    
    coordinates_elem = ET.SubElement(line_string, 'coordinates')

    # -------------------------------------------------------------------------
    # 3. PROCESAMIENTO DE PUNTOS
    # -------------------------------------------------------------------------
    lista_coordenadas_kml = []
    puntos_convertidos = 0

    for pt in root.findall('.//ns:Trackpoint', ns_tcx):
        lat_elem = pt.find('.//ns:LatitudeDegrees', ns_tcx)
        lon_elem = pt.find('.//ns:LongitudeDegrees', ns_tcx)
        time_elem = pt.find('ns:Time', ns_tcx)
        ele_elem = pt.find('ns:AltitudeMeters', ns_tcx)
        hr_elem = pt.find('.//ns:HeartRateBpm/ns:Value', ns_tcx)
        
        if lat_elem is None or lon_elem is None:
            continue
            
        lat = lat_elem.text
        lon = lon_elem.text
        ele = ele_elem.text if ele_elem is not None else "0"
        
        # --- Añadir al GPX ---
        trkpt = ET.SubElement(trkseg, 'trkpt', {'lat': lat, 'lon': lon})
        if time_elem is not None:
            t = ET.SubElement(trkpt, 'time')
            t.text = time_elem.text
        if ele_elem is not None:
            e = ET.SubElement(trkpt, 'ele')
            e.text = ele
        if hr_elem is not None:
            extensions = ET.SubElement(trkpt, 'extensions')
            gpxtpx = ET.SubElement(extensions, 'gpxtpx:TrackPointExtension')
            hr = ET.SubElement(gpxtpx, 'gpxtpx:hr')
            hr.text = hr_elem.text

        # --- Añadir al KML ---
        # El formato KML requiere: longitud,latitud,altitud (separados por comas, sin espacios)
        lista_coordenadas_kml.append(f"{lon},{lat},{ele}")
        
        puntos_convertidos += 1

    # Guardamos los puntos en la estructura KML (unidos por espacios o saltos de línea)
    coordinates_elem.text = "\n".join(lista_coordenadas_kml)

    # -------------------------------------------------------------------------
    # 4. ESCRITURA DE ARCHIVOS
    # -------------------------------------------------------------------------
    # Guardar GPX
    tree_gpx = ET.ElementTree(gpx)
    ET.indent(tree_gpx, space="  ", level=0)
    tree_gpx.write(ruta_gpx, encoding='utf-8', xml_declaration=True)
    
    # Guardar KML
    tree_kml = ET.ElementTree(kml)
    ET.indent(tree_kml, space="  ", level=0)
    tree_kml.write(ruta_kml, encoding='utf-8', xml_declaration=True)
    
    print(f"¡Hecho! Se han procesado {puntos_convertidos} puntos.")
    print(f"-> Guardado GPX: {ruta_gpx}")
    print(f"-> Guardado KML: {ruta_kml}")

# --- EJECUCIÓN DEL SCRIPT ---
# Asegúrate de cambiar el nombre al de tu archivo real
archivo_origen = "mi_actividad.tcx"
archivo_gpx = "mi_actividad.gpx"
archivo_kml = "mi_actividad.kml"

tcx_a_gpx_y_kml(archivo_origen, archivo_gpx, archivo_kml)

import xml.etree.ElementTree as ET
from datetime import datetime
import math

def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    """Calcula la distancia en metros entre dos coordenadas usando Haversine."""
    R = 6371000  # Radio de la Tierra en metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def tcx_a_gpx_y_kml(ruta_tcx, ruta_gpx, ruta_kml):
    ns_tcx = {'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
    
    try:
        tree = ET.parse(ruta_tcx)
        root = tree.getroot()
    except Exception as e:
        print(f"Error al leer el archivo TCX: {e}")
        return

    # --- 1. ESTRUCTURAS BASE (GPX y KML) ---
    gpx = ET.Element('gpx', {
        'version': '1.1',
        'creator': 'Python TCX Converter',
        'xmlns': 'http://www.topografix.com/GPX/1/1',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:schemaLocation': 'http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd',
        'xmlns:gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'
    })
    
    metadata = ET.SubElement(gpx, 'metadata')
    time_meta = ET.SubElement(metadata, 'time')
    time_meta.text = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    trk = ET.SubElement(gpx, 'trk')
    trkseg = ET.SubElement(trk, 'trkseg')

    kml = ET.Element('kml', {'xmlns': 'http://www.opengis.net/kml/2.2'})
    document = ET.SubElement(kml, 'Document')
    name_kml = ET.SubElement(document, 'name')
    name_kml.text = f"Ruta - {datetime.now().strftime('%Y-%m-%d')}"
    
    style = ET.SubElement(document, 'Style', {'id': 'lineaRoja'})
    line_style = ET.SubElement(style, 'LineStyle')
    ET.SubElement(line_style, 'color').text = 'ff0000ff'
    ET.SubElement(line_style, 'width').text = '4'
    
    placemark = ET.SubElement(document, 'Placemark')
    ET.SubElement(placemark, 'styleUrl').text = '#lineaRoja'
    line_string = ET.SubElement(placemark, 'LineString')
    ET.SubElement(line_string, 'altitudeMode').text = 'absolute'
    coordinates_elem = ET.SubElement(line_string, 'coordinates')

    # --- 2. VARIABLES DE MÉTRICAS ---
    lista_coordenadas_kml = []
    puntos_convertidos = 0
    
    distancia_total_m = 0.0
    desnivel_positivo_m = 0.0
    altitud_maxima_m = -float('inf')
    
    ultimo_lat = None
    ultimo_lon = None
    ultima_altitud = None

    # --- 3. PROCESAMIENTO DE PUNTOS ---
    for pt in root.findall('.//ns:Trackpoint', ns_tcx):
        lat_elem = pt.find('.//ns:LatitudeDegrees', ns_tcx)
        lon_elem = pt.find('.//ns:LongitudeDegrees', ns_tcx)
        time_elem = pt.find('ns:Time', ns_tcx)
        ele_elem = pt.find('ns:AltitudeMeters', ns_tcx)
        hr_elem = pt.find('.//ns:HeartRateBpm/ns:Value', ns_tcx)
        
        if lat_elem is None or lon_elem is None:
            continue
            
        lat = float(lat_elem.text)
        lon = float(lon_elem.text)
        ele = float(ele_elem.text) if ele_elem is not None else 0.0
        
        # CÁLCULO DE DISTANCIA
        if ultimo_lat is not None and ultimo_lon is not None:
            distancia_total_m += calcular_distancia_haversine(ultimo_lat, ultimo_lon, lat, lon)
            
        # CÁLCULO DE DESNIVEL Y ALTITUD MÁXIMA
        if ele_elem is not None:
            if ele > altitud_maxima_m:
                altitud_maxima_m = ele
                
            if ultima_altitud is not None:
                diferencia_altitud = ele - ultima_altitud
                if diferencia_altitud > 0:
                    desnivel_positivo_m += diferencia_altitud

        # Guardar estado para el siguiente punto
        ultimo_lat = lat
        ultimo_lon = lon
        if ele_elem is not None:
            ultima_altitud = ele
        
        # --- Añadir al GPX ---
        trkpt = ET.SubElement(trkseg, 'trkpt', {'lat': str(lat), 'lon': str(lon)})
        if time_elem is not None:
            ET.SubElement(trkpt, 'time').text = time_elem.text
        if ele_elem is not None:
            ET.SubElement(trkpt, 'ele').text = str(ele)
        if hr_elem is not None:
            extensions = ET.SubElement(trkpt, 'extensions')
            gpxtpx = ET.SubElement(extensions, 'gpxtpx:TrackPointExtension')
            ET.SubElement(gpxtpx, 'gpxtpx:hr').text = hr_elem.text

        # --- Añadir al KML ---
        lista_coordenadas_kml.append(f"{lon},{lat},{ele}")
        puntos_convertidos += 1

    # Cerrar KML
    coordinates_elem.text = "\n".join(lista_coordenadas_kml)

    # --- 4. ESCRITURA DE ARCHIVOS ---
    tree_gpx = ET.ElementTree(gpx)
    ET.indent(tree_gpx, space="  ", level=0)
    tree_gpx.write(ruta_gpx, encoding='utf-8', xml_declaration=True)
    
    tree_kml = ET.ElementTree(kml)
    ET.indent(tree_kml, space="  ", level=0)
    tree_kml.write(ruta_kml, encoding='utf-8', xml_declaration=True)
    
    # Si no se encontraron datos de altitud, ajustamos el máximo a 0
    if altitud_maxima_m == -float('inf'):
        altitud_maxima_m = 0.0

    # --- 5. RESUMEN POR PANTALLA ---
    print("=" * 45)
    print(" 🚀 PROCESAMIENTO COMPLETADO EXITOSAMENTE")
    print("=" * 45)
    print(f" -> Puntos procesados : {puntos_convertidos}")
    print(f" -> Archivo GPX       : {ruta_gpx}")
    print(f" -> Archivo KML       : {ruta_kml}")
    print("-" * 45)
    print(" 📈 RESUMEN DE LA ACTIVIDAD:")
    print("-" * 45)
    print(f" 🏃 Distancia Total    : {distancia_total_m / 1000:.2f} km")
    print(f" ⛰️  Desnivel Positivo : {desnivel_positivo_m:.0f} m")
    print(f" 🔝 Altitud Máxima    : {altitud_maxima_m:.0f} m")
    print("=" * 45)

# --- EJECUCIÓN DEL SCRIPT ---
archivo_origen = "mi_actividad.tcx"
archivo_gpx = "mi_actividad.gpx"
archivo_kml = "mi_actividad.kml"

tcx_a_gpx_y_kml(archivo_origen, archivo_gpx, archivo_kml)

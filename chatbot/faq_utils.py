import pandas as pd
import os
import csv
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# Ruta base de documentos
BASE_DIR = os.path.join("media", "docs")


def agregar_faq_entry_simple(pregunta, respuesta, categoria="General"):
    """
    Versión simplificada para agregar FAQ con formato correcto
    """
    faq_csv = os.path.join(BASE_DIR, "basecsvf.csv")
    
    try:
        # Crear directorio si no existe
        os.makedirs(BASE_DIR, exist_ok=True)
        
        # Verificar si el archivo existe
        file_exists = os.path.exists(faq_csv)
        
        # Obtener el próximo ID
        next_id = 1
        if file_exists and os.path.getsize(faq_csv) > 0:
            try:
                df = pd.read_csv(faq_csv, quotechar='"', skipinitialspace=True, on_bad_lines='skip')
                if not df.empty and 'id' in df.columns:
                    next_id = df['id'].max() + 1
            except Exception as e:
                logger.warning(f"No se pudo determinar el próximo ID: {e}")
                next_id = 1
        
        fecha_actual = timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + '+00:00'
        
        # Preparar los datos con la estructura correcta
        nueva_entrada = {
            'id': next_id,
            'Pregunta': pregunta.strip(),
            'Respuesta': respuesta.strip(),
            'Categoría': categoria.strip(),
            'fechaCreacion': fecha_actual,
            'fechaModificacion': fecha_actual
        }
        
        # Escribir al CSV
        with open(faq_csv, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'Pregunta', 'Respuesta', 'Categoría', 'fechaCreacion', 'fechaModificacion']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Si el archivo es nuevo, escribir los headers
            if not file_exists or os.path.getsize(faq_csv) == 0:
                writer.writeheader()
            
            writer.writerow(nueva_entrada)
        
        logger.info(f"FAQ agregado exitosamente con ID {next_id}: {pregunta[:50]}...")
        
        return {
            'success': True,
            'message': 'FAQ agregado exitosamente',
            'entrada': nueva_entrada
        }
        
    except Exception as e:
        logger.error(f"Error al agregar FAQ: {str(e)}")
        return {
            'success': False,
            'message': f'Error al agregar FAQ: {str(e)}',
            'entrada': None
        }


def validar_faq_duplicado_simple(pregunta, umbral_similitud=0.8):
    """
    Versión simplificada para verificar duplicados
    """
    faq_csv = os.path.join(BASE_DIR, "basecsvf.csv")
    
    if not os.path.exists(faq_csv):
        return {'es_duplicado': False, 'pregunta_similar': None, 'similitud': 0}
    
    try:
        df = pd.read_csv(faq_csv, quotechar='"', skipinitialspace=True, on_bad_lines='skip')
        df = df.dropna(subset=["Pregunta"])
        
        pregunta_lower = pregunta.lower().strip()
        max_similitud = 0
        pregunta_similar = None
        
        for _, row in df.iterrows():
            pregunta_existente = str(row['Pregunta']).lower().strip()
            
            # Calcular similitud básica
            if pregunta_lower in pregunta_existente or pregunta_existente in pregunta_lower:
                similitud = 0.9  # Alta similitud si una contiene a la otra
            else:
                # Similitud básica por palabras comunes
                palabras_pregunta = set(pregunta_lower.split())
                palabras_existente = set(pregunta_existente.split())
                palabras_comunes = palabras_pregunta.intersection(palabras_existente)
                total_palabras = len(palabras_pregunta.union(palabras_existente))
                similitud = len(palabras_comunes) / total_palabras if total_palabras > 0 else 0
            
            if similitud > max_similitud:
                max_similitud = similitud
                pregunta_similar = str(row['Pregunta'])
        
        es_duplicado = max_similitud >= umbral_similitud
        
        return {
            'es_duplicado': es_duplicado,
            'pregunta_similar': pregunta_similar if es_duplicado else None,
            'similitud': max_similitud
        }
        
    except Exception as e:
        logger.error(f"Error al validar duplicados: {str(e)}")
        return {'es_duplicado': False, 'pregunta_similar': None, 'similitud': 0}


def obtener_estadisticas_faq_simple():
    """
    Versión simplificada para obtener estadísticas
    """
    faq_csv = os.path.join(BASE_DIR, "basecsvf.csv")
    
    if not os.path.exists(faq_csv):
        return {
            'total_preguntas': 0,
            'archivo_existe': False,
            'tamaño_archivo': 0
        }
    
    try:
        df = pd.read_csv(faq_csv, quotechar='"', skipinitialspace=True, on_bad_lines='skip')
        df = df.dropna(subset=["Pregunta", "Respuesta"])
        
        return {
            'total_preguntas': len(df),
            'archivo_existe': True,
            'tamaño_archivo': os.path.getsize(faq_csv),
            'ultima_modificacion': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {str(e)}")
        return {
            'total_preguntas': 0,
            'archivo_existe': True,
            'tamaño_archivo': os.path.getsize(faq_csv) if os.path.exists(faq_csv) else 0,
            'error': str(e)
        }

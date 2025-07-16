import pandas as pd
import os
import re
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import csv
from django.utils import timezone
import logging
import boto3
from botocore.exceptions import ClientError
import tempfile
from django.conf import settings
import requests

logger = logging.getLogger(__name__)

# Ruta base de documentos
BASE_DIR = os.path.join("media", "docs")

def get_s3_client():
    """Obtiene cliente S3 configurado"""
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

def download_from_s3(filename):
    """Descarga un archivo desde S3 a un archivo temporal"""
    try:
        s3_client = get_s3_client()
        s3_key = f"media/docs/{filename}"
        
        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1])
        temp_file.close()
        
        # Descargar desde S3
        s3_client.download_file(settings.AWS_STORAGE_BUCKET_NAME, s3_key, temp_file.name)
        
        return temp_file.name
        
    except Exception as e:
        logger.error(f"Error descargando {filename} desde S3: {e}")
        return None

def get_file_from_s3_or_local(filename):
    """Obtiene archivo desde S3 o desde el directorio local como fallback"""
    # Intentar primero desde S3
    temp_path = download_from_s3(filename)
    if temp_path:
        return temp_path, True  # True indica que es temporal
    
    # Fallback a archivo local
    local_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(local_path):
        return local_path, False  # False indica que no es temporal
    
    return None, False

def download_csv_from_s3(filename):
    """Descarga y lee un CSV desde S3"""
    try:
        s3_client = get_s3_client()
        s3_key = f"media/docs/{filename}"
        
        # Obtener el objeto desde S3
        response = s3_client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_key)
        csv_content = response['Body'].read().decode('utf-8')
        
        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        temp_file.write(csv_content)
        temp_file.close()
        
        return temp_file.name
        
    except Exception as e:
        logger.error(f"Error descargando CSV {filename} desde S3: {e}")
        return None

def list_s3_files():
    """Lista archivos en S3"""
    try:
        s3_client = get_s3_client()
        response = s3_client.list_objects_v2(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Prefix='media/docs/'
        )
        
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                filename = obj['Key'].replace('media/docs/', '')
                if filename:  # Ignorar carpetas vacías
                    files.append(filename)
        
        return files
        
    except Exception as e:
        logger.error(f"Error listando archivos S3: {e}")
        return []

def limpiar_contenido_web(texto):
    """
    Limpia texto extraído del sitio web del DCCO para eliminar navegación, encabezados y ruido visual.
    """
    # 1. Unificar saltos de línea
    texto = re.sub(r'\n+', '\n', texto)
    lineas = texto.split("\n")
    lineas_limpias = []

    # 2. Definir patrones de líneas que suelen ser navegación o títulos
    patrones_basura = [
        r'^(Saltar al contenido|Alternar menú)$',
        r'^(QUIÉNES SOMOS|INVESTIGACIÓN|PROYECTOS|PUBLICACIONES|SERVICIOS)$',
        r'^(Departamentos y Centros|Eventos|Libros|Revistas|Estadísticas|Noticias Vinculación|Convenios)$',
        r'^(Filosofía|Autoridades|Áreas de Conocimiento|Planta Docente|Horario de Atención|Resultados de la Investigación)$',
        r'^Página principal$', r'^Inicio$', r'^Menú$', r'^Información$', r'^Descripción$'
    ]

    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue
        if any(re.match(p, linea, re.IGNORECASE) for p in patrones_basura):
            continue
        if len(linea.split()) <= 2 and linea.isupper():
            continue  # evitar encabezados tipo "SERVICIOS"
        if len(linea) < 5:
            continue  # saltar texto muy corto que suele ser ruido

        lineas_limpias.append(linea)

    return "\n".join(lineas_limpias).strip()


def cargar_documentos():
    all_docs = []

    # 1. Cargar CSV de FAQ desde S3
    faq_csv_temp = download_csv_from_s3("basecsvf.csv")
    if faq_csv_temp:
        try:
            # Intentar leer el CSV con diferentes configuraciones para manejar problemas de formato
            df = pd.read_csv(faq_csv_temp, quotechar='"', skipinitialspace=True, on_bad_lines='skip')
            
            # Verificar que tenga las columnas esperadas (con flexibilidad en mayúsculas/minúsculas)
            columns_lower = [col.lower() for col in df.columns]
            if 'pregunta' in columns_lower and 'respuesta' in columns_lower:
                # Normalizar nombres de columnas
                df.columns = [col.lower().capitalize() for col in df.columns]
                df = df.dropna(subset=["Pregunta", "Respuesta"])

                for _, row in df.iterrows():
                    contenido = f"Pregunta: {row['Pregunta']}\nRespuesta: {row['Respuesta']}"
                    doc = Document(
                        page_content=contenido,
                        metadata={
                            "source": "faq",
                            "tipo": "faq",
                            "pregunta_original": row["Pregunta"],
                            "respuesta_original": row["Respuesta"]
                        }
                    )
                    all_docs.append(doc)
                    
                logger.info(f"✅ CSV FAQ cargado desde S3: {len(df)} entradas")
            else:
                logger.warning(f"CSV no tiene las columnas esperadas. Columnas encontradas: {df.columns.tolist()}")
                logger.warning("Columnas esperadas: 'Pregunta' y 'Respuesta'")
                
        except Exception as e:
            logger.error(f"Error al parsear CSV desde S3: {e}")
        finally:
            # Limpiar archivo temporal
            if os.path.exists(faq_csv_temp):
                os.unlink(faq_csv_temp)
    else:
        # Fallback a archivo local
        faq_csv = os.path.join(BASE_DIR, "basecsvf.csv")
        if os.path.exists(faq_csv):
            try:
                df = pd.read_csv(faq_csv, quotechar='"', skipinitialspace=True, on_bad_lines='skip')
                if 'Pregunta' in df.columns and 'Respuesta' in df.columns:
                    df = df.dropna(subset=["Pregunta", "Respuesta"])
                    for _, row in df.iterrows():
                        contenido = f"Pregunta: {row['Pregunta']}\nRespuesta: {row['Respuesta']}"
                        doc = Document(
                            page_content=contenido,
                            metadata={
                                "source": "faq",
                                "tipo": "faq",
                                "pregunta_original": row["Pregunta"],
                                "respuesta_original": row["Respuesta"]
                            }
                        )
                        all_docs.append(doc)
                    logger.info(f"✅ CSV FAQ cargado localmente: {len(df)} entradas")
            except Exception as e:
                logger.error(f"Error al parsear CSV local: {e}")

    # 2. Cargar contenido web DCCO (scraping limpio)
    web_csv_temp = download_csv_from_s3("contenido_web_dcco.csv")
    if web_csv_temp:
        try:
            df = pd.read_csv(web_csv_temp)
            df = df.dropna(subset=["Titulo", "Contenido"])

            for _, row in df.iterrows():
                contenido_limpio = limpiar_contenido_web(row["Contenido"])
                doc = Document(
                    page_content=contenido_limpio,
                    metadata={
                        "source": "web",
                        "tipo": "web",
                        "titulo": row["Titulo"],
                        "url": row.get("URL", "")
                    }
                )
                all_docs.append(doc)
                logger.info(f"[WEB] {row['Titulo']} cargado desde {row.get('URL', '')}")
        except Exception as e:
            logger.error(f"Error cargando contenido web desde S3: {e}")
        finally:
            if os.path.exists(web_csv_temp):
                os.unlink(web_csv_temp)

    # 3. Cargar PDFs desde S3
    pdf_count = 0
    pdf_chunks_total = 0
    
    try:
        # Listar archivos PDF en S3
        s3_files = list_s3_files()
        pdf_files = [f for f in s3_files if f.endswith(".pdf")]
        logger.info(f"Encontrados {len(pdf_files)} archivos PDF en S3")
        
        for filename in pdf_files:
            try:
                logger.info(f"Cargando PDF desde S3: {filename}")
                
                # Descargar PDF desde S3
                pdf_path, is_temp = get_file_from_s3_or_local(filename)
                if not pdf_path:
                    logger.error(f"No se pudo obtener el PDF: {filename}")
                    continue
                
                loader = PyMuPDFLoader(pdf_path)
                raw_docs = loader.load()
                
                # Limpiar archivo temporal si es necesario
                if is_temp:
                    os.unlink(pdf_path)
                
                if not raw_docs:
                    logger.warning(f"PDF {filename} está vacío o no se pudo leer")
                    continue
                
                # Verificar contenido antes de dividir
                total_content = "".join([doc.page_content for doc in raw_docs])
                if len(total_content.strip()) < 100:
                    logger.warning(f"PDF {filename} tiene muy poco contenido: {len(total_content)} caracteres")
                
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=500, 
                    chunk_overlap=50,
                    separators=["\n\n", "\n", " ", ""]
                )
                split_docs = splitter.split_documents(raw_docs)
                
                chunks_count = 0
                for i, doc in enumerate(split_docs):
                    if len(doc.page_content.strip()) < 50:  # Filtrar chunks muy pequeños
                        continue
                        
                    doc.metadata.update({
                        "source": "pdf",
                        "filename": filename,
                        "chunk_id": i,
                        "tipo": "pdf",
                        "tipo_documento": "pdf_syllabus",
                        "total_chunks": len(split_docs)
                    })
                    all_docs.append(doc)
                    chunks_count += 1
                
                pdf_count += 1
                pdf_chunks_total += chunks_count
                logger.info(f"✅ PDF {filename} cargado desde S3: {chunks_count} chunks válidos de {len(split_docs)} totales")
                
            except Exception as e:
                logger.error(f"❌ Error cargando PDF {filename} desde S3: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"❌ Error accediendo a archivos PDF en S3: {str(e)}")
    
    logger.info(f"📊 Total PDFs cargados: {pdf_count}, Total chunks: {pdf_chunks_total}")
    logger.info(f"📊 Total documentos cargados: {len(all_docs)}")
    
    logger.info(f"📊 Total PDFs cargados: {pdf_count}, Total chunks: {pdf_chunks_total}")
    logger.info(f"📊 Total documentos cargados: {len(all_docs)}")
    
    return all_docs


def agregar_faq_entry(pregunta, respuesta):
    """
    Agrega una nueva entrada al archivo CSV de FAQ
    
    Args:
        pregunta (str): La pregunta a agregar
        respuesta (str): La respuesta correspondiente
    
    Returns:
        dict: Resultado de la operación con éxito/error
    """
    faq_csv = os.path.join(BASE_DIR, "basecsvf.csv")
    
    try:
        # Crear directorio si no existe
        os.makedirs(BASE_DIR, exist_ok=True)
        
        # Verificar si el archivo existe, si no, crearlo con headers
        file_exists = os.path.exists(faq_csv)
        
        # Preparar los datos
        nueva_entrada = {
            'Pregunta': pregunta.strip(),
            'Respuesta': respuesta.strip(),
            'Fecha_Agregado': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Escribir al CSV
        with open(faq_csv, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Pregunta', 'Respuesta', 'Fecha_Agregado']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Si el archivo es nuevo, escribir los headers
            if not file_exists or os.path.getsize(faq_csv) == 0:
                writer.writeheader()
            
            writer.writerow(nueva_entrada)
        
        logger.info(f"FAQ agregado exitosamente: {pregunta[:50]}...")
        
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


def validar_faq_duplicado(pregunta, umbral_similitud=0.8):
    """
    Verifica si ya existe una pregunta similar en el FAQ
    
    Args:
        pregunta (str): La pregunta a verificar
        umbral_similitud (float): Umbral de similitud para considerar duplicado
    
    Returns:
        dict: Información sobre duplicados encontrados
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
            
            # Calcular similitud usando SequenceMatcher
            from difflib import SequenceMatcher
            similitud = SequenceMatcher(None, pregunta_lower, pregunta_existente).ratio()
            
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


def obtener_estadisticas_faq():
    """
    Obtiene estadísticas básicas del archivo FAQ
    
    Returns:
        dict: Estadísticas del FAQ
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
            'ultima_modificacion': timezone.datetime.fromtimestamp(
                os.path.getmtime(faq_csv)
            ).strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {str(e)}")
        return {
            'total_preguntas': 0,
            'archivo_existe': True,
            'tamaño_archivo': os.path.getsize(faq_csv),
            'error': str(e)
        }

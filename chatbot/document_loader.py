import pandas as pd
import os
import re
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import csv
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# Ruta base de documentos
BASE_DIR = os.path.join("media", "docs")

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

    # 1. Cargar CSV de FAQ
    faq_csv = os.path.join(BASE_DIR, "basecsvf.csv")
    if os.path.exists(faq_csv):
        try:
            # Intentar leer el CSV con diferentes configuraciones para manejar problemas de formato
            df = pd.read_csv(faq_csv, quotechar='"', skipinitialspace=True, on_bad_lines='skip')
        except pd.errors.ParserError as e:
            print(f"Error al parsear CSV: {e}")
            # Intentar con configuración más flexible
            try:
                df = pd.read_csv(faq_csv, sep=',', quotechar='"', escapechar='\\', on_bad_lines='skip')
            except Exception as backup_error:
                print(f"Error de backup al parsear CSV: {backup_error}")
                # Si todo falla, crear un DataFrame vacío para continuar
                df = pd.DataFrame(columns=['Pregunta', 'Respuesta'])
        
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

    # 2. Cargar contenido web DCCO (scraping limpio)
    web_csv = os.path.join(BASE_DIR, "contenido_web_dcco.csv")
    if os.path.exists(web_csv):
        df = pd.read_csv(web_csv)
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
            print(f"[WEB] {row['Titulo']} cargado desde {row.get('URL', '')}")

    # 3. Cargar PDFs
    pdf_count = 0
    pdf_chunks_total = 0
    
    try:
        pdf_files = [f for f in os.listdir(BASE_DIR) if f.endswith(".pdf")]
        logger.info(f"Encontrados {len(pdf_files)} archivos PDF en {BASE_DIR}")
        
        for filename in pdf_files:
            try:
                pdf_path = os.path.join(BASE_DIR, filename)
                logger.info(f"Cargando PDF: {filename}")
                
                loader = PyMuPDFLoader(pdf_path)
                raw_docs = loader.load()
                
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
                logger.info(f"✅ PDF {filename} cargado: {chunks_count} chunks válidos de {len(split_docs)} totales")
                
            except Exception as e:
                logger.error(f"❌ Error cargando PDF {filename}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"❌ Error accediendo al directorio de PDFs: {str(e)}")
    
    logger.info(f"📊 Total PDFs cargados: {pdf_count}, Total chunks: {pdf_chunks_total}")
    
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

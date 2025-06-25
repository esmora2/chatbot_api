from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import time
import re
import csv

# Configuración de Selenium
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

# URL de la página que quieres scrape
url = "https://dcco.espe.edu.ec/"  # Cambia por la URL que desees scrapear
response =  requests.get(url)

soup = BeautifulSoup(response.content, "html.parser")

driver.get(url)
time.sleep(3)  # Esperar 3 segundos para asegurar que la página cargue completamente
soup = BeautifulSoup(driver.page_source, "html.parser")

# Función para limpiar el contenido de texto
def limpiar_texto(texto):
    """
    Elimina texto irrelevante, saltos de línea extra, espacios en blanco y palabras comunes
    que no aportan valor al contenido.
    """
    # Limpiar espacios en blanco innecesarios y saltos de línea
    texto = re.sub(r'\s+', ' ', texto.strip())
    
    # Eliminar algunas palabras no necesarias (ajusta esta lista según lo que encuentres)
    palabras_comunes = [
        "comunicación", "mensaje", "información", "noticias", "servicios", 
        "contactos", "acerca de", "contactar", "información adicional", 
        "dirección", "horarios", "redes sociales"
    ]
    for palabra in palabras_comunes:
        texto = texto.replace(palabra, '')
    
    # Eliminar saltos de línea extras o tabulaciones
    texto = texto.replace("\n", " ").replace("\r", "").strip()

    return texto

# Función para extraer contenido relevante
def extraer_contenido(soup):
    contenido_relevante = []

    # Encuentra todo el texto dentro de las etiquetas <p> (párrafos)
    parrafos = soup.find_all("p")
    for p in parrafos:
        texto = p.get_text()
        texto_limpio = limpiar_texto(texto)
        if texto_limpio:
            contenido_relevante.append(texto_limpio)
    
    # Encuentra contenido dentro de otros elementos como <h1>, <h2>, <h3> (títulos)
    for etiqueta in ["h1", "h2", "h3"]:
        titulos = soup.find_all(etiqueta)
        for titulo in titulos:
            texto = titulo.get_text()
            texto_limpio = limpiar_texto(texto)
            if texto_limpio:
                contenido_relevante.append(texto_limpio)

    # Extraer texto de las listas (ul/li) si es relevante
    listas = soup.find_all("ul")
    for lista in listas:
        items = lista.find_all("li")
        for item in items:
            texto = item.get_text()
            texto_limpio = limpiar_texto(texto)
            if texto_limpio:
                contenido_relevante.append(texto_limpio)

    # Extraer cualquier otro tipo de contenido que sea relevante
    # (por ejemplo, links o textos en divs específicos)
    divs = soup.find_all("div")
    for div in divs:
        texto = div.get_text()
        texto_limpio = limpiar_texto(texto)
        if texto_limpio:
            contenido_relevante.append(texto_limpio)

    return contenido_relevante

# Llamar a la función para extraer el contenido limpio
contenido_extraido = extraer_contenido(soup)

# Guardar el contenido extraído en un archivo CSV
with open("contenido_extraido.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Contenido"])  # Escribimos un encabezado
    for linea in contenido_extraido:
        writer.writerow([linea])  # Escribimos cada línea de texto extraído

print("✅ Contenido extraído y guardado en 'contenido_extraido.csv'.")

# Cerrar el navegador
driver.quit()

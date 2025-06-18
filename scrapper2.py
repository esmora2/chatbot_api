from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def extract_main_content(soup):
    """Extrae contenido principal eliminando elementos no deseados"""
    for tag in soup(["script", "style", "nav", "footer", "iframe"]):
        tag.decompose()
        
    main_content = soup.find("main") or \
                  soup.find("article") or \
                  soup.find("div", {"role": "main"}) or \
                  soup.find("div", class_=lambda x: x and "content" in x.lower())
    
    return main_content.get_text(separator="\n", strip=True) if main_content else ""

def scrape_site(base_url):
    driver = setup_driver()
    driver.get(base_url)
    
    try:
        # Esperar a que cargue el menú (corregido el paréntesis faltante)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul[id*='menu'], nav, ul.menu")))
        
        # Extraer enlaces
        soup = BeautifulSoup(driver.page_source, "html.parser")
        menu = soup.find("ul", id=lambda x: x and "menu" in x) or \
              soup.find("nav") or \
              soup.find("ul", class_="menu")
        
        if not menu:
            raise ValueError("No se encontró el menú principal")
            
        enlaces = []
        def extract_links(element):
            items = element.find_all("li", recursive=False)
            for item in items:
                if a := item.find("a", href=True):
                    if a["href"] not in ["#", ""] and not a["href"].startswith(("javascript:", "mailto:")):
                        enlaces.append((a.get_text(strip=True), 
                                      a["href"] if a["href"].startswith("http") else f"{base_url.rstrip('/')}/{a['href'].lstrip('/')}"))
                if submenu := item.find("ul"):
                    extract_links(submenu)
        
        extract_links(menu)
        
        # Scrapear páginas
        resultados = []
        for titulo, url in enlaces[:20]:  # Limitar para prueba
            try:
                driver.get(url)
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
                
                page = BeautifulSoup(driver.page_source, "html.parser")
                contenido = extract_main_content(page)
                
                if contenido:
                    resultados.append({
                        "titulo": titulo,
                        "url": url,
                        "contenido": contenido[:10000],  # Aumentar límite
                        "fecha_scraping": time.strftime("%Y-%m-%d")
                    })
                    print(f"✅ {titulo} - {len(contenido)} caracteres")
                
            except Exception as e:
                print(f"❌ Error en {url}: {str(e)}")
                continue
                
        return resultados
        
    except Exception as e:  # Añadido bloque except faltante
        print(f"❌ Error general: {str(e)}")
        return []
    finally:
        driver.quit()

# Ejecución (corregida la separación de declaraciones)
if __name__ == "__main__":
    datos = scrape_site("https://dcco.espe.edu.ec/")
    
    if datos:
        with open("media/docs/contenido_web_dcco_mejorado.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["titulo", "url", "contenido", "fecha_scraping"])
            writer.writeheader()
            writer.writerows(datos)
        print(f"✅ Datos guardados ({len(datos)} páginas)")
    else:
        print("❌ No se obtuvieron datos")
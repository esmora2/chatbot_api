from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import csv

# Configuración del navegador
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

# Abrir página principal
driver.get("https://dcco.espe.edu.ec/")
time.sleep(3)
soup = BeautifulSoup(driver.page_source, "html.parser")

# Encontrar menú principal
menu = soup.find("ul", id="menu-micrositio-departamentos-centros")

# Extraer enlaces del menú
enlaces = []

def extraer_links(ul):
    items = ul.find_all("li", recursive=False)
    for item in items:
        a = item.find("a")
        if a and a.get("href") and a.get("href") != "#":
            enlaces.append((a.get_text(strip=True), a["href"]))
        submenu = item.find("ul", class_="sub-menu")
        if submenu:
            extraer_links(submenu)

extraer_links(menu)

# Visitar cada enlace y guardar texto
resultados = []
for titulo, url in enlaces:
    try:
        driver.get(url)
        time.sleep(2)
        page = BeautifulSoup(driver.page_source, "html.parser")
        texto = page.get_text(separator="\n", strip=True)
        resultados.append((titulo, url, texto[:5000]))  # limitar a 5k chars
        print(f"[OK] {titulo}")
    except Exception as e:
        print(f"[ERROR] {url}: {e}")

driver.quit()

# Guardar en CSV
with open("media/docs/contenido_web_dcco.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Titulo", "URL", "Contenido"])
    writer.writerows(resultados)

print("✅ Contenido guardado en 'contenido_web_dcco.csv'")

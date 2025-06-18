from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Configurar Selenium con Chrome en modo headless
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
url = "https://dcco.espe.edu.ec/"
driver.get(url)
time.sleep(3)  # esperar a que el JS cargue

html = driver.page_source
driver.quit()

soup = BeautifulSoup(html, "html.parser")

# Usar el ID correcto del menú
menu = soup.find("ul", id="menu-micrositio-departamentos-centros")

def recorrer_menu(ul, nivel=0):
    items = ul.find_all("li", recursive=False)
    for item in items:
        link = item.find("a")
        if link:
            texto = link.get_text(strip=True)
            href = link.get("href")
            print("  " * nivel + f"- {texto} -> {href}")
        # Submenús
        sub = item.find("ul", class_="sub-menu")
        if sub:
            recorrer_menu(sub, nivel + 1)

if menu:
    recorrer_menu(menu)
else:
    print("No se encontró el menú.")

# Builtin
import time
import sys

# First Party
import config
from simplelog import log

# Third Party
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

# Configurações do Selenium.
GECKO_DRIVER_PATH = "/usr/bin/geckodriver"  # Caminho do driver no computador.
LOAD_TIME = 10                              # Tempo de carregamento da página, em segundos.
                                            # Use números maiores em conexões mais lentas.

TEST_URL = "https://consultas.anvisa.gov.br/#/documentos/tecnicos/253510002520205/"


def create_webdriver():
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    service = Service(GECKO_DRIVER_PATH)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    return driver


def fetch_webpage(driver, page):
    try:
        driver.get(page)
        time.sleep(LOAD_TIME)
        return driver.page_source
    except Exception as e:
        log(f"Erro ao carregar página: {e}")
        return None


def extract_tag_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    code_list = []
    date_list = []

    expedientes = soup.find_all("label", string="Expediente")
    datas = soup.find_all("label", string="Data do Expediente")

    for expediente in expedientes:
        expediente = expediente.next_siblings

        for info in expediente:
            if info != "\n":
                code_list.append(info.get_text())

    for data in datas:
        data = data.next_siblings

        for info in data:
            if info != "\n":
                date_list.append(info.get_text())

    infos_list = zip(code_list, date_list)

    return infos_list


def main():
    driver = create_webdriver()
    try:
        content = fetch_webpage(driver, TEST_URL)
        if content:
            petitions = extract_tag_content(content)

            for petition in petitions:
                log(f"Expediente: {petition[0]} | Data: {petition[1]}")

        else:
            log("Falha na extração do conteúdo da página.")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
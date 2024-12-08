# Builtin
import time

# First Party
import config
from simplelog import log

# Third Party
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

# Configurações do Selenium.
if config.OS == "win32":
    GECKO_DRIVER_PATH = "honestly i dont know at this point"
else:
    GECKO_DRIVER_PATH = "/usr/bin/geckodriver"
LOAD_TIME = 10
log(f"Running on {config.OS} OS.")

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


def extract_content(html_content, target_info):
    # target_info can be: "Expediente", "Data do Expediente".

    soup = BeautifulSoup(html_content, 'html.parser')

    infos_list = []

    entries = soup.find_all("label", string=target_info)

    for entry in entries:
        entry = entry.next_siblings

        for info in entry:
            if info != "\n":
                infos_list.append(info.get_text())

    return infos_list


def main():
    driver = create_webdriver()
    try:
        content = fetch_webpage(driver, TEST_URL)
        if content:
            record_number = extract_content(content, "Expediente")
            record_date = extract_content(content, "Data do Expediente")

            for petition in zip(record_number, record_date):
                log(f"Expediente: {petition[0]} | Data: {petition[1]}")

        else:
            log("Falha na extração do conteúdo da página.")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
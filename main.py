# Builtin
import time
import os

# First Party
import config
from simplelog import log

# Third Party
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

# Selenium configs.
WEBDRIVER_PATH = "/usr/bin/geckodriver" # Used on my Linux machine for testing.
LOAD_TIME = 10

log(f"Running on {config.OS.title()}.")

def create_webdriver():
    options = Options()
    options.add_argument("--headless")
    if config.OS == "win32":
        driver = webdriver.Edge(options=options)
    else:
        service = Service(WEBDRIVER_PATH)
        driver = webdriver.Firefox(service=service, options=options)
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
    soup = BeautifulSoup(html_content, 'html.parser')
    infos_list = []
    entries = soup.find_all("label", string=target_info)
    for entry in entries:
        entry = entry.next_siblings
        for info in entry:
            if info != "\n":
                infos_list.append(info.get_text())
    return infos_list


def add_to_csv(data, separator=";", filename="data.csv"):
    path = os.path.join(config.dest_path, filename)
    with open(path, "a") as log_file:
        log_file.write(f"{data}{separator}")


def extract_petitions(driver, url):
    content = fetch_webpage(driver, url)
    if content:
        table = []
        headers = [
            "Expediente", "Data do Expediente", "Nº do Protocolo", "Situação atual", "Assunto",
            "Dados da Publicação (RE - Data Resolução - DOU - Data Publicação)"
        ]

        for header in headers:
            log(f"Extraíndo '{header}'")
            extracted_content = extract_content(content, header)
            if not extracted_content:
                log(f"FATAL: Nenhuma informação encontrada.", bail=True)
            table.append(extracted_content)

        extracted_date = extract_content(content, "Data do Processo")
        table[1].insert(0, extracted_date[0])

        for num, header in enumerate(headers):
            table[num].insert(0, header)

        for col in range(len(table[0])):
            log(f"Column: {col + 1}")
            for row in range(len(headers)):
                log(f"Row: {row + 1}")
                info = table[row][col].replace("\n", " ").replace("?", "").strip()
                log(f"Info: {info}")
                sep = "\n" if row == 5 else ";"
                add_to_csv(info, sep)

    else:
        log("FATAL: Falha na extração do conteúdo da página.")


def main():
    driver = create_webdriver()
    mepenox = "https://consultas.anvisa.gov.br/#/documentos/tecnicos/253510002520205/"
    extract_petitions(driver, mepenox)
    driver.quit()


if __name__ == "__main__":
    main()
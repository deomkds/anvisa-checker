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

TEST_URL = "https://consultas.anvisa.gov.br/#/documentos/tecnicos/253510002520205/"

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


def add_to_csv(data, separator=";", filename="data.csv"):
    path = os.path.join(config.dest_path, filename)
    with open(path, "a") as log_file:
        log_file.write(f"{data}{separator}")


def main():
    driver = create_webdriver()
    try:
        content = fetch_webpage(driver, TEST_URL)

        if content:
            headers = [
                "Expediente", "Data do Expediente", "Nº do Protocolo", "Situação atual", "Assunto",
                "Dados da Publicação (RE - Data Resolução - DOU - Data Publicação)"
            ]

            table = []

            for num in range(6):
                extracted_content = extract_content(content, headers[num])
                if not extracted_content:
                    log(f"FATAL: Zero content retrieved from ANVISA's website.", bail=True)
                table.append(extracted_content)

            extracted_date = extract_content(content, "Data do Processo")
            table[1].insert(0, extracted_date[0])

            for num, header in enumerate(headers):
                table[num].insert(0, header)

            for col in range(len(table[0])):
                log(f"Column: {col}")
                for row in range(6):
                    log(f"Row: {row}")
                    info = table[row][col].replace("\n", " ").replace("?", "").strip()
                    log(f"Info: {info}")
                    sep = "\n" if row == 5 else ";"
                    add_to_csv(info, sep)

        else:
            log("Falha na extração do conteúdo da página.")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
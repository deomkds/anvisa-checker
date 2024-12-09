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
LOAD_TIME = 7

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


def load_drugs(file_path):
    with open(file_path) as urls_db:
        lines = urls_db.readlines()
    log(f"Carregados {len(lines)} medicamento(s).")
    return [line.split("|") for line in lines]

def extract_petitions(driver, url, drug_name):
    content = fetch_webpage(driver, url)
    if content:
        table = []
        headers = [
            "Expediente", "Data do Expediente", "Nº do Protocolo", "Situação atual", "Assunto",
            "Dados da Publicação (RE - Data Resolução - DOU - Data Publicação)"
        ]

        for header in headers:
            extracted_content = extract_content(content, header)
            table.append(extracted_content)

        extracted_date = extract_content(content, "Data do Processo")
        table[1].insert(0, extracted_date[0])

        records_amount = len(table[0])
        log(f"Quantidade de expedientes: '{records_amount}'.")
        if records_amount < 1:
            log(f"Nenhuma informação encontrada.")
            return 1

        drug_name_list = [drug_name] * records_amount
        table.insert(0, drug_name_list)
        headers.insert(0, "Medicamento")

        for num, header in enumerate(headers):
            table[num].insert(0, header)

        records_amount = len(table[0])

        for col in range(records_amount):
            for row in range(len(headers)):
                info = table[row][col].replace("\n", " ").replace("?", "").strip()
                sep = "\n" if row == (len(headers) - 1) else ";"
                add_to_csv(info, sep)
                log(f"Column: {col + 1} | Row: {row + 1} | Info: '{info}'")

        return 0

    else:
        log("FATAL: Falha na extração do conteúdo da página.")
        return 2


def main():
    drugs = load_drugs("endereços.txt")
    driver = create_webdriver()

    for drug in drugs:
        drug_name = drug[0].strip()
        process_n = drug[1].replace(".", "").replace("/", "").replace("-", "").strip()
        log(f"Buscando informações do medicamento '{drug_name}' (N.º de Processo: '{process_n}').")
        final_url = f"https://consultas.anvisa.gov.br/#/documentos/tecnicos/{process_n}/"

        returned_value = 1
        while returned_value == 1:
            returned_value = extract_petitions(driver, final_url, drug_name)

    driver.quit()


if __name__ == "__main__":
    main()
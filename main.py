# Builtin
import time
import os
import sys
from pathlib import Path
from datetime import datetime

# Third Party
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

# Selenium configs.
WEBDRIVER_PATH = "/usr/bin/geckodriver" # Used on my Linux machine for testing.
LOAD_TIME = 7
TIME_PROC = 1.5 # Time to account for processing stuff.

OS = sys.platform
DEBUG_MODE = False

home_dir = Path.home()
log_path = os.path.join(home_dir, "Desktop/")

def log(text, essential=False, line_break=False, bail=False, clear=False):
    if DEBUG_MODE or essential:
        if clear:
            os.system("cls") if OS == "win32" else os.system("clear")
        moment_obj = datetime.now()
        moment = moment_obj.strftime("%Y-%m-%d %H:%M:%S")
        path = os.path.join(log_path, 'anvisa-log.txt')
        br = f"\n" if line_break else f""
        output_line = f"{br}{moment}: {text}"
        print(output_line)
        with open(path, "a") as log_file:
            log_file.write(f"{output_line}\n")

        if bail:
            sys.exit()

def create_webdriver():
    options = Options()
    options.add_argument("--headless")
    if OS == "win32":
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
        log(f"Erro ao carregar página: {e}", essential=True)
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

def add_to_csv(data, csv, separator=";"):
    csv.write(f"{data}{separator}")

def open_csv(csv_name="anvisa-data.csv"):
    if os.path.exists(csv_name):
        os.remove(csv_name)
    csv_file = open(csv_name, "w")
    return csv_file

def close_csv(csv_file):
    csv_file.close()

def load_drugs(file_path):
    with open(file_path, "r", encoding="utf-8") as urls_db:
        lines = urls_db.readlines()
    return [line.split("|") for line in lines]

def extract_petitions(driver, url, drug_name, skip_header, csv_file):
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

        records_amount = len(table[0])
        log(f"Quantidade de expedientes: '{records_amount}'.")
        if records_amount < 1:
            log(f"Nenhuma informação encontrada. Tentando novamente...")
            return 1

        extracted_date = extract_content(content, "Data do Processo")
        table[1].insert(0, extracted_date[0])

        info_type_list = ["Processo"] + ["Petição"] * (records_amount - 1)
        table.insert(0, info_type_list)
        headers.insert(0, "Movimento")

        drug_name_list = [drug_name] * records_amount
        table.insert(0, drug_name_list)
        headers.insert(0, "Medicamento")

        for num, header in enumerate(headers):
            table[num].insert(0, header)

        records_amount = len(table[0])

        for col in range(records_amount):
            for row in range(len(headers)):
                if skip_header and col == 0:
                    continue
                info = table[row][col].replace("\n", " ").replace("?", "").strip()
                sep = "\n" if row == (len(headers) - 1) else ";"
                add_to_csv(info, csv_file, sep)

        return 0

    else:
        log("FATAL: Falha na extração do conteúdo da página.", essential=True)
        return 2

def convert_seconds(seconds):
    # Conversion
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    hours = minutes // 60
    remaining_minutes = minutes % 60

    return f"{int(hours):02d}:{int(remaining_minutes):02d}:{int(remaining_seconds):02d}"

def main():
    drugs = load_drugs("protocolos.txt")
    driver = create_webdriver()
    csv = open_csv()

    log(f"Carregados {len(drugs)} medicamento(s).")

    for num, drug in enumerate(drugs):
        drug_name = drug[0].strip()
        process_n = drug[1].replace(".", "").replace("/", "").replace("-", "").strip()
        final_url = f"https://consultas.anvisa.gov.br/#/documentos/tecnicos/{process_n}/"
        skip_header = True if num > 0 else False
        returned_value = 1

        log(f"[{num + 1}/{len(drugs)}] Buscando medicamento '{drug_name}'.", essential=True)
        time_string = convert_seconds((len(drugs) - num) * (LOAD_TIME + TIME_PROC))
        log(f"Tempo restante: {time_string}.", essential=True)

        while returned_value == 1:
            returned_value = extract_petitions(driver, final_url, drug_name, skip_header, csv)

    driver.quit()
    close_csv(csv)


if __name__ == "__main__":
    main()
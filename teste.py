from playwright.sync_api import sync_playwright
import sqlite3
import time
from schedule import repeat, every, run_pending
from datetime import datetime
import json

descarte = ["Sobre a empresa", "Vagas", "Candidatar"]

# @repeat(every().minute)
def scraping():
    conexao = sqlite3.connect("vagas.db")
    banco = conexao.cursor()

    banco.execute("""
        CREATE TABLE IF NOT EXISTS vagas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            link TEXT,
            data TEXT,
            infos TEXT
        )
    """)

    with sync_playwright() as p:

        abrir = p.chromium.launch(headless=False)

        site = abrir.new_page()

        site.goto("https://avivatec.inhire.app/vagas")

        site.wait_for_load_state("networkidle")

        vagas = site.query_selector_all("a[data-component-name='job-position-link']")

        for vaga in vagas:
            titulo = vaga.query_selector("div[data-sentry-element='JobPositionName']").inner_text()
            link = "https://avivatec.inhire.app" + vaga.get_attribute("href")
            data = datetime.now()
            infos = []
            
            siteVaga = abrir.new_page()
            siteVaga.goto(link)
            siteVaga.wait_for_load_state("networkidle")

            lista_infos = siteVaga.query_selector_all("li")

            print("Título:", titulo)
            print("Link:", link)
            print("Data:", data)
            print("Informações:")
            for info in lista_infos:
                print("-", info.inner_text())
                if info.inner_text() not in descarte:
                    infos.append(info.inner_text())

            infos_json = json.dumps(infos)

            banco.execute("""
                INSERT INTO vagas (titulo, link, data, infos)
                VALUES (?, ?, ?, ?)
            """, (titulo, link, data, infos_json))

        abrir.close()
    conexao.commit()
    conexao.close()


scrap = scraping()

# while True:
#     run_pending()
#     time.sleep(5)
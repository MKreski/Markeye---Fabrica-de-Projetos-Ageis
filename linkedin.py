from playwright.sync_api import sync_playwright
import sqlite3
import time
from schedule import repeat, every, run_pending
from datetime import datetime

# descarte = ["Sobre a empresa", "Vagas", "Candidatar"]

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

        pagina = "https://www.linkedin.com/company/brq/"

        site.goto(pagina + "jobs/")

        # site.wait_for_load_state("networkidle")

        site.get_by_role("button", name="Fechar").click()
        site.get_by_role("link", name="Ver todas as vagas").click()

        site.wait_for_load_state("networkidle")

        # site.query_selector("div[class='artdeco-carousel__content']").query_selector("href[class='job-card-square__link']").click()

        vagas = site.query_selector_all("a[data-tracking-control-name='public_jobs_jserp-result_search-card']") #a[class='base-card__full-link']

        for vaga in vagas:
            titulo = vaga.inner_text()
            print(titulo)
            link = vaga.get_attribute("href")
            print(link)
            data = datetime.now()
            
            siteVaga = abrir.new_page()
            siteVaga.goto(link)
            siteVaga.wait_for_load_state("networkidle")
            siteVaga.get_by_role("button", name="Fechar").click()
            siteVaga.query_selector("button[aria-label='Show more']").click()

            lista_infos = siteVaga.locator("div.show-more-less-html__markup") #query_selector_all("div[class='show-more-less-html__markup']")
            infos_text = lista_infos.inner_text()

            print("Título:", titulo)
            print("Link:", link)
            print("Data:", data)
            print("Informações:", infos_text)

            banco.execute("""
                INSERT INTO vagas (titulo, link, data, infos)
                VALUES (?, ?, ?, ?)
            """, (titulo, link, data, infos_text))

        abrir.close()
    conexao.commit()
    conexao.close()


scrap = scraping()

# while True:
#     run_pending()
#     time.sleep(5)
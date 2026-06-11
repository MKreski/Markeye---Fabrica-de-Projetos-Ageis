from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import sqlite3
import time
from schedule import repeat, every, run_pending
from datetime import datetime
import random
import time
# Função para simular o tempo de leitura ou reação de um humano
def pausa_humana(minimo=1.5, maximo=4.5):
    tempo = random.uniform(minimo, maximo)
    time.sleep(tempo)

def scraping(pagina):
    # banco
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

        site.goto(pagina + "jobs/")

        # botao de fechar que aparece
        btn_fechar_inicial = site.get_by_role("button", name="Fechar")
        try:
            btn_fechar_inicial.wait_for(state="visible", timeout=3000)
            pausa_humana()
            btn_fechar_inicial.click()
        except PlaywrightTimeoutError:
            pass # se n aparecer fé
         
        # espera o botao de ver as vaga
        botao_ver_vagas = site.get_by_role("link", name="Ver todas as vagas")
        botao_ver_vagas.wait_for(state="visible")
        pausa_humana()
        botao_ver_vagas.click()

        # espera a lista de vaga
        seletor_vaga = "a[data-tracking-control-name='public_jobs_jserp-result_search-card']"
        # garantindo que a vaga aparece
        site.locator(seletor_vaga).first.wait_for(state="visible") 
        
        # pega as vagas
        vagas = site.locator(seletor_vaga).all()

        for index, vaga in enumerate(vagas):
            if index >= 25: # limita a 25 vagas pra n dar pau de memoria
                break
            
            titulo = vaga.inner_text()
            print(f"\nColetando: {titulo}")
            link = vaga.get_attribute("href")
            data = datetime.now()
            
            pausa_humana(6,15) # pausa maior pq tem que fingir antes de abrir outra vaga
            siteVaga = abrir.new_page()
            siteVaga.goto(link)

            # fecha cartao dentro do site da vaga
            btn_fechar_vaga = siteVaga.get_by_role("button", name="Fechar")
            try:
                btn_fechar_vaga.wait_for(state="visible", timeout=3000)
                pausa_humana()
                btn_fechar_vaga.click()
            except PlaywrightTimeoutError:
                pass

            # mostrar tudo da vaga
            btn_show_more = siteVaga.locator("button[aria-label='Show more']")
            try:
                btn_show_more.wait_for(state="visible", timeout=3000)
                pausa_humana()
                btn_show_more.click()
            except PlaywrightTimeoutError:
                pass 

            # espera div de infos
            lista_infos = siteVaga.locator("div.show-more-less-html__markup")
            lista_infos.wait_for(state="visible")
            infos_text = lista_infos.inner_text()

            print("Link:", link)
            print("Data:", data)
            print("Informações coletadas com sucesso.")
            pausa_humana()

            banco.execute("""
                INSERT INTO vagas (titulo, link, data, infos)
                VALUES (?, ?, ?, ?)
            """, (titulo, link, data, infos_text))

            # fecha a aba pra n dar problema de excesso de memoria
            pausa_humana()
            siteVaga.close()

        abrir.close()
        
    conexao.commit()
    conexao.close()
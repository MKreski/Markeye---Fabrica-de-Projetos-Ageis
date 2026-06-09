from datetime import datetime
import time
from playwright.sync_api import sync_playwright


def cadastrarEmpresa():

    nomeEmpresa = input("Digite o nome da empresa: ")

    print("\nBuscando o LinkedIn da empresa...\n")

    linkedin = None


    with sync_playwright() as busca:

        navengador = busca.chromium.launch(headless=False)

        pagina = navengador.new_page()

        pesquisa = nomeEmpresa + " linkedin"

        pagina.goto("https://www.google.com/")

        time.sleep(3)

        pesquisa_input = pagina.get_by_role("combobox")
        time.sleep(3)
        pesquisa_input.fill(pesquisa)
        time.sleep(1)
        pesquisa_input.press("Enter")
        pagina.wait_for_selector("#search")
        time.sleep(2)
        links = pagina.query_selector_all("a")
        time.sleep(2)
        for i in range(links.count()):
            
            link = links.nth(i).get_attribute("href")

            if link and "linkedin.com/company" in link:
                
                linkedin = link
                break

        navengador.close()


    if linkedin is None:

        print("Não foi possível encontrar automaticamente.")

        linkedin = input("Digite o LinkedIn da empresa: ")


cadastrarEmpresa()






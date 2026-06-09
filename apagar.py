import sqlite3
def scraping():
    conexao = sqlite3.connect("vagas.db")
    banco = conexao.cursor()

    banco.execute("""
        DROP TABLE IF EXISTS vagas
    """)

scrap = scraping()
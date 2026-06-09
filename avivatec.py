from playwright.sync_api import sync_playwright
import sqlite3
from datetime import datetime
import json
from google import genai
import typing_extensions as typing

client = genai.Client(api_key="INSERIR CHAVE")

instruction = """
Você é um especialista em estratégia corporativa e análise de mercado de tecnologia.

Você receberá um JSON contendo vagas de emprego com alterações detectadas entre dois snapshots.
Cada vaga possui:
- "titulo_vaga"
- "adicionados"
- "removidos"

Sua tarefa é analisar apenas mudanças RELEVANTES (ignore alterações superficiais, estéticas ou genéricas).

Você é um especialista em estratégia corporativa e RH técnico.
Você receberá dados de uma vaga de emprego que sofreu alterações.
Sua tarefa é analisar os campos "Adicionados" e "Removidos".

TOM: Executivo, direto e analítico.

ESTRUTURA: Sempre separe em dois blocos: 'Resumo das Alterações' (por vaga) e 'Estratégia Corporativa' (geral)

OBJETIVO:
Resumir, no mínimo de linhas possível, o que mudou nos dados de forma profissional. Caso a tecnologia adicionada pertença a uma stack diferente da removida, destaque a transição de paradigma (ex: de On-premise para Cloud)

Identificar, de forma clara e objetiva, a estratégia da empresa de acordo com os dados recebidos.

IMPORTANTE:
- Não invente informações
- Baseie-se exclusivamente nos dados recebidos
"""

def scraping():

    conexao = sqlite3.connect("vagas.db")
    banco = conexao.cursor()

    banco.execute("""
        CREATE TABLE IF NOT EXISTS vagas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            link TEXT UNIQUE,
            data TEXT
        )
    """)

    banco.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vaga_id INTEGER,
            data_coleta TEXT,
            FOREIGN KEY (vaga_id) REFERENCES vagas(id)
        )
    """)

    banco.execute("""
        CREATE TABLE IF NOT EXISTS infos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id INTEGER,
            texto TEXT,
            FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
        )
    """)

    descarte = ["Sobre a empresa", "Vagas", "Candidatar"]

    vagasAtualizadas = []
    vagasNovas = []
    vagasRemovidas = []

    linksAtuais = set()

    with sync_playwright() as p:

        chrome = p.chromium.launch(headless=False)

        site = chrome.new_page()

        site.goto("https://avivatec.inhire.app/vagas")

        site.wait_for_selector("a[data-component-name='job-position-link']")

        vagas = site.query_selector_all(
            "a[data-component-name='job-position-link']"
        )

        for vaga in vagas:

            titulo = vaga.query_selector(
                "div[data-sentry-element='JobPositionName']"
            ).inner_text()

            link = "https://avivatec.inhire.app" + vaga.get_attribute("href")

            linksAtuais.add(link)

            data = datetime.now().isoformat()

            infos = []

            print(f"\nColetando vaga: {titulo}")

            siteVaga = chrome.new_page()

            try:

                siteVaga.goto(link)

                siteVaga.wait_for_timeout(3000)

                lista_infos = siteVaga.query_selector_all("li")

                for info in lista_infos:

                    texto = " ".join(
                        info.inner_text().split()
                    ).strip()

                    if texto and texto not in descarte:
                        infos.append(texto)

            finally:
                siteVaga.close()

            banco.execute(
                "SELECT id FROM vagas WHERE link = ?",
                (link,)
            )

            resultado = banco.fetchone()

            if resultado:

                vaga_id = resultado[0]

            else:

                banco.execute("""
                    INSERT INTO vagas (titulo, link, data)
                    VALUES (?, ?, ?)
                """, (titulo, link, data))

                vaga_id = banco.lastrowid

                vagasNovas.append({
                    "titulo_vaga": titulo,
                    "adicionados": ["Nova vaga publicada"],
                    "removidos": []
                })

            banco.execute("""
                SELECT id
                FROM snapshots
                WHERE vaga_id = ?
                ORDER BY id DESC
                LIMIT 1
            """, (vaga_id,))

            ultimo = banco.fetchone()

            infos_atuais = set(infos)

            if ultimo:

                ultimo_snapshot = ultimo[0]

                banco.execute("""
                    SELECT texto
                    FROM infos
                    WHERE snapshot_id = ?
                """, (ultimo_snapshot,))

                infos_antigas = set(
                    row[0] for row in banco.fetchall()
                )

                adicionados = list(infos_atuais - infos_antigas)

                removidos = list(infos_antigas - infos_atuais)

                if adicionados or removidos:

                    vagasAtualizadas.append({
                        "titulo_vaga": titulo,
                        "adicionados": adicionados,
                        "removidos": removidos
                    })

                else:
                    print("Sem alterações:", titulo)
                    continue

            banco.execute("""
                INSERT INTO snapshots (vaga_id, data_coleta)
                VALUES (?, ?)
            """, (vaga_id, data))

            snapshot_id = banco.lastrowid

            for texto in infos:

                banco.execute("""
                    INSERT INTO infos (snapshot_id, texto)
                    VALUES (?, ?)
                """, (snapshot_id, texto))

            conexao.commit()

        chrome.close()

    banco.execute("""
        SELECT titulo, link
        FROM vagas
    """)

    vagasBanco = banco.fetchall()

    for tituloBanco, linkBanco in vagasBanco:

        if linkBanco not in linksAtuais:

            vagasRemovidas.append({
                "titulo_vaga": tituloBanco,
                "adicionados": [],
                "removidos": ["Vaga removida do portal"]
            })

    todasAlteracoes = (
        vagasNovas +
        vagasAtualizadas +
        vagasRemovidas
    )

    conexao.close()

    if todasAlteracoes:

        jsonIA = json.dumps(
            todasAlteracoes,
            ensure_ascii=False,
            indent=2
        )

        print(
            f"\nEnviando {len(todasAlteracoes)} alterações para IA..."
        )

        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{instruction}\n\n{jsonIA}"
            )

            print("\n")
            print(response.text)

        except Exception as e:

            print(
                f"Erro ao chamar API Gemini: {e}"
            )

    else:
        print("Não houve alterações.")

scraping()
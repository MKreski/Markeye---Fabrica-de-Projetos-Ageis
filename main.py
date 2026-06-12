import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import linkedin_v2
import sqlite3

class GerenciadorEmpresas:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Avivatec - Gerenciador de Empresas")
        self.janela.geometry("800x500")
        conexao = sqlite3.connect("empresas.db")
        banco = conexao.cursor()
        banco.execute("""
            CREATE TABLE IF NOT EXISTS empresas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                url TEXT
            )
        """)
        self.empresas = banco.execute("SELECT nome, url FROM empresas").fetchall()
        conexao.close()

        self.criarMenu()
        self.criarTela()
        for nome, url in self.empresas:
            self.tabela.insert("", "end", values=(nome, url))

    def criarMenu(self):
        barra_menu = tk.Menu(self.janela)
        menu_arquivo = tk.Menu(barra_menu, tearoff=0)
        menu_arquivo.add_command(label="Sair", command=self.janela.quit)
        barra_menu.add_cascade(label="Arquivo", menu=menu_arquivo)
        self.janela.config(menu=barra_menu)

    def criarTela(self):
        frame_topo = tk.Frame(self.janela)
        frame_topo.pack(pady=10)

        tk.Label(frame_topo, text="Nome da Empresa:").grid(row=0, column=0, padx=5)
        self.entry_nome = tk.Entry(frame_topo, width=40)
        self.entry_nome.grid(row=0, column=1)

        tk.Label(frame_topo, text="URL das Vagas (LinkedIn):").grid(row=1, column=0, padx=5)
        self.entry_linkedin = tk.Entry(frame_topo, width=40)
        self.entry_linkedin.grid(row=1, column=1)

        tk.Button(frame_topo, text="Cadastrar Empresa", command=self.cadastrar_empresa).grid(row=2, column=0, columnspan=2, pady=10)

        self.tabela = ttk.Treeview(self.janela, columns=("Empresa", "URL"), show="headings")
        self.tabela.heading("Empresa", text="Empresa")
        self.tabela.heading("URL", text="URL das Vagas")
        self.tabela.column("Empresa", width=200)
        self.tabela.column("URL", width=500)
        self.tabela.pack(fill="both", expand=True, padx=10, pady=10)

        frame_botoes = tk.Frame(self.janela)
        frame_botoes.pack(pady=10)

        tk.Button(frame_botoes, text="Remover Empresa", command=self.remover_empresa).pack(side="left", padx=5)
        
        self.btn_analise = tk.Button(frame_botoes, text="Executar Análise", command=self.iniciar_analise_thread)
        self.btn_analise.pack(side="left", padx=5)

    def cadastrar_empresa(self):
        nome = self.entry_nome.get().strip()
        url = self.entry_linkedin.get().strip()

        if not nome or not url:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        conexao = sqlite3.connect("empresas.db")
        banco = conexao.cursor()
        banco.execute("""
            CREATE TABLE IF NOT EXISTS empresas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                url TEXT
            )
        """)
        
        banco.execute("INSERT INTO empresas (nome, url) VALUES (?, ?)", (nome, url))
        conexao.commit()
        conexao.close()

        self.tabela.insert("", "end", values=(nome, url))
        
        self.entry_nome.delete(0, tk.END)
        self.entry_linkedin.delete(0, tk.END)

    def remover_empresa(self):
        selecionado = self.tabela.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma empresa.")
            return
        
        conexao = sqlite3.connect("empresas.db")
        banco = conexao.cursor()
        dados = self.tabela.item(selecionado)
        empresa = dados["values"][0]
        banco.execute("DELETE FROM empresas WHERE nome = ?", (empresa,))
        conexao.commit()
        conexao.close() 

        self.tabela.delete(selecionado)

    # --- LÓGICA DE INTEGRAÇÃO COM THREADING ---

    def iniciar_analise_thread(self):
        selecionado = self.tabela.selection()

        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma empresa na tabela primeiro.")
            return

        dados = self.tabela.item(selecionado)
        empresa = dados["values"][0]
        url = dados["values"][1]

        self.btn_analise.config(state=tk.DISABLED, text="Analisando... Aguarde")
        thread = threading.Thread(target=self.processar_scraping, args=(empresa, url))
        thread.start()

    def processar_scraping(self, empresa, url):
        try:
            linkedin_v2.scraping(url)
            print(f"Iniciando scraping no background para: {empresa}")
            
            time.sleep(5) 
            
            resultado = f"Análise concluída com o Gemini para a empresa {empresa}!"
            self.janela.after(0, self.finalizar_analise, resultado)

        except Exception as e:
            self.janela.after(0, self.finalizar_analise, f"Erro na análise: {str(e)}")

    def finalizar_analise(self, mensagem):
        self.btn_analise.config(state=tk.NORMAL, text="Executar Análise")
        messagebox.showinfo("Resultado da Análise IA", mensagem)

if __name__ == "__main__":
    janela = tk.Tk()
    app = GerenciadorEmpresas(janela)
    janela.mainloop()
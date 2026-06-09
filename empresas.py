import sqlite3

matriz_empresas = []

def adicionar_empresa():
    print("\n--- Adicionar Nova Empresa ---")
    nome = input("Nome da empresa: ").strip()
    linkedin = input("Link do LinkedIn: ").strip()
    
    try:
        qtd = int(input("Quantidade (valor inteiro): "))
    except ValueError:
        print("Valor inválido! Usando 1 como padrão.")
        qtd = 1
        
    monitorar_str = input("Monitorar esta empresa? (s/n): ").strip().lower()
    monitorar = True if monitorar_str.lower() == 's' else False
    
    linha_empresa = [nome, linkedin, qtd, monitorar]
    matriz_empresas.append(linha_empresa)
    
    print(f"\nEmpresa '{nome}' adicionada com sucesso na matriz!")

def listar_empresas():
    if not matriz_empresas:
        print("\nA matriz está vazia. Nenhuma empresa cadastrada ainda.")
        return
        
    print("\n--- Empresas na Matriz (Memória) ---")
    for i, empresa in enumerate(matriz_empresas):
        nome, linkedin, qtd, monitorar = empresa
        status_monitoramento = "Sim" if monitorar else "Não"
        print(f"[{i}] Nome: {nome} | LinkedIn: {linkedin} | Qtd: {qtd} | Monitorar: {status_monitoramento}")

def salvar_no_banco():
    if not matriz_empresas:
        print("\nA matriz está vazia. Adicione empresas antes de salvar no banco.")
        return
        
    print("\n--- Salvando no Banco de Dados ---")
    conexao = sqlite3.connect("empresas.db")
    cursor = conexao.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            linkedin TEXT,
            qtd INTEGER,
            monitorar BOOLEAN
        )
    ''')
    
    registros_inseridos = 0
    for empresa in matriz_empresas:
        cursor.execute('''
            INSERT INTO empresas (nome, linkedin, qtd, monitorar)
            VALUES (?, ?, ?, ?)
        ''', (empresa[0], empresa[1], empresa[2], empresa[3]))
        registros_inseridos += 1
        
    conexao.commit()
    conexao.close()
    
    matriz_empresas.clear()
    print(f"{registros_inseridos} registro(s) salvo(s) no banco")
    print("A matriz em memória foi limpa.")

def menu():
    while True:
        print("\n" + "="*30)
        print("SISTEMA DE GESTÃO DE EMPRESAS")
        print("="*30)
        print("1. Adicionar Empresa na Matriz")
        print("2. Listar Empresas na Matriz")
        print("3. Salvar Matriz no SQLite (empresas.db)")
        print("4. Sair do Sistema")
        
        opcao = input("\nEscolha uma opção (1-4): ").strip()
        
        if opcao == '1':
            adicionar_empresa()
        elif opcao == '2':
            listar_empresas()
        elif opcao == '3':
            salvar_no_banco()
        elif opcao == '4':
            print("\nSaindo... Até logo!")
            break
        else:
            print("\nOpção inválida. Tente novamente.")

if __name__ == "__main__":
    menu()
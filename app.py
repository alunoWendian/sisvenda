import sqlite3
from hashlib import sha256

# Variável global para armazenar o usuário logado
usuario_logado = {"username": None, "tipo": None}

def inicializar_bd():
    conn = sqlite3.connect('vendas.db')
    cursor = conn.cursor()
    
    # Tabela de Usuários
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        tipo TEXT)''')
    
    # Tabela de Produtos
    cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        preco REAL NOT NULL,
                        estoque INTEGER NOT NULL)''')
    
    # Criar Admin padrão se não existir
    admin_senha = sha256("admin123".encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO usuarios (username, password, tipo) VALUES (?, ?, ?)", 
                       ('admin', admin_senha, 'admin'))
    except sqlite3.IntegrityError:
        pass
            
    conn.commit()
    conn.close()

# --- DECORADOR DE PERMISSÃO ---
def requer_permissao(tipo_requerido):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if usuario_logado["tipo"] == tipo_requerido:
                return func(*args, **kwargs)
            else:
                print(f"\n[!] ACESSO NEGADO: Apenas usuários '{tipo_requerido}' podem realizar esta ação.")
        return wrapper
    return decorator

# --- FUNÇÕES DE ADMIN ---

@requer_permissao('admin')
def cadastrar_novo_usuario():
    print("\n--- CADASTRO DE NOVO USUÁRIO ---")
    novo_user = input("Nome de usuário: ")
    nova_senha = input("Senha: ")
    tipo = input("Tipo (admin/cliente): ").lower()

    if tipo not in ['admin', 'cliente']:
        print("Erro: Tipo inválido.")
        return

    senha_hash = sha256(nova_senha.encode()).hexdigest()
    try:
        conn = sqlite3.connect('vendas.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (username, password, tipo) VALUES (?, ?, ?)", 
                       (novo_user, senha_hash, tipo))
        conn.commit()
        conn.close()
        print(f"[v] Usuário '{novo_user}' cadastrado!")
    except sqlite3.IntegrityError:
        print("[!] Erro: Usuário já existe.")

@requer_permissao('admin')
def cadastrar_produto():
    print("\n--- CADASTRO DE PRODUTO ---")
    nome = input("Nome do produto: ")
    try:
        preco = float(input("Preço: "))
        estoque = int(input("Quantidade em estoque: "))
        
        conn = sqlite3.connect('vendas.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)", 
                       (nome, preco, estoque))
        conn.commit()
        conn.close()
        print(f"[v] Produto '{nome}' adicionado ao estoque!")
    except ValueError:
        print("[!] Erro: Use números para preço e estoque.")

# --- FUNÇÕES DE CLIENTE ---

def listar_produtos():
    conn = sqlite3.connect('vendas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    
    print("\n--- PRODUTOS DISPONÍVEIS ---")
    if not produtos:
        print("Nenhum produto cadastrado.")
    for p in produtos:
        print(f"ID: {p[0]} | {p[1]} | R$ {p[2]:.2f} | Estoque: {p[3]}")

@requer_permissao('cliente')
def realizar_compra():
    listar_produtos()
    try:
        id_prod = int(input("\nDigite o ID do produto que deseja comprar: "))
        qtd = int(input("Quantidade: "))
        
        conn = sqlite3.connect('vendas.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nome, preco, estoque FROM produtos WHERE id = ?", (id_prod,))
        produto = cursor.fetchone()
        
        if produto and produto[2] >= qtd:
            novo_estoque = produto[2] - qtd
            cursor.execute("UPDATE produtos SET estoque = ? WHERE id = ?", (novo_estoque, id_prod))
            conn.commit()
            print(f"\n[v] Compra de {qtd}x {produto[0]} realizada com sucesso!")
        else:
            print("\n[!] Produto não encontrado ou estoque insuficiente.")
        conn.close()
    except ValueError:
        print("[!] Entrada inválida.")

# --- SISTEMA DE LOGIN ---

def login():
    print("\n" + "="*20 + "\n SISTEMA DE VENDAS \n" + "="*20)
    user = input("Usuário: ")
    senha = input("Senha: ")
    senha_hash = sha256(senha.encode()).hexdigest()

    conn = sqlite3.connect('vendas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT tipo FROM usuarios WHERE username = ? AND password = ?", (user, senha_hash))
    res = cursor.fetchone()
    conn.close()

    if res:
        usuario_logado["username"] = user
        usuario_logado["tipo"] = res[0]
        return True
    return False

# --- MENU PRINCIPAL ---

def main():
    inicializar_bd()
    if login():
        while True:
            print(f"\nSESSÃO: {usuario_logado['username']} ({usuario_logado['tipo'].upper()})")
            
            if usuario_logado["tipo"] == 'admin':
                print("1. Cadastrar Usuário")
                print("2. Cadastrar Produto")
                print("3. Listar Produtos")
                print("4. Sair")
            else:
                print("1. Ver Catálogo")
                print("2. Comprar Produto")
                print("3. Sair")

            opcao = input("\nEscolha: ")

            if usuario_logado["tipo"] == 'admin':
                if opcao == '1': cadastrar_novo_usuario()
                elif opcao == '2': cadastrar_produto()
                elif opcao == '3': listar_produtos()
                elif opcao == '4': break
            else:
                if opcao == '1': listar_produtos()
                elif opcao == '2': realizar_compra()
                elif opcao == '3': break
    else:
        print("\n[!] Login incorreto. Tente novamente.")

if __name__ == "__main__":
    main()
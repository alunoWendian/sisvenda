import sqlite3
from hashlib import sha256
import os

# --- CONFIGURAÇÃO DO BANCO ---
def inicializar_bd():
    conn = sqlite3.connect('vendas.db')
    cursor = conn.cursor()
    # Tabela de usuários
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        tipo TEXT)''')
    
    # Criar admin padrão se não existir
    senha_admin = sha256("admin123".encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO usuarios (username, password, tipo) VALUES (?, ?, ?)", 
                       ('admin', senha_admin, 'admin'))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

# --- LÓGICA DE AUTENTICAÇÃO ---
def login():
    print("\n" + "="*20)
    print("  LOGIN DO SISTEMA")
    print("="*20)
    usuario = input("Usuário: ")
    senha = input("Senha: ")
    senha_hash = sha256(senha.encode()).hexdigest()

    conn = sqlite3.connect('vendas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT tipo FROM usuarios WHERE username = ? AND password = ?", (usuario, senha_hash))
    res = cursor.fetchone()
    conn.close()

    if res:
        return usuario, res[0]
    return None, None

# --- MENUS ---
def menu_admin(user):
    while True:
        print(f"\n--- PAINEL ADMIN (Logado como: {user}) ---")
        print("1. Cadastrar Produto")
        print("2. Ver Relatório de Vendas")
        print("3. Sair")
        opcao = input("Escolha: ")
        
        if opcao == '1':
            print(">> Funcionalidade: Cadastro de produto (SQL INSERT)")
        elif opcao == '2':
            print(">> Funcionalidade: Select em vendas")
        elif opcao == '3':
            break

def menu_cliente(user):
    while True:
        print(f"\n--- ÁREA DO CLIENTE (Olá, {user}!) ---")
        print("1. Ver Catálogo")
        print("2. Comprar Produto")
        print("3. Meus Pedidos")
        print("4. Sair")
        opcao = input("Escolha: ")
        
        if opcao == '4':
            break
        else:
            print(f">> Você escolheu a opção {opcao}")

# --- FLUXO PRINCIPAL ---
def main():
    inicializar_bd()
    
    while True:
        user, tipo = login()
        
        if user:
            print(f"\nLogin realizado com sucesso! Nível: {tipo.upper()}")
            if tipo == 'admin':
                menu_admin(user)
            else:
                menu_cliente(user)
        else:
            print("\n[!] Erro: Usuário ou senha incorretos.")
            cont = input("Tentar novamente? (s/n): ")
            if cont.lower() != 's':
                break

if __name__ == "__main__":
    main()
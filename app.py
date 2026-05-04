from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'loja_secreta_123' # Chave para manter o carrinho ativo

def get_db_connection():
    conn = sqlite3.connect('loja_virtual.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS produtos 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     nome TEXT NOT NULL, 
                     preco REAL NOT NULL)''')
    conn.commit()
    conn.close()

# --- ROTAS DO CLIENTE (VITRINE) ---
@app.route('/')
def vitrine():
    conn = get_db_connection()
    produtos = conn.execute('SELECT * FROM produtos').fetchall()
    conn.close()
    return render_template('loja.html', produtos=produtos)

@app.route('/adicionar_carrinho/<int:id>')
def adicionar_carrinho(id):
    if 'carrinho' not in session:
        session['carrinho'] = []
    
    carrinho = session['carrinho']
    carrinho.append(id)
    session['carrinho'] = carrinho
    return redirect(url_for('vitrine'))

@app.route('/carrinho')
def ver_carrinho():
    carrinho_ids = session.get('carrinho', [])
    conn = get_db_connection()
    itens = []
    total = 0
    for pid in carrinho_ids:
        item = conn.execute('SELECT * FROM produtos WHERE id = ?', (pid,)).fetchone()
        if item:
            itens.append(item)
            total += item['preco']
    conn.close()
    return render_template('carrinho.html', itens=itens, total=total)

# --- ROTAS DO ADMINISTRADOR (CADASTRO) ---
@app.route('/admin')
def admin():
    conn = get_db_connection()
    produtos = conn.execute('SELECT * FROM produtos').fetchall()
    conn.close()
    return render_template('admin.html', produtos=produtos)

@app.route('/admin/add', methods=['POST'])
def admin_add():
    nome = request.form['nome']
    preco = request.form['preco']
    conn = get_db_connection()
    conn.execute('INSERT INTO produtos (nome, preco) VALUES (?, ?)', (nome, preco))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/limpar')
def limpar():
    session.pop('carrinho', None)
    return redirect(url_for('vitrine'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
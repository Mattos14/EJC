from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'minha_chave_secreta'  # Necessária para manter sessões (login)

# Função para conectar ao banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect('database.db')  # Arquivo do banco
    conn.row_factory = sqlite3.Row        # Permite acessar colunas pelo nome
    return conn

# Rota da tela de login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        senha = request.form['senha']

        # Verifica se a senha está correta (fixa aqui, mas poderia vir de um banco)
        if senha == 'EJC2025':
            session['logado'] = True  # Cria a sessão
            return redirect('/dashboard')
        else:
            return 'Senha incorreta. Tente novamente.'

    return render_template('login.html')


# Rota principal após login - Menu com opções
@app.route('/dashboard')
def dashboard():
    if not session.get('logado'):
        return redirect('/')
    
    return render_template('dashboard.html')


# Rota para adicionar nova pessoa
@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    if not session.get('logado'):
        return redirect('/')

    if request.method == 'POST':
        nome = request.form['nome']
        equipe = request.form['equipe']
        celular = request.form['celular']

        # Insere no banco de dados
        conn = get_db_connection()
        conn.execute('INSERT INTO pessoas (nome, equipe, celular) VALUES (?, ?, ?)',
                     (nome, equipe, celular))
        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template('adicionar.html')


# Rota para buscar pessoas por nome ou equipe
@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    if not session.get('logado'):
        return redirect('/')

    resultados = None

    if request.method == 'POST':
        nome = request.form['nome']
        equipe = request.form['equipe']

        conn = get_db_connection()
        query = 'SELECT * FROM pessoas WHERE 1=1'  # Condição inicial para montar a busca
        params = []

        # Adiciona condição se o nome for preenchido
        if nome:
            query += ' AND nome LIKE ?'
            params.append(f'%{nome}%')
        
        # Adiciona condição se a equipe for preenchida
        if equipe:
            query += ' AND equipe LIKE ?'
            params.append(f'%{equipe}%')

        resultados = conn.execute(query, params).fetchall()
        conn.close()

    return render_template('buscar.html', resultados=resultados)


# Rota para deletar pessoa por ID
@app.route('/delete/<int:id>')
def delete(id):
    if not session.get('logado'):
        return redirect('/')

    conn = get_db_connection()
    conn.execute('DELETE FROM pessoas WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return redirect('/buscar')


# Rota para logout (encerrar sessão)
@app.route('/logout')
def logout():
    session.clear()  # Remove todos os dados da sessão
    return redirect('/')


# Executa o servidor Flask localmente
if __name__ == '__main__':
    app.run(debug=True)

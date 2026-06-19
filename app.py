from flask import Flask, render_template, request, redirect, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = 'fa48d13a972b85006eb37bc06e03f68f9f64159b44f22f2156bb9e1ac36a5980'

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

def inicializar_banco():
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                usuario VARCHAR(50) UNIQUE NOT NULL,
                senha VARCHAR(50) NOT NULL,
                perfil VARCHAR(20) DEFAULT 'leitura'
            );
        """)
        cursor.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS perfil VARCHAR(20) DEFAULT 'leitura';")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS abonadas (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                data_abonada DATE,
                setor VARCHAR(50),
                trimestre VARCHAR(50)
            );
        """)
        cursor.execute("ALTER TABLE abonadas ADD COLUMN IF NOT EXISTS nome VARCHAR(100);")
        cursor.execute("ALTER TABLE abonadas ADD COLUMN IF NOT EXISTS data_abonada DATE;")
        cursor.execute("ALTER TABLE abonadas ADD COLUMN IF NOT EXISTS setor VARCHAR(50);")
        cursor.execute("ALTER TABLE abonadas ADD COLUMN IF NOT EXISTS trimestre VARCHAR(50);")
        
        cursor.execute("""
            INSERT INTO usuarios (usuario, senha, perfil) VALUES ('recepcao', '123456vT@', 'admin')
            ON CONFLICT (usuario) DO UPDATE SET perfil = 'admin', senha = '123456vT@';
        """)
        cursor.execute("""
            INSERT INTO usuarios (usuario, senha, perfil) VALUES ('dgi', '2026', 'leitura')
            ON CONFLICT (usuario) DO UPDATE SET perfil = 'leitura', senha = '2026';
        """)
        cursor.execute("""
            INSERT INTO usuarios (usuario, senha, perfil) VALUES ('rh', '2026', 'leitura')
            ON CONFLICT (usuario) DO UPDATE SET perfil = 'leitura', senha = '2026';
        """)
        
        conn.commit()
        cursor.close()
        print("⚡ Banco de dados verificado e updated!")
    except Exception as e:
        print("Erro ao inicializar o banco:", e)
        conn.rollback()

inicializar_banco()

@app.after_request
def limpar_transacoes_presas(response):
    try:
        conn.rollback()
    except:
        pass
    return response

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario_digitado = request.form.get('usuario')
        senha_digitada = request.form.get('senha')

        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario, senha, perfil FROM usuarios WHERE usuario = %s", (usuario_digitado,))
        user = cursor.fetchone()
        cursor.close()

        if user and user[2] == senha_digitada:
            session['usuario'] = user[1] 
            session['perfil'] = user[3]  
            return redirect('/dashboard')
        else:
            return """
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Erro de Login</title>
                <style>
                    body{ margin:0; height:100vh; display:flex; justify-content:center; align-items:center; background:#f4f6f9; font-family:Arial,sans-serif; }
                    .card{ background:white; width:450px; padding:40px; border-radius:15px; text-align:center; box-shadow:0 0 20px rgba(0,0,0,0.15); }
                    .icone{ font-size:70px; color:#ef4444; }
                    h2{ color:#1e3a8a; margin-top:15px; }
                    p{ color:#64748b; font-size:16px; margin-top:10px; }
                    .botao{ display:inline-block; background:#2563eb; color:white; text-decoration:none; padding:12px 25px; border-radius:8px; margin-top:20px; }
                </style>
            </head>
            <body>
                <div class="card">
                    <div class="icone">❌</div>
                    <h2>Falha no Login</h2>
                    <p>Usuário ou senha incorretos!</p>
                    <br>
                    <a class="botao" href="/login">Tentar Novamente</a>
                </div>
            </body>
            </html>
            """
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

@app.route('/cadastro', methods=['GET', 'POST']) 
def cadastro():
    if 'usuario' not in session:
        return redirect('/login')
    
    if session.get('perfil') != 'admin':
        return """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Acesso Negado</title>
            <style>
                body{ margin:0; height:100vh; display:flex; justify-content:center; align-items:center; background:#f4f6f9; font-family:Arial,sans-serif; }
                .card{ background:white; width:450px; padding:40px; border-radius:15px; text-align:center; box-shadow:0 0 20px rgba(0,0,0,0.15); }
                .icone{ font-size:70px; color:#ef4444; }
                h2{ color:#1e3a8a; margin-top:15px; }
                p{ color:#64748b; font-size:16px; margin-top:10px; }
                .botao{ display:inline-block; background:#2563eb; color:white; text-decoration:none; padding:12px 25px; border-radius:8px; margin-top:20px; }
            </style>
        </head>
        <body>
            <div class="card">
                <div class="icone">❌</div>
                <h2>Acesso Negado</h2>
                <p>Seu perfil não possui permissão para cadastrar abonadas.</p>
                <br>
                <a class="botao" href="/dashboard">Voltar ao Painel</a>
            </div>
        </body>
        </html>
        """, 403

    if request.method == 'POST':
        try:
            nome = request.form['nome']
            data_abonada = request.form['data_abonada']
            setor = request.form['setor']
            trimestre = request.form['trimestre']

            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO abonadas (nome, data_abonada, setor, trimestre)
                VALUES (%s, %s, %s, %s)
                """,
                (nome, data_abonada, setor, trimestre)
            )
            conn.commit()
            cursor.close()

            return """
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Sucesso</title>
                <style>
                    body{ margin:0; height:100vh; display:flex; justify-content:center; align-items:center; background:#f4f6f9; font-family:Arial,sans-serif; }
                    .card{ background:white; width:450px; padding:40px; border-radius:15px; text-align:center; box-shadow:0 0 20px rgba(0,0,0,0.15); }
                    .icone{ font-size:70px; color:#22c55e; }
                    h2{ color:#1e3a8a; margin-top:15px; }
                    .botao{ display:inline-block; background:#2563eb; color:white; text-decoration:none; padding:12px 25px; border-radius:8px; }
                </style>
            </head>
            <body>
                <div class="card">
                    <div class="icone">✓</div>
                    <h2>Registro salvo com sucesso!</h2>
                    <br>
                    <a class="botao" href="/cadastro">Cadastrar Outra</a>
                </div>
            </body>
            </html>
            """
        except Exception as erro:
            conn.rollback()
            return f"<h2>ERRO NO CADASTRO</h2><p>{erro}</p>"

    return render_template('cadastro.html')

@app.route('/consulta', methods=['GET', 'POST'])
def consulta():
    if 'usuario' not in session:
        return redirect('/login')

    resultados = []
    if request.method == 'POST':
        pesquisa = request.form['pesquisa']

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT *
            FROM abonadas
            WHERE nome ILIKE %s
            OR setor ILIKE %s
            OR CAST(data_abonada AS TEXT) ILIKE %s
            ORDER BY id DESC
            """,
            (f'%{pesquisa}%', f'%{pesquisa}%', f'%{pesquisa}%')
        )
        resultados = cursor.fetchall()
        cursor.close()

    return render_template('consulta.html', resultados=resultados)

@app.route('/relatorio')
def relatorio():
    if 'usuario' not in session:
        return redirect('/login')

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT trimestre, COUNT(*)
        FROM abonadas
        GROUP BY trimestre
        ORDER BY trimestre
        """
    )
    dados = cursor.fetchall()
    cursor.close()

    return render_template('relatorio.html', dados=dados)

@app.route('/sair')
def sair():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
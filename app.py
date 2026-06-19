from flask import Flask, render_template, request, redirect, session
import psycopg2

app = Flask(__name__)
app.secret_key = 'fa48d13a972b85006eb37bc06e03f68f9f64159b44f22f2156bb9e1ac36a5980'
import os
import psycopg2

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = conn.cursor()

from flask import redirect 

@app.route('/')
def home():
   
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 1. Pega os dados que o usuário digitou na tela de login
        usuario_digitado = request.form.get('usuario')
        senha_digitada = request.form.get('senha')

        cursor = conn.cursor()
        
        cursor.execute("SELECT id, usuario, senha, perfil FROM usuarios WHERE usuario = %s", (usuario_digitado,))
        user = cursor.fetchone()
        cursor.close()

        if user and user[2] == senha_digitada:
            # 4. Se deu certo, salvamos os dados dele na "memória" do navegador (Session)
            session['usuario'] = user[1] # Salva o nome (recepcao, dgi ou rh)
            session['perfil'] = user[3]  # Salva o perfil (admin ou leitura)
            
            return redirect('/dashboard')
        else:
           
            return "❌ Usuário ou senha incorretos! Volte e tente novamente."

    
    return render_template('login.html')




@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')



@app.route('/cadastro', methods=['GET', 'POST']) 
def cadastro():
  
    if 'usuario' not in session:
        return redirect('/login')
    
    
    if session.get('perfil') != 'admin':
        return "❌ Acesso Negado: Seu perfil não tem permissão para cadastrar abonadas.", 403

  
    if request.method == 'POST':
        
        pass

        try:

            nome = request.form['nome']
            data_abonada = request.form['data_abonada']
            setor = request.form['setor']
            trimestre = request.form['trimestre']

            cursor.execute(
                """
                INSERT INTO abonadas
                (
                    nome,
                    data_abonada,
                    setor,
                    trimestre
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    nome,
                    data_abonada,
                    setor,
                    trimestre
                )
            )

            conn.commit()

            return """
<!DOCTYPE html>
<html lang="pt-BR">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Sucesso</title>

<style>

body{
    margin:0;
    height:100vh;
    display:flex;
    justify-content:center;
    align-items:center;
    background:#f4f6f9;
    font-family:Arial,sans-serif;
}

.card{
    background:white;
    width:450px;
    padding:40px;
    border-radius:15px;
    text-align:center;
    box-shadow:0 0 20px rgba(0,0,0,0.15);
}

.icone{
    font-size:70px;
    color:#22c55e;
}

h2{
    color:#1e3a8a;
    margin-top:15px;
}

.botao{
    display:inline-block;
    background:#2563eb;
    color:white;
    text-decoration:none;
    padding:12px 25px;
    border-radius:8px;
}

</style>

</head>

<body>

<div class="card">

<div class="icone">✓</div>

<h2>Registro salvo com sucesso!</h2>

<br>

<a class="botao" href="/cadastro">
Cadastrar Outra
</a>

</div>

</body>

</html>
"""

        except Exception as erro:

            conn.rollback()

            return f"""
            <h2>ERRO</h2>
            <p>{erro}</p>
            """

    return render_template('cadastro.html')


@app.route('/consulta', methods=['GET', 'POST'])
def consulta():

    resultados = []

    if request.method == 'POST':

        pesquisa = request.form['pesquisa']

        cursor.execute(
            """
            SELECT *
            FROM abonadas
            WHERE nome ILIKE %s
            OR setor ILIKE %s
            OR CAST(data_abonada AS TEXT) ILIKE %s
            ORDER BY id DESC
            """,
            (
                f'%{pesquisa}%',
                f'%{pesquisa}%',
                f'%{pesquisa}%'
            )
        )

        resultados = cursor.fetchall()

    return render_template(
        'consulta.html',
        resultados=resultados
    )


@app.route('/relatorio')
def relatorio():

    cursor.execute(
        """
        SELECT
            trimestre,
            COUNT(*)
        FROM abonadas
        GROUP BY trimestre
        ORDER BY trimestre
        """
    )

    dados = cursor.fetchall()

    return render_template(
        'relatorio.html',
        dados=dados
    )



@app.route('/sair')
def sair():
    return redirect('/')

if __name__ == '__main__':
       app.run(debug=True)
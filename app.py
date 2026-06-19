from flask import Flask, render_template, request, redirect
import psycopg2

app = Flask(__name__)

conn = psycopg2.connect(
    host="localhost",
    database="controle_abonadas",
    user="recepcao",
    password="1234"
)

cursor = conn.cursor()


# LOGIN

@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        usuario = request.form['usuario']
        senha = request.form['senha']

        cursor.execute(
            """
            SELECT *
            FROM usuarios
            WHERE usuario = %s
            AND senha = %s
            """,
            (usuario, senha)
        )

        resultado = cursor.fetchone()

        if resultado:
            return redirect('/dashboard')

        return """
        <h2>Usuário ou senha inválidos</h2>
        <br>
        <a href="/">Voltar</a>
        """

    return render_template('login.html')


# DASHBOARD

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# CADASTRO

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():

    if request.method == 'POST':

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


# CONSULTA

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


# RELATÓRIO

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


# SAIR

@app.route('/sair')
def sair():
    return redirect('/')


app.run(debug=True)
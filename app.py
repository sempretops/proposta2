from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from weasyprint import HTML
import io
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------------------------------------------
# 1. Definimos o modelo da proposta
# ------------------------------------------------------
class Proposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), unique=True, nullable=False)
    date = db.Column(db.String(20), nullable=False)
    validity = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    product = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

# ------------------------------------------------------
# 2. Criamos as tabelas ao carregar a aplicação
# ------------------------------------------------------
with app.app_context():
    db.create_all()

# ------------------------------------------------------
# 3. Rotas relacionadas ao CRUD de Proposals
# ------------------------------------------------------
@app.route('/')
def index():
    """Lista as propostas salvas no banco."""
    proposals = Proposal.query.all()
    return render_template('index.html', proposals=proposals)

@app.route('/add', methods=['GET', 'POST'])
def add_proposal():
    if request.method == 'POST':
        number = request.form['number']
        date = request.form['date']
        validity = request.form['validity']
        company_name = request.form['company_name']
        contact = request.form['contact']
        product = request.form['product']
        quantity = int(request.form['quantity'])
        unit_price = float(request.form['unit_price'])
        total_price = quantity * unit_price

        new_proposal = Proposal(
            number=number,
            date=date,
            validity=validity,
            company_name=company_name,
            contact=contact,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price
        )
        db.session.add(new_proposal)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('form.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_proposal(id):
    proposal = Proposal.query.get(id)
    if request.method == 'POST':
        proposal.number = request.form['number']
        proposal.date = request.form['date']
        proposal.validity = request.form['validity']
        proposal.company_name = request.form['company_name']
        proposal.contact = request.form['contact']
        proposal.product = request.form['product']
        proposal.quantity = int(request.form['quantity'])
        proposal.unit_price = float(request.form['unit_price'])
        proposal.total_price = proposal.quantity * proposal.unit_price

        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('form.html', proposal=proposal)

@app.route('/delete/<int:id>')
def delete_proposal(id):
    proposal = Proposal.query.get(id)
    db.session.delete(proposal)
    db.session.commit()
    return redirect(url_for('index'))

# ------------------------------------------------------
# 4. Rota para gerar PDF a partir de dados de um formulário
#    (sem salvar no banco, apenas gerando PDF na hora)
# ------------------------------------------------------
@app.route('/gerar_pdf', methods=['POST'])
def gerar_pdf():
    # Captura dados do formulário
    empresa = request.form['empresa']
    cnpj = request.form['cnpj']
    ie = request.form['ie']
    nome_contato = request.form['nome_contato']
    email = request.form['email']
    telefone = request.form['telefone']
    descricao = request.form['descricao']
    quantidade = request.form['quantidade']
    unidade = request.form['unidade']
    valor_unitario = request.form['valor_unitario']
    valor_total = request.form['valor_total']
    request.form['periodo']
    request.form.get('periodo_personalizado')
    request.form.getlist('equipamento[]')
    request.form.getlist('quantidade[]')
    request.form.getlist('valor_unitario[]')
    request.form.getlist('valor_total_linha[]')
    request.form['valor_total_geral']

    # Data de hoje e data de validade (7 dias depois)
    data_hoje = datetime.now().strftime('%d/%m/%Y')
    data_validade = (datetime.now() + timedelta(days=7)).strftime('%d/%m/%Y')

    # Render template HTML
    html_str = render_template(
        'pdf_template.html',
        # Dados do formulário
        empresa=empresa,
        cnpj=cnpj,
        ie=ie,
        nome_contato=nome_contato,
        email=email,
        telefone=telefone,
        descricao=descricao,
        quantidade=quantidade,
        unidade=unidade,
        valor_unitario=valor_unitario,
        valor_total=valor_total,

        # Dados fixos e calculados
        data_hoje=data_hoje,
        data_validade=data_validade
    )

    # Gerar PDF
    pdf_file = HTML(string=html_str).write_pdf()

    return send_file(
        io.BytesIO(pdf_file),
        as_attachment=True,
        download_name='proposta.pdf',
        mimetype='application/pdf'
    )

# ------------------------------------------------------
# 5. Executa a aplicação localmente
# ------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)

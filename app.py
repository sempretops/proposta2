from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo da proposta
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

@app.route('/')
def index():
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
            number=number, date=date, validity=validity, company_name=company_name,
            contact=contact, product=product, quantity=quantity,
            unit_price=unit_price, total_price=total_price
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

if __name__ == '__main__':
    if not os.path.exists("database.db"):
        db.create_all()
    app.run(debug=True)

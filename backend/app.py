from flask import Flask, jsonify, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# 🔗 Configuration de la base PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/ticketsdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 🎫 Modèle Ticket
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priorite = db.Column(db.String(20), nullable=True)
    statut = db.Column(db.String(20), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    id_employe = db.Column(db.Integer, nullable=True)
    id_technicien = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "titre": self.titre,
            "description": self.description,
            "priorite": self.priorite,
            "statut": self.statut,
            "date_creation": self.date_creation.isoformat(),
            "id_employe": self.id_employe,
            "id_technicien": self.id_technicien
        }

# 🏠 Route d'accueil simple
@app.route('/')
def home():
    return "Bienvenue Maïssa 🧡 API Flask + PostgreSQL"

# 🔁 Route JSON : GET tous les tickets
@app.route('/tickets', methods=['GET'])
def get_tickets():
    tickets = Ticket.query.all()
    return jsonify([ticket.to_dict() for ticket in tickets])

# 🌐 Formulaire HTML (affichage)
@app.route('/formulaire', methods=['GET'])
def afficher_formulaire():
    tickets = Ticket.query.all()
    return render_template('index.html', tickets=tickets)

# 🌐 Formulaire HTML (soumission)
@app.route('/tickets', methods=['POST'])
def formulaire_ticket():
    titre = request.form.get('titre')
    description = request.form.get('description')
    priorite = request.form.get('priorite')
    statut = request.form.get('statut')
    id_employe = request.form.get('id_employe')
    id_technicien = request.form.get('id_technicien')

    nouveau_ticket = Ticket(
        titre=titre,
        description=description,
        priorite=priorite,
        statut=statut,
        id_employe=id_employe,
        id_technicien=id_technicien
    )
    db.session.add(nouveau_ticket)
    db.session.commit()

    return redirect('/formulaire')

@app.route('/delete/<int:ticket_id>', methods=['POST'])
def supprimer_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if ticket:
        db.session.delete(ticket)
        db.session.commit()
    return redirect('/dashboard')


# 📊 Dashboard avec filtres
@app.route('/dashboard')
def dashboard():
    statut = request.args.get('statut')
    priorite = request.args.get('priorite')

    query = Ticket.query
    if statut:
        query = query.filter_by(statut=statut)
    if priorite:
        query = query.filter_by(priorite=priorite)

    tickets = query.all()
    return render_template('dashboard.html', tickets=tickets)

# 📈 Statistiques
@app.route('/stats')
def stats():
    from collections import Counter
    tickets = Ticket.query.all()
    statuts = Counter([ticket.statut for ticket in tickets])
    priorites = Counter([ticket.priorite for ticket in tickets if ticket.priorite])

    return render_template('stats.html',
        data_statut=statuts,
        data_priorite=priorites
    )

import csv
from io import StringIO
from flask import Response

@app.route('/export')
def export_csv():
    tickets = Ticket.query.all()

    # Création CSV en mémoire
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Titre', 'Description', 'Priorité', 'Statut', 'Date création', 'Employé', 'Technicien'])

    for ticket in tickets:
        writer.writerow([
            ticket.id,
            ticket.titre,
            ticket.description,
            ticket.priorite,
            ticket.statut,
            ticket.date_creation.strftime("%Y-%m-%d %H:%M:%S"),
            ticket.id_employe,
            ticket.id_technicien
        ])

    output.seek(0)

    return Response(output, mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=tickets.csv"})


# 🚀 Lancement
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

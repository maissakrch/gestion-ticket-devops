from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# 🔗 Configuration de la base PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/ticketsdb'
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

# 🏠 Route d'accueil
@app.route('/')
def home():
    return "Bienvenue Maïssa 🧡 API Flask + PostgreSQL"

# 🔁 Route GET et POST pour /tickets
@app.route('/tickets', methods=['GET', 'POST'])
def tickets():
    if request.method == 'GET':
        tickets = Ticket.query.all()
        return jsonify([ticket.to_dict() for ticket in tickets])

    elif request.method == 'POST':
        data = request.get_json()
        titre = data.get('titre')
        description = data.get('description')
        priorite = data.get('priorite')
        statut = data.get('statut')
        id_employe = data.get('id_employe')
        id_technicien = data.get('id_technicien')

        if not titre or not statut:
            return jsonify({"error": "Champs manquants"}), 400

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

        return jsonify(nouveau_ticket.to_dict()), 201

# 🚀 Lancement de l'app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

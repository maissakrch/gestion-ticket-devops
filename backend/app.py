from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 🔗 Configuration de la base PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/ticketsdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 🎫 Modèle Ticket
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False)
    statut = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "titre": self.titre,
            "statut": self.statut
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
        statut = data.get('statut')

        if not titre or not statut:
            return jsonify({"error": "Champs manquants"}), 400

        nouveau_ticket = Ticket(titre=titre, statut=statut)
        db.session.add(nouveau_ticket)
        db.session.commit()

        return jsonify(nouveau_ticket.to_dict()), 201

# 🚀 Lancement de l'app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

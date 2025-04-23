from flask import Flask, jsonify, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Clé secrète pour les sessions

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

# 🔐 Décorateur pour protéger les pages
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

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

# 📊 Dashboard avec filtres (protégé)
@app.route('/dashboard')
@login_required
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

# 📈 Statistiques (protégé)
@app.route('/stats')
@login_required
def stats():
    from collections import Counter
    tickets = Ticket.query.all()
    statuts = Counter([ticket.statut for ticket in tickets])
    priorites = Counter([ticket.priorite for ticket in tickets if ticket.priorite])

    return render_template('stats.html',
        data_statut=statuts,
        data_priorite=priorites
    )

# 🔐 Page de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            return redirect('/dashboard')
        else:
            return "Identifiants invalides", 401

    return render_template('login.html')

# 🔐 Déconnexion
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

# 🚀 Lancement
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

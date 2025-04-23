from flask import Flask, jsonify, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Clé secrète pour les sessions

# 🔗 Configuration de la base PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/ticketsdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 🔐 Gestion de session avec Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # redirige vers /login si l’utilisateur n’est pas connecté

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Utilisateur(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin' ou 'user'

    def set_password(self, mot_de_passe_clair):
        self.mot_de_passe = generate_password_hash(mot_de_passe_clair)

    def check_password(self, mot_de_passe_clair):
        return check_password_hash(self.mot_de_passe, mot_de_passe_clair)

@login_manager.user_loader
def load_user(user_id):
    return Utilisateur.query.get(int(user_id))

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
        email = request.form.get('email')
        mot_de_passe = request.form.get('mot_de_passe')
        user = Utilisateur.query.filter_by(email=email).first()

        if user and user.check_password(mot_de_passe):
            login_user(user)
            print("✅ Connexion réussie")
            return redirect('/dashboard')

        print("❌ Identifiants invalides")
        return "Identifiants invalides"
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']
        mot_de_passe = request.form['mot_de_passe']
        role = request.form['role']

        if Utilisateur.query.filter_by(email=email).first():
            return "Cet email est déjà utilisé."

        nouvel_utilisateur = Utilisateur(nom=nom, email=email, role=role)
        nouvel_utilisateur.set_password(mot_de_passe)

        db.session.add(nouvel_utilisateur)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')

@app.route('/admin/users')
@login_required
def gestion_utilisateurs():
    if current_user.role != 'admin':
        return "Accès refusé", 403

    utilisateurs = Utilisateur.query.all()
    return render_template('admin_users.html', utilisateurs=utilisateurs)

@app.route('/admin/users/delete/<int:id>', methods=['POST'])
@login_required
def supprimer_utilisateur(id):
    if current_user.role != 'admin':
        return "Accès refusé", 403

    user = Utilisateur.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect('/admin/users')

@app.route('/admin/users/add', methods=['POST'])
@login_required
def ajouter_utilisateur():
    if current_user.role != 'admin':
        return "Accès refusé", 403

    nom = request.form['nom']
    email = request.form['email']
    mot_de_passe = request.form['mot_de_passe']
    role = request.form['role']

    if Utilisateur.query.filter_by(email=email).first():
        return "Email déjà utilisé."

    nouvel_user = Utilisateur(nom=nom, email=email, role=role)
    nouvel_user.set_password(mot_de_passe)
    db.session.add(nouvel_user)
    db.session.commit()

    return redirect('/admin/users')


# 🚀 Lancement
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

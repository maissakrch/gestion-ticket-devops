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
    role = db.Column(db.String(20), nullable=False)  # admin, user, technicien

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
@app.route('/formulaire')
@login_required
def afficher_formulaire():
    utilisateurs = Utilisateur.query.all()
    tickets = Ticket.query.all()
    return render_template('index.html', tickets=tickets, utilisateurs=utilisateurs)


# 🌐 Formulaire HTML (soumission)
from random import choice
import random


@app.route('/tickets', methods=['POST'])
def formulaire_ticket():
    titre = request.form.get('titre')
    description = request.form.get('description')
    priorite = request.form.get('priorite')

    # ID de l'employé automatiquement : l'utilisateur connecté
    id_employe = current_user.id

    # Technicien aléatoire
    techniciens = Utilisateur.query.filter_by(role="technicien").all()
    id_technicien = random.choice(techniciens).id if techniciens else None

    # Statut par défaut = "ouvert"
    nouveau_ticket = Ticket(
        titre=titre,
        description=description,
        priorite=priorite,
        statut="ouvert",
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

    # 👑 Admin : voit tout
    if current_user.role == 'admin':
        query = Ticket.query
    # 👤 Utilisateur simple : voit ses propres tickets
    elif current_user.role == 'user':
        query = Ticket.query.filter_by(id_employe=current_user.id)
    # 🛠 Technicien : voit ses tickets dans une autre route dédiée
    else:
        return redirect('/technicien/tickets')

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
    from collections import Counter, defaultdict
    from datetime import datetime

    tickets = Ticket.query.all()

    # Nombre de tickets par statut
    statuts = Counter(ticket.statut for ticket in tickets)

    # Nombre de tickets critiques
    priorites = Counter(ticket.priorite for ticket in tickets if ticket.priorite)

    # Temps moyen de résolution par technicien
    technicien_durations = defaultdict(list)
    for ticket in tickets:
        if ticket.statut == "fermé" and ticket.id_technicien:
            # Simulation : résolution = date_creation + 2 jours (ou autre logique)
            resolution_date = ticket.date_creation  # Remplacer par ticket.date_resolution si dispo
            duration = (datetime.utcnow() - ticket.date_creation).total_seconds() / 3600  # en heures
            technicien_durations[ticket.id_technicien].append(duration)

    technicien_moyennes = {
        Utilisateur.query.get(tid).nom: round(sum(durations)/len(durations), 2)
        for tid, durations in technicien_durations.items()
        if durations
    }

    return render_template("stats.html",
        data_statut=statuts,
        data_priorite=priorites,
        moyennes_par_technicien=technicien_moyennes
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

@app.route('/admin/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if current_user.role != 'admin':
        return "Accès refusé", 403

    user = Utilisateur.query.get(id)

    if request.method == 'POST':
        user.nom = request.form['nom']
        user.email = request.form['email']
        if request.form['mot_de_passe']:
            user.set_password(request.form['mot_de_passe'])
        user.role = request.form['role']
        db.session.commit()
        return redirect('/admin/users')

    return render_template('edit_user.html', user=user)

@app.route('/technicien/tickets')
@login_required
def tickets_technicien():
    if current_user.role != 'technicien':
        return "Accès réservé aux techniciens", 403

    tickets = Ticket.query.filter_by(id_technicien=current_user.id).all()
    return render_template('tickets_technicien.html', tickets=tickets)

@app.route('/technicien/tickets/<int:id>/update', methods=['POST'])
@login_required
def maj_ticket(id):
    if current_user.role != 'technicien':
        return "Accès refusé", 403

    ticket = Ticket.query.get(id)
    if ticket.id_technicien != current_user.id:
        return "Ce ticket ne vous est pas assigné.", 403

    ticket.description = request.form.get('description')
    ticket.statut = request.form.get('statut')
    db.session.commit()
    return redirect('/technicien/tickets')

@app.route('/admin/tickets/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_ticket(id):
    if current_user.role != 'admin':
        return "Accès refusé", 403

    ticket = Ticket.query.get(id)
    techniciens = Utilisateur.query.filter_by(role='technicien').all()

    if request.method == 'POST':
        ticket.titre = request.form.get('titre')
        ticket.description = request.form.get('description')
        ticket.priorite = request.form.get('priorite')
        ticket.statut = request.form.get('statut')
        ticket.id_technicien = int(request.form.get('id_technicien'))
        db.session.commit()
        return redirect('/dashboard')

    return render_template('edit_ticket.html', ticket=ticket, techniciens=techniciens)

@app.route('/profil', methods=['GET', 'POST'])
@login_required
def profil():
    if request.method == 'POST':
        current_user.nom = request.form['nom']
        current_user.email = request.form['email']
        nouveau_mdp = request.form['mot_de_passe']
        if nouveau_mdp:
            current_user.set_password(nouveau_mdp)
        db.session.commit()
        return redirect('/dashboard')
    
    return render_template('profil.html', user=current_user)


# 🚀 Lancement
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

# Image officielle Python
FROM python:3.11-slim

# Définir le dossier de travail
WORKDIR /app

# Copier les fichiers dans le conteneur
COPY . /app

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port Flask
EXPOSE 5050

# Lancer l'application
CMD ["python", "app.py"]

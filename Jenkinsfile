pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "gestion-ticket-app"
    }

    stages {
        stage('Clone du repo') {
            steps {
                echo '🔄 Clonage du projet depuis GitHub...'
                // Jenkins le fait automatiquement
            }
        }

        stage('Installation des dépendances') {
            steps {
                echo '📦 Installation des requirements'
                sh 'pip install -r backend/requirements.txt'
            }
        }

        stage('Tests') {
            steps {
                echo '🧪 Lancement des tests (optionnel si tu en as)'
                // Tu peux ignorer ou ajouter des tests si tu en as
            }
        }

        stage('Docker Build') {
            steps {
                echo '🐳 Construction de l’image Docker'
                sh 'docker build -t $DOCKER_IMAGE backend'
            }
        }

        stage('Docker Run') {
            steps {
                echo '🚀 Démarrage du conteneur Docker'
                sh 'docker run -d -p 5050:5050 $DOCKER_IMAGE'
            }
        }
    }

    post {
        success {
            echo '✅ Build terminé avec succès !'
        }
        failure {
            echo '❌ Build échoué.'
        }
    }
}

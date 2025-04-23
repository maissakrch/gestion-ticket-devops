pipeline {
    agent any

    environment {
        PROJECT_NAME = "gestion-ticket-devops"
    }

    stages {
        stage('Clone Repository') {
            steps {
                echo '📥 Clonage du dépôt...'
                git 'https://github.com/maissakrch/gestion-ticket-devops.git'
            }
        }

        stage('Build Docker Images') {
            steps {
                echo '🐳 Construction des images Docker...'
                sh 'docker compose build'
            }
        }

        stage('Deploy Containers') {
            steps {
                echo '🚀 Déploiement des containers...'
                sh 'docker compose down'
                sh 'docker compose up -d'
            }
        }
    }

    post {
        success {
            echo '✅ Déploiement réussi !'
        }
        failure {
            echo '❌ Échec du pipeline Jenkins !'
        }
    }
}

pipeline {
    agent any

    stages {
        stage('Pull code') {
            steps {
                git 'https://github.com/maissakrch/gestion-ticket-devops.git'
            }
        }

        stage('Build & Restart Docker') {
            steps {
                script {
                    // Arrête les anciens conteneurs (si existants)
                    sh 'docker-compose down'

                    // Reconstruit et relance les conteneurs
                    sh 'docker-compose up -d --build'
                }
            }
        }
    }
}

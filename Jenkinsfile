pipeline {
    agent any
    stages {
        stage('build') {
            steps {
                withEnv(readFile('/var/jenkins_home/envfile/.env').split("\n")) {
                    sh '''
                    docker compose build resub-bot
                '''
                }
            }
        }
        stage('deploy') {
            steps {
                withEnv(readFile('/var/jenkins_home/envfile/.env').split("\n")) {
                    sh '''
                    docker compose up -d resub-bot
                '''
                }
            }
        }
    }
}
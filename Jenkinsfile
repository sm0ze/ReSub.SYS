pipeline {
    agent any
    stages {
        stage('build') {
            steps {
                withEnv(readFile('/var/jenkins_home/envfile/.env').split("\n")) {
                    sh '''
                    docker compose -f docker-compose.yaml build resub-bot
                '''
                }
            }
        }
        stage('deploy') {
            steps {
                withEnv(readFile('/var/jenkins_home/envfile/.env').split("\n")) {
                    sh '''
                    docker compose -f docker-compose.yaml up -d resub-bot
                '''
                }
            }
        }
    }
}
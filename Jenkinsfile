pipeline {
    agent any
    stages {
        stage('build') {
            steps {
                script {
                    def envVars = readFile('/var/jenkins_home/envfile/.env').split("\n").toList()
                    withEnv(envVars) {
                        sh 'sudo docker compose -f docker-compose.yaml build resub-bot'
                    }
                }
            }
        }
        stage('deploy') {
            steps {
                script {
                    def envVars = readFile('/var/jenkins_home/envfile/.env').split("\n").toList()
                    withEnv(envVars) {
                        sh 'sudo docker compose -f docker-compose.yaml up -d resub-bot'
                    }
                }
            }
        }
    }
}
pipeline {
    agent any
    stages {
        stage('build') {
            steps {
                sh '''
                    export $(cat /home/pi/docker/.env | xargs)
                    docker compose build bot
                '''
            }
        }
        stage('deploy') {
            steps {
                sh '''
                    export $(cat /home/pi/docker/.env | xargs)
                    docker compose up -d bot
                '''
            }
        }
    }
}
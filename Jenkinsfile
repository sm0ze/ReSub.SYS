pipeline {
    agent any
    stages {
        stage('build') {
            steps {
                script {
                    def customImage = docker.build("resub-discord-bot:${env.BUILD_ID}")
                }
            }
        }
        stage('deploy') {
            steps {
                script {
                    customImage.push('latest')
                }
            }
        }
    }
}

pipeline {
    agent {
        dockerfile true
    }
    stages {
        stage('build') {
            steps {
                def customImage = docker.build("Resub-Bot:${currentBuild.startTimeInMillis}")
            }
        }
    }
}
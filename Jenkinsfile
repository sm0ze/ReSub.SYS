pipeline {
    agent any
    stages {
        node{
            def customImage = docker.build("my-image:${currentBuild.startTimeInMillis}")
            customImage.push('latest')
        }
    }
}
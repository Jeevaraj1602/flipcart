pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'featureprogram',
                    url: 'https://github.com/Jeevaraj1602/flipcart.git'
            }
        }

        stage('Maven Build') {
            steps {
                bat 'mvn clean package'
            }
        }

        stage('Docker Build') {
            steps {
                bat 'docker build -t jeevaraj1602/flipcart:latest .'
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-cred',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    bat 'docker login -u %DOCKER_USER% -p %DOCKER_PASS%'
                    bat 'docker push jeevaraj1602/flipcart:latest'
                }
            }
        }
    }
}
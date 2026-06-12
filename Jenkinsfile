pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        IMAGE_NAME_UNSTABLE = "hassan911123/sentiment-api:unstable"
        IMAGE_NAME_STABLE = "hassan911123/sentiment-api:stable"
        CONTAINER_NAME = "sentiment-api-ci"
    }

    stages {

        stage('Fetch') {
            steps {
                checkout scm
            }
        }

        stage('Build and Run') {
            steps {
                sh '''
                    docker rm -f ${CONTAINER_NAME} || true
                    docker build -t ${IMAGE_NAME_UNSTABLE} .
                    docker run -d --name ${CONTAINER_NAME} -p 5000:5000 ${IMAGE_NAME_UNSTABLE}
                    sleep 25
                '''
            }
        }

        stage('Unit Test') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --quiet -r requirements.txt
                    pytest tests/test_api.py -v
                '''
            }
        }

        stage('UI Test') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest tests/test_ui.py -v
                '''
            }
        }

        stage('Build and Push') {
            steps {
                sh '''
                    echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin

                    docker build -t ${IMAGE_NAME_UNSTABLE} .
                    docker push ${IMAGE_NAME_UNSTABLE}

                    git fetch origin stable-fallback
                    git checkout stable-fallback
                    docker build -t ${IMAGE_NAME_STABLE} .
                    docker push ${IMAGE_NAME_STABLE}
                    git checkout main
                '''
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    kubectl apply -f k8s/pvc.yaml
                    kubectl apply -f k8s/blue-deployment.yaml
                    kubectl apply -f k8s/green-deployment.yaml
                    kubectl apply -f k8s/service.yaml
                '''
            }
        }
    }

    post {
        always {
            sh '''
                docker rm -f ${CONTAINER_NAME} || true
            '''
        }
    }
}

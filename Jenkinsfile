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
                    sleep 30
                '''
            }
        }

        stage('Unit Test') {
            steps {
                sh "docker exec ${CONTAINER_NAME} pytest tests/test_api.py -v"
            }
        }

        stage('UI Test') {
            steps {
                sh "docker exec ${CONTAINER_NAME} pytest tests/test_ui.py -v"
            }
        }

        stage('Build and Push') {
            steps {
                sh '''
                    echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin

                    docker build -t ${IMAGE_NAME_UNSTABLE} .
                    docker push ${IMAGE_NAME_UNSTABLE}

                    rm -rf stable-fallback-build
                    git clone -b stable-fallback https://github.com/janjua911/selfhealing-mlops-FA23-BAI-019.git stable-fallback-build

                    cd stable-fallback-build
                    docker build -t ${IMAGE_NAME_STABLE} .
                    docker push ${IMAGE_NAME_STABLE}
                    cd ..

                    rm -rf stable-fallback-build
                '''
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    if ! minikube status | grep -q "Running"; then
                        minikube start --driver=docker
                    fi

                    eval $(minikube docker-env)

                    kubectl apply -f k8s/pvc.yaml
                    kubectl apply -f k8s/blue-deployment.yaml
                    kubectl apply -f k8s/green-deployment.yaml
                    kubectl apply -f k8s/service.yaml

                    docker rm -f ${CONTAINER_NAME} || true
                '''
            }
        }
    }
}

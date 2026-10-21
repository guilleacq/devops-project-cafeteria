pipeline {
    agent any

    environment {
        // Ajusta tu registry si tienes uno propio provisto por la facultad
        REGISTRY = 'luispee' 
        IMAGE_BACKEND = "${env.REGISTRY}/devops-project-cafeteria-backend"
        IMAGE_FRONTEND = "${env.REGISTRY}/devops-project-cafeteria-frontend"
        VERSION_TAG = "${params.VERSION}"
    }

    options {
        timestamps()
    }

    parameters {
        string(name: 'VERSION', defaultValue: '1.0.0', description: 'Versión a desplegar')
        booleanParam(name: 'EJECUTAR_TESTS', defaultValue: true, description: 'Correr los tests del backend')
    }

    stages {
        stage('Info del Commit') {
            steps {
                echo "Rama: ${env.BRANCH_NAME}"
                echo "Desplegando versión: ${params.VERSION}"
                sh 'git log -1 --oneline'
            }
        }

        stage('Backend: Lint & Tests (Docker Compose Test)') {
            when {
                expression { params.EJECUTAR_TESTS }
            }
            steps {
                echo "Levantando base de datos y ejecutando tests con Docker Compose..."
                
                // 1. Nos aseguramos de levantar la base de datos de test y esperar a que esté saludable
                sh "docker compose --profile test up -d db"
                
                // 2. Ejecutamos el servicio de tests definido en el compose, inyectando la URL de la base de datos del compose
                sh "docker compose --profile test run --rm -e DATABASE_URL='postgresql://cafeteria:cafeteria@db:5432/cafeteria' -v \${WORKSPACE}/backend/reports:/app/reports backend-tests pytest --junitxml=reports/junit.xml"
                
                // 3. Bajamos los servicios temporales para dejar el entorno limpio
                sh "docker compose --profile test down -v"
            }
        }

        stage('Frontend: Build check') {
            steps {
                echo "Validando compilación del Frontend (etapa build)..."
                // Aprovechamos la etapa 'build' del Dockerfile del frontend para asegurar que compila bien
                sh "docker build --target build ./frontend"
            }
        }

        stage('Construir Imágenes de Producción (Runtime)') {
            steps {
                echo "Construyendo imágenes finales para despliegue..."
                
                // Backend Runtime
                sh "docker build --target runtime -t ${IMAGE_BACKEND}:${VERSION_TAG} -t ${IMAGE_BACKEND}:latest ./backend"
                
                // Frontend Runtime (con NGINX)
                sh "docker build --target runtime -t ${IMAGE_FRONTEND}:${VERSION_TAG} -t ${IMAGE_FRONTEND}:latest ./frontend"
            }
        }

        stage('Push al Registry') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh "echo '${DOCKER_PASS}' | docker login -u '${DOCKER_USER}' --password-stdin"
                    
                    sh "docker push ${IMAGE_BACKEND}:${VERSION_TAG}"
                    sh "docker push ${IMAGE_BACKEND}:latest"
                    sh "docker push ${IMAGE_FRONTEND}:${VERSION_TAG}"
                    sh "docker push ${IMAGE_FRONTEND}:latest"
                }
            }
        }

        stage('Deploy a Kubernetes') {
            when {
                branch 'main'
            }
            steps {
                echo "Desplegando en el namespace alumno-team4..."
                
                // Actualizamos las imágenes de los deployments existentes en tu namespace
                sh """
                    kubectl set image deployment/backend backend=${IMAGE_BACKEND}:${VERSION_TAG} -n alumno-team4
                    kubectl set image deployment/frontend frontend=${IMAGE_FRONTEND}:${VERSION_TAG} -n alumno-team4
                """
                
                // Verificamos que el rollout se complete exitosamente
                sh """
                    kubectl rollout status deployment/backend -n alumno-team4
                    kubectl rollout status deployment/frontend -n alumno-team4
                """
            }
        }
    }

    post {
        always {
            // Publica los resultados de los tests en Jenkins
            junit allowEmptyResults: true, testResults: 'backend/reports/junit.xml'
        }
    }
}
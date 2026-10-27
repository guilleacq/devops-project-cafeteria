pipeline {
    agent any

    environment {
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

        stage('Backend: Lint & Tests (Docker Target Test)') {
            when {
                expression { params.EJECUTAR_TESTS }
            }
            steps {
                echo "Construyendo imagen de pruebas del backend..."
                sh "docker build --target test -t backend-test-env:latest ./backend"
                
                echo "Creando red de prueba temporal para la base de datos..."
                sh "docker network create test-net-pipeline || true"
                
                echo "Levantando base de datos temporal para los tests..."
                sh """
                    docker run -d --name temp-test-db \
                      --network test-net-pipeline \
                      -e POSTGRES_USER=cafeteria \
                      -e POSTGRES_PASSWORD=cafeteria \
                      -e POSTGRES_DB=cafeteria \
                      -v \${WORKSPACE}/db/init.sql:/docker-entrypoint-initdb.d/01_init.sql:ro \
                      postgres:16
                """
                
                echo "Esperando a que la base de datos esté lista..."
                sh "sleep 5"
                
                echo "Ejecutando tests con pytest dentro del contenedor..."
                // Acá inyectamos la DATABASE_URL apuntando al contenedor temporal dentro de la red privada
                sh """
                    docker run --rm \
                      --network test-net-pipeline \
                      -e DATABASE_URL='postgresql://cafeteria:cafeteria@temp-test-db:5432/cafeteria' \
                      -v \${WORKSPACE}/backend/reports:/app/reports \
                      backend-test-env:latest pytest --junitxml=reports/junit.xml
                """
            }
        }

        stage('Frontend: Build check') {
            steps {
                echo "Validando compilación del Frontend (etapa build)..."
                sh "docker build --target build ./frontend"
            }
        }

        stage('Construir Imágenes de Producción (Runtime)') {
            steps {
                echo "Construyendo imágenes finales para despliegue..."
                sh "docker build --target runtime -t ${IMAGE_BACKEND}:${VERSION_TAG} -t ${IMAGE_BACKEND}:latest ./backend"
                sh "docker build --target runtime -t ${IMAGE_FRONTEND}:${VERSION_TAG} -t ${IMAGE_FRONTEND}:latest ./frontend"
            }
        }

        stage('Push al Registry') {
            /* when {
                branch 'main'
            } */
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
            /* when {
                branch 'main'
            } */
            steps {
                echo "Desplegando en el namespace alumno-team4..."
                sh """
                    kubectl set image deployment/backend backend=${IMAGE_BACKEND}:${VERSION_TAG} -n alumno-team4
                    kubectl set image deployment/frontend frontend=${IMAGE_FRONTEND}:${VERSION_TAG} -n alumno-team4
                """
                sh """
                    kubectl rollout status deployment/backend -n alumno-team4
                    kubectl rollout status deployment/frontend -n alumno-team4
                """
            }
        }
    }

    post {
        always {
            // Limpiamos los recursos temporales de los tests si llegaron a quedar colgados
            sh "docker stop temp-test-db || true"
            sh "docker rm temp-test-db || true"
            sh "docker network rm test-net-pipeline || true"
            
            junit allowEmptyResults: true, testResults: 'backend/reports/junit.xml'
        }
    }
}
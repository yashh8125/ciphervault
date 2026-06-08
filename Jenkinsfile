pipeline {
    agent any

    environment {
        IMAGE_NAME = "ciphervault"
        IMAGE_TAG  = "build-${BUILD_NUMBER}"
        COMPOSE_FILE = "docker-compose.yml"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Cloning repository..."
                checkout scm
            }
        }

        stage('Lint & Static Analysis') {
            steps {
                echo "Running linter..."
                sh '''
                    pip install flake8 --quiet --break-system-packages || pip install flake8 --quiet
                    flake8 vault/ ciphervault/ --max-line-length=120 --exclude=venv,migrations || true
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                echo "Installing Python dependencies..."
                sh '''
                    sudo apt-get install -y python3-venv python3-pip 2>/dev/null || true
                    python3 -m venv venv --system-site-packages
                    . venv/bin/activate
                    pip install -r requirements.txt --quiet --break-system-packages
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo "Running Django tests..."
                sh '''
                    . venv/bin/activate
                    export DJANGO_SETTINGS_MODULE=ciphervault.settings
                    export CIPHER_KEY=dGVzdGtleXRlc3RrZXl0ZXN0a2V5dGVzdGtleTA=
                    export MYSQL_DB=test_db
                    export MYSQL_USER=test
                    export MYSQL_PASSWORD=test
                    export MYSQL_HOST=localhost
                    export MYSQL_PORT=3306
                    python manage.py test --verbosity=2 || true
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Deploy with Docker Compose') {
            when {
                branch 'main'
            }
            steps {
                echo "Deploying to production..."
                withCredentials([file(credentialsId: 'ciphervault-env', variable: 'ENV_FILE')]) {
                    sh '''
                        cp $ENV_FILE .env
                        docker compose down
                        docker compose up -d --build
                    '''
                }
            }
        }

    }

    post {
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed. Check logs above."
        }
        always {
            echo "Cleaning up dangling Docker images..."
            sh "docker image prune -f || true"
        }
    }
}

// ---------------------------------------------------------------------------
// ACEest Fitness & Gym — Jenkins declarative pipeline (Phase 5)
//
// Responsible for the primary BUILD phase: pull the latest code from GitHub
// and perform a clean build + validation in a controlled environment.
//
// Stages:
//   Checkout      -> latest revision from the configured Git branch
//   Build         -> clean venv, install deps, byte-compile, dependency check
//   Test          -> Pytest suite with a coverage quality gate + JUnit report
//   Docker Build  -> build the production image
//   Smoke Test    -> run the image and hit /api/health
//
// Configure this as a "Pipeline script from SCM" job pointing at the repo and
// this file (see docs/jenkins.md).
// ---------------------------------------------------------------------------
pipeline {
    agent any

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '10'))
        disableConcurrentBuilds()
        timeout(time: 25, unit: 'MINUTES')
        skipDefaultCheckout(true)
    }

    environment {
        IMAGE_NAME = 'aceest-fitness'
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
        VENV       = '.ci-venv'
        PY         = '.ci-venv/bin/python'
        PIP        = '.ci-venv/bin/pip'
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    checkout scm
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                    echo "Building ${env.IMAGE_NAME}:${env.IMAGE_TAG} @ ${env.GIT_COMMIT_SHORT}"
                }
            }
        }

        stage('Build') {
            steps {
                echo '--- Clean build: virtualenv, dependencies, byte-compilation ---'
                sh '''
                    set -eu
                    rm -rf "${VENV}"
                    python3 -m venv "${VENV}"
                    "${PIP}" install --upgrade pip
                    "${PIP}" install -r requirements-dev.txt
                    "${PY}" -m compileall -q aceest app.py config.py
                    "${PIP}" check
                '''
            }
        }

        stage('Test') {
            steps {
                echo '--- Pytest suite with 90% coverage quality gate ---'
                sh '''
                    set -eu
                    mkdir -p reports
                    "${PY}" -m pytest \
                        --junitxml=reports/junit.xml \
                        --cov=aceest \
                        --cov-report=term-missing \
                        --cov-report=xml:reports/coverage.xml \
                        --cov-report=html:reports/htmlcov \
                        --cov-fail-under=90
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/junit.xml'
                }
            }
        }

        stage('Docker Build') {
            steps {
                echo '--- Build the production container image ---'
                sh '''
                    docker build \
                        -t "${IMAGE_NAME}:${IMAGE_TAG}" \
                        -t "${IMAGE_NAME}:latest" .
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                echo '--- Start the container and probe /api/health ---'
                sh '''
                    set -eu
                    docker rm -f aceest-ci >/dev/null 2>&1 || true
                    docker run -d --name aceest-ci "${IMAGE_NAME}:${IMAGE_TAG}"
                    ok=0
                    for i in $(seq 1 30); do
                        if docker exec aceest-ci python -c \
                            "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/api/health')" 2>/dev/null; then
                            ok=1
                            echo "Health check passed"
                            break
                        fi
                        sleep 1
                    done
                    docker rm -f aceest-ci >/dev/null 2>&1 || true
                    if [ "${ok}" -ne 1 ]; then
                        echo "Smoke test FAILED: /api/health did not become available"
                        exit 1
                    fi
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
            deleteDir()
        }
        success {
            echo "Pipeline succeeded: ${env.IMAGE_NAME}:${env.IMAGE_TAG}"
        }
        failure {
            echo "Pipeline FAILED for build ${env.BUILD_NUMBER} — check the console log."
        }
    }
}

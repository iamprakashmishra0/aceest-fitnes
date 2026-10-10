# ---------------------------------------------------------------------------
# Custom Jenkins controller for the ACEest pipeline (Phase 5).
#
# Adds Python (to run the app + Pytest) and the Docker CLI (to build images
# using the host daemon via the mounted /var/run/docker.sock), and pre-installs
# the required plugins and Configuration-as-Code settings.
#
# Build:  docker build -t aceest-jenkins jenkins/
# (Normally used through jenkins/docker-compose.yml.)
# ---------------------------------------------------------------------------
FROM jenkins/jenkins:lts-jdk17

USER root

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        python3 \
        python3-venv \
        python3-pip \
        curl \
        ca-certificates \
        git \
        docker-cli \
 && rm -rf /var/lib/apt/lists/*

# Install the pipeline plugins into the image's reference directory; the
# official entrypoint copies them into JENKINS_HOME on first start.
USER jenkins
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

# Skip the interactive setup wizard — the job and admin user come from the
# Configuration-as-Code file mounted at /casc/jenkins.yaml.
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"

# 8080 = web UI, 50000 = inbound build-agent port.
EXPOSE 8080 50000

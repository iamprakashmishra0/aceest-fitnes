# Jenkins Guide — ACEest Fitness & Gym (Phase 5)

Phase 5 adds a **Jenkins server** that owns the primary **BUILD** phase. It pulls
the latest revision from GitHub and performs a clean, controlled build of the
environment, acting as a second validation layer (after the local Pytest suite
and before the GitHub Actions pipeline in Phase 6).

---

## 1. Overview

| Item | Value |
| --- | --- |
| Pipeline definition | [`Jenkinsfile`](../Jenkinsfile) (declarative) |
| Job name | `aceest-fitness` |
| Repository branch | `*/main` |
| Agent requirements | Python 3, Docker CLI, `curl`, `git` |
| Quality gate | Pytest with `--cov-fail-under=90` |
| Reports | JUnit XML + coverage XML/HTML |

The pipeline is portable: the same `Jenkinsfile` runs on a containerised
Jenkins (recommended below) or a natively installed controller.

---

## 2. How the pipeline works

| Stage | What it does | Why |
| --- | --- | --- |
| **Checkout** | `checkout scm` — pulls the latest code. | Ensures a pristine working tree. |
| **Build** | Creates a fresh virtualenv, installs `requirements-dev.txt`, byte-compiles the package and runs `pip check`. | A *clean build* proves the code compiles and dependencies are consistent. |
| **Test** | Runs Pytest, emitting JUnit + coverage reports and failing below 90% coverage. | The automated quality gate. |
| **Docker Build** | Builds `aceest-fitness:<build-number>` and `:latest`. | Confirms the image assembles in CI. |
| **Smoke Test** | Starts the container and probes `/api/health`. | Confirms the built artefact actually runs. |

`post` blocks publish reports (`reports/**`), clean the workspace and report the
overall result.

---

## 3. Installation

Choose **one** of the two options. Option A is recommended because it is
reproducible and installs everything (Python, Docker CLI, plugins) in one step.

### 3.1 Option A — Dockerised Jenkins (recommended)

**Prerequisites**

- Docker Engine 20.10+
- `docker-compose` (v1.29+ or the Compose v2 plugin)

**Build and start**

```bash
# from the repository root
docker-compose -f jenkins/docker-compose.yml up -d --build
```

This builds `jenkins/Dockerfile` (Jenkins LTS + Python + Docker CLI + plugins),
mounts the host Docker socket and the Configuration-as-Code file, and exposes
the UI on port `8080`.

Verify it is up:

```bash
docker-compose -f jenkins/docker-compose.yml ps
docker logs -f aceest-jenkins     # wait for "Jenkins is fully up and running"
```

> **Credentials:** change `JENKINS_ADMIN_PASSWORD` and `GITHUB_REPO_URL` in
> `jenkins/docker-compose.yml` before exposing the host. The default login is
> `admin` / `admin`.

### 3.2 Option B — Native install (Ubuntu / Debian)

**3.2.1 Install Java 17**

```bash
sudo apt update
sudo apt install -y openjdk-17-jre-headless
java -version
```

**3.2.2 Install Jenkins**

```bash
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key \
  | sudo tee /usr/share/keyrings/jenkins-keyring.asc >/dev/null

echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
https://pkg.jenkins.io/debian-stable binary/" \
  | sudo tee /etc/apt/sources.list.d/jenkins.list >/dev/null

sudo apt update
sudo apt install -y jenkins
sudo systemctl enable --now jenkins
```

Retrieve the initial admin password:

```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

**3.2.3 Install the build tools**

```bash
sudo apt install -y python3 python3-venv python3-pip curl git docker.io
# let the jenkins user use Docker
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

**3.2.4 Install the plugins**

In the UI: **Manage Jenkins → Plugins → Available plugins**, then install:

`Pipeline`, `Git`, `Docker Pipeline`, `JUnit`, `HTML Publisher`,
`GitHub`, `Pipeline: Stage View`, `Job DSL`, `Configuration as Code`,
`Timestamper`, `Workspace Cleanup`.

---

## 4. Setup

### 4.1 Option A — automatic (JCasC)

The `jenkins/casc/jenkins.yaml` file configures everything on startup:

- an **admin** user (password from `JENKINS_ADMIN_PASSWORD`),
- the **`aceest-fitness`** pipeline job, checking out `GITHUB_REPO_URL` on
  `*/main` and running `Jenkinsfile`,
- a **Poll SCM** trigger (`H/5 * * * *`).

Open <http://localhost:8080/> and log in as `admin`. The job is ready to run.

### 4.2 Option B — manual job creation

1. Complete the setup wizard and install the suggested + listed plugins.
2. **New Item → Pipeline**, name it **`aceest-fitness`**, click **OK**.
3. Under **Build Triggers**, tick **Poll SCM** and set `H/5 * * * *`.
4. Under **Pipeline**:
   - **Definition:** *Pipeline script from SCM*
   - **SCM:** *Git*
   - **Repository URL:** `https://github.com/<your-username>/aceest-fitness.git`
   - **Branch Specifier:** `*/main`
   - **Script Path:** `Jenkinsfile`
5. **Save**.

> Public repositories need no credentials. For a private repo, add a
> *Username with password* (GitHub personal access token) or SSH credential
> under **Manage Jenkins → Credentials** and select it in the SCM section.

---

## 5. Triggering builds

- **Manually:** open the job → **Build Now**.
- **Polling:** the configured `scm` trigger checks GitHub every ~5 minutes.
- **Webhook (instant):** in GitHub go to **Settings → Webhooks → Add webhook**:
  - Payload URL: `http://<jenkins-host>:8080/github-webhook/`
  - Content type: `application/json`
  - Event: *Just the push event*
  The Jenkins job option **GitHub hook trigger for GITScm polling** must be
  enabled. (Requires Jenkins to be reachable from GitHub — use a public URL or a
  tunnel such as ngrok.)

---

## 6. The quality gate

The **Test** stage runs:

```bash
pytest --junitxml=reports/junit.xml \
       --cov=aceest --cov-report=xml:reports/coverage.xml \
       --cov-fail-under=90
```

- A **failing test** fails the build (via the JUnit post-processing).
- Coverage **below 90%** fails the build.
- The current suite passes at **100%** coverage (88 tests).

Results appear on the build page: **Test Result**, **Coverage Report** and
archived `reports/` artefacts.

---

## 7. Troubleshooting

| Symptom | Fix |
| --- | --- |
| `docker: command not found` inside a build | Install the CLI in the image (Option A handles this) or `apt install docker.io` (Option B). |
| `permission denied /var/run/docker.sock` | Add the Jenkins user to the `docker` group (`usermod -aG docker jenkins`) and restart; or run the container with `user: root`. |
| Job cannot find `Jenkinsfile` | Ensure **Script Path** is `Jenkinsfile` and the branch spec is `*/main`. |
| `python3 -m venv` fails | Install `python3-venv` (`sudo apt install python3-venv`). |
| Plugins missing after first start | Rebuild the image (`docker-compose ... up -d --build`) or install them under **Manage Jenkins → Plugins**. |
| Webhook does not fire | Jenkins must be reachable from GitHub; use polling or a tunnel. |

---

## 8. Cleanup

```bash
docker-compose -f jenkins/docker-compose.yml down -v
docker rmi aceest-jenkins:latest
```

> `down -v` also removes the `jenkins_home` volume and all build history.

---

*ACEest Fitness & Gym — Introduction to DevOps, Assignment 1, Phase 5.*

# GitHub Actions CI Guide — ACEest Fitness & Gym (Phase 6)

Phase 6 delivers a fully automated CI/CD pipeline defined in
[`.github/workflows/main.yml`](../.github/workflows/main.yml). It runs on every
push and pull request and performs three stages: **Build & Lint**, **Docker
Image Assembly** and **Automated Testing** (executed inside the container).

---

## 1. Overview

| Item | Value |
| --- | --- |
| Workflow file | `.github/workflows/main.yml` |
| Workflow name | `CI` |
| Triggers | `push`, `pull_request` (to `main`/`develop`), `workflow_dispatch` |
| Runner | GitHub-hosted `ubuntu-latest` |
| Jobs | `build-and-lint`, `docker-image`, `test-in-container` |
| Quality gate | Pytest with `--cov-fail-under=90` |
| Artefacts | JUnit XML, coverage XML/HTML |

---

## 2. The three stages

### Stage 1 — Build & Lint (`build-and-lint`)

| Step | Command | Purpose |
| --- | --- | --- |
| Checkout | `actions/checkout@v4` | Get the source. |
| Set up Python | `actions/setup-python@v5` (3.12, pip cache) | Reproducible interpreter + dependency cache. |
| Install dependencies | `pip install -r requirements-dev.txt` | Runtime + test + lint tooling. |
| Compile (syntax check) | `python -m compileall -q aceest app.py config.py` | Fails on syntax errors. |
| Lint | `flake8 aceest app.py config.py tests` | Enforces style/quality (config in `.flake8`). |

### Stage 2 — Docker Image Assembly (`docker-image`)

```yaml
uses: docker/build-push-action@v6
with:
  context: .
  push: false
  load: true
  tags: aceest-fitness:ci
  cache-from: type=gha
  cache-to: type=gha,mode=max
```

Builds the **production** image (default `runtime` stage) and loads it into the
runner, then smoke-tests `/api/health`. BuildKit's GitHub Actions cache keeps
subsequent builds fast.

### Stage 3 — Automated Testing (`test-in-container`)

Builds the dedicated **test** image (`--target test`) and runs Pytest **inside
the container**:

```bash
docker run --rm -v "$PWD/reports:/app/reports" aceest-fitness:test \
  python -m pytest \
    --junitxml=reports/junit.xml \
    --cov=aceest \
    --cov-report=term-missing \
    --cov-report=xml:reports/coverage.xml \
    --cov-report=html:reports/htmlcov \
    --cov-fail-under=90
```

The resulting `reports/` directory is uploaded as the `test-reports` artefact
even if the step fails (`if: always()`).

### Job dependency graph

```
build-and-lint ──┬──► docker-image
                 └──► test-in-container
```

Both heavy jobs wait for the fast lint job, so obvious failures surface first.

---

## 3. Where the workflow lives & how it is enabled

1. The file `.github/workflows/main.yml` is committed to the repository.
2. GitHub Actions is **enabled by default** for public repositories — no setup
   required. (For a private repo: **Settings → Actions → General → Allow all
   actions**.)
3. The workflow runs automatically on the next push / pull request. It can also
   be started manually from **Actions → CI → Run workflow**
   (`workflow_dispatch`).

No secrets are required — the pipeline only builds and tests. Pushing the image
to a registry (e.g. GHCR/Docker Hub) would require `docker/login-action` and
repository secrets; that is intentionally out of scope here.

---

## 4. Viewing results

- **Actions tab → CI** shows each run, the job graph and per-step logs.
- **Artefacts:** the `test-reports` artefact exposes `junit.xml`,
  `coverage.xml` and the HTML report for download.
- **Badge:** the README shows the live status badge:

  ```markdown
  ![CI](https://github.com/iamprakashmishra0/aceest-fitnes/actions/workflows/main.yml/badge.svg)
  ```

---

## 5. Reproducing the pipeline locally

Every CI step can be run on a workstation:

```bash
# Stage 1 — Build & Lint
python -m venv .ci-venv && . .ci-venv/bin/activate
pip install -r requirements-dev.txt
python -m compileall -q aceest app.py config.py
flake8 aceest app.py config.py tests

# Stage 2 — Docker Image Assembly
docker build -t aceest-fitness:ci .
docker run -d --name aceest-ci aceest-fitness:ci
docker exec aceest-ci python -c \
  "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/api/health')"
docker rm -f aceest-ci

# Stage 3 — Automated Testing inside the container
docker build --target test -t aceest-fitness:test .
docker run --rm -v "$PWD/reports:/app/reports" aceest-fitness:test \
  python -m pytest --cov=aceest --cov-fail-under=90
```

---

## 6. Jenkins and GitHub Actions — integration logic

The two CI systems are complementary rather than redundant; together they form
the assignment's "secondary validation layer" story:

| | **Jenkins** (Phase 5) | **GitHub Actions** (Phase 6) |
| --- | --- | --- |
| Hosting | Self-hosted controller (`jenkins/`) | GitHub-hosted runner |
| Trigger | GitHub polling / webhook | push & pull_request events |
| Role | Authoritative **BUILD** gate on a controlled server | Fast, per-commit feedback in the repo |
| Stages | Checkout → Build → Test → Docker Build → Smoke Test | Build & Lint → Docker Assembly → Tests-in-container |
| Reports | JUnit + coverage in the build page | Workflow artefacts |

**Flow:** a developer pushes a branch → **GitHub Actions** validates every
commit/pull request quickly with the same `Dockerfile` and Pytest suite →
once merged to `main`, **Jenkins** performs the heavier, controlled clean build
and image assembly. Because both consume the identical `requirements*.txt`,
`Dockerfile`, `pytest.ini` and `.flake8`, they enforce the *same* quality gate
(`pytest --cov-fail-under=90`), guaranteeing environmental consistency from
local development through build to release.

---

## 7. Troubleshooting

| Symptom | Likely cause / fix |
| --- | --- |
| `flake8` reports errors | Run `flake8` locally and fix; config is in `.flake8`. |
| Docker build fails on the runner | Ensure the `Dockerfile` builds locally (`docker build -t aceest-fitness:ci .`). |
| Tests pass locally but fail in CI | Confirm you are running inside the test image (`--target test`). |
| Coverage gate fails | Add tests; the global threshold is 90%. |
| Workflow does not appear | Ensure the file is at `.github/workflows/main.yml` on the default branch. |
| `permission denied` for actions | Private repos: allow actions under **Settings → Actions → General**. |

---

*ACEest Fitness & Gym — Introduction to DevOps, Assignment 1, Phase 6.*

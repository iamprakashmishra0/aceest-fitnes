# Git Workflow — ACEest Fitness & Gym

This document describes the **Version Control System (VCS) strategy** used for
the ACEest Fitness & Gym project (Assignment 1, Phase 2). The goal is a clean,
reviewable history with industry-standard branching and commit conventions.

---

## 1. Branching Model

The project uses a lightweight **Git Flow** model:

| Branch | Purpose | Lifetime |
| --- | --- | --- |
| `main` | Production-ready code. Every commit is tagged as a release. | Permanent |
| `develop` | Integration branch where completed work is merged before release. | Permanent |
| `feature/<name>` | A single new capability (e.g. `feature/api-blueprint`). | Temporary |
| `bugfix/<name>` | A single defect fix. | Temporary |
| `infra/<name>` | Tooling, configuration, documentation and CI/CD changes. | Temporary |

### Flow

```
main ──●────────────────●────────────●───────────────●──▶ (tags: v1.0.0)
        \              /                               \
         ●──●──●──●──●  develop                          ●──▶
             \    /   \
        feature/...    infra/...
```

1. Branch off `develop` (or `main` for hotfixes).
2. Commit small, self-contained changes.
3. Open a **pull request** into `develop`.
4. After review/CI passes, merge with `--no-ff` to preserve the branch history.
5. When a milestone is reached, merge `develop` into `main` and tag it.

---

## 2. Branch Naming

```
feature/<short-description>     feature/client-registration
bugfix/<short-description>      bugfix/calorie-rounding
infra/<short-description>       infra/docker-build
```

Use lower-case, hyphen-separated names. Keep them short and descriptive.

---

## 3. Commit Message Convention

Commits follow the **Conventional Commits** specification:

```
<type>(<optional scope>): <short summary>

<optional body explaining what and why>
```

| Type | Use for |
| --- | --- |
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only |
| `test` | Adding or fixing tests |
| `refactor` | Code change that is not a feature or fix |
| `infra` / `chore` | Build, tooling, configuration |
| `ci` | CI/CD pipeline changes |

**Rules**

- Use the **imperative mood**: "add client endpoint", not "added".
- Keep the summary under ~72 characters.
- Reference issues where relevant (e.g. `closes #12`).
- One logical change per commit.

**Examples**

```
feat(api): add client CRUD endpoints
feat(services): implement calorie and BMI calculations
infra: add application factory and layered config
docs: document Git branching and commit conventions
fix(repository): cascade client deletion to child records
```

---

## 4. Release & Tagging

Releases are tagged on `main` using semantic versioning:

```bash
git checkout main
git merge --no-ff develop -m "release: v1.0.0"
git tag -a v1.0.0 -m "ACEest Fitness & Gym v1.0.0"
git push origin main --tags
```

| Version | Meaning |
| --- | --- |
| `MAJOR` | Breaking change |
| `MINOR` | New feature, backward compatible |
| `PATCH` | Bug fix, backward compatible |

---

## 5. Day-to-day Commands

```bash
# Start a feature
git checkout develop
git pull
git checkout -b feature/client-registration

# Work and commit
git add -p
git commit -m "feat(ui): add client registration form"

# Publish and open a pull request
git push -u origin feature/client-registration

# After the PR is merged, tidy up
git checkout develop
git pull
git branch -d feature/client-registration
```

---

## 6. Remote Synchronisation (GitHub)

```bash
# From the project root
git init
git branch -M main
git remote add origin https://github.com/<your-username>/aceest-fitness.git

# First push (after creating the empty public repo on GitHub)
git push -u origin main
git push -u origin develop
git push origin --tags
```

If you use the GitHub CLI:

```bash
gh auth login
gh repo create aceest-fitness --public --source=. --remote=origin --push
```

---

## 7. `.gitignore`

Build artefacts, virtual environments, databases and generated reports are
excluded from version control (see `.gitignore`). The SQLite database
`aceest_fitness.db` is generated at runtime and never committed.

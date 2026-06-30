# PyPI publish — maintainer guide

## What failed (trusted publishing)

If you see:

```text
invalid-publisher: valid token, but no corresponding publisher
environment: MISSING
```

GitHub Actions tried **OIDC trusted publishing** because the workflow had `permissions: id-token: write`, but PyPI has **no trusted publisher** registered for `KanakMalpani/Loop-Engineering` + that workflow file.

Workflows now use **API token auth only** (`PYPI_API_TOKEN`). Trusted publishing is optional (see below).

Note: GitHub does not allow `secrets` in `if:` conditions — missing tokens surface as publish-step errors from `pypa/gh-action-pypi-publish`.

---

## Quick fix — API token (recommended)

### 1. Create a PyPI token

1. Log in at [pypi.org](https://pypi.org/)
2. **Account settings** → **API tokens** → **Add API token**
3. Scope:
   - **Entire account** (simplest; required for first upload of new project `le-loop-stack`), or
   - Per-project tokens for `le-loopforge`, `le-loopctl`, `le-loop-stack` after each project exists

Copy the token (starts with `pypi-`).

### 2. Add GitHub secret

1. [Loop-Engineering → Settings → Secrets and variables → Actions](https://github.com/KanakMalpani/Loop-Engineering/settings/secrets/actions)
2. **New repository secret**
3. Name: `PYPI_API_TOKEN`
4. Value: paste the `pypi-...` token

### 3. Publish order

Run workflows on `main` in this order:

| Order | Workflow | Package | Version in repo |
|-------|----------|---------|-----------------|
| 1 | Publish loopforge to PyPI | `le-loopforge` | 0.5.0 |
| 2 | Publish loopctl to PyPI | `le-loopctl` | 0.5.0 |
| 3 | Publish loopbench to PyPI | `loopbench` | 0.2.0 |
| 4 | Publish loopgym to PyPI | `loopgym` | 0.1.3 |
| 5 | Publish le-loop-stack to PyPI | `le-loop-stack` | 0.4.0 |

**Actions** → select workflow → **Run workflow** → branch `main`.

### 4. Verify

```bash
pip index versions le-loopctl
pip index versions le-loop-stack
```

Or fresh venv:

```bash
pip install "le-loop-stack>=0.4.0"
loopctl score --spec path/to/minimal-loop.yaml --json
```

---

## Optional — trusted publishing (no long-lived token)

Configure **on PyPI for each project** (`le-loopforge`, `le-loopctl`, `le-loop-stack`):

1. Project → **Publishing** → **Add a new pending publisher**
2. **PyPI** → **GitHub**
3. **Owner:** `KanakMalpani`
4. **Repository:** `Loop-Engineering`
5. **Workflow name:** e.g. `publish-loopctl.yml` (one publisher per workflow, or use filename without path)
6. **Environment name:** leave **empty** (must match workflow; our workflows do not use GitHub Environments)

Then restore in the workflow:

```yaml
permissions:
  id-token: write
  contents: read
```

And remove the `password:` line from `pypa/gh-action-pypi-publish`.

Do **not** mix both unless you know which path the action will take.

---

## New project: le-loop-stack

First upload of `le-loop-stack` requires either:

- Account-scoped API token, or
- Manual `twine upload` once to create the project, then project-scoped tokens

---

## Local publish (fallback)

Wheels for Wave 16 stack (built locally):

| Package | Version | Path |
|---------|---------|------|
| loopbench | 0.2.0 | `07-loopbench/dist/` |
| loopgym | 0.1.3 | `06-loopgym/dist/` |
| le-loopforge | 0.5.0 | `01-loop-engineering/loopforge/dist/` |
| le-loopctl | 0.5.0 | `01-loop-engineering/loopctl/dist/` |
| le-loop-stack | 0.4.0 | `01-loop-engineering/stack/dist/` |

```bash
cd loopctl && python -m build
python -m twine upload dist/*   # TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-...
```

Publish order: loopbench → loopgym → loopforge → loopctl → le-loop-stack.

Registry: [ECOSYSTEM_VERSIONS.md](../../ECOSYSTEM_VERSIONS.md)

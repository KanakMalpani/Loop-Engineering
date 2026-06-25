# PyPI package naming

Loop Engineering publishes under **`le-`** prefixed names because the short names on PyPI belong to unrelated projects.

| Install with pip | CLI command | PyPI page | Notes |
|------------------|-------------|-----------|-------|
| **`le-loop-stack`** | (meta) | https://pypi.org/project/le-loop-stack/ | **Recommended** — installs forge + ctl + gym |
| **`le-loopforge`** | `loopforge` | https://pypi.org/project/le-loopforge/ | Do **not** `pip install loopforge` |
| **`le-loopctl`** | `loopctl` | https://pypi.org/project/le-loopctl/ | Do **not** `pip install loopctl` |
| **`loopgym`** | (Python API) | https://pypi.org/project/loopgym/ | LoopGym runtime; **0.1.2+** emits Loop Trace 1.0 |
| **`loopbench`** | `loopbench` | https://pypi.org/project/loopbench/ | Public benchmark CLI |

## Recommended install (Golden Path v3)

```bash
pip install "le-loop-stack>=0.1.0"
```

Optional extras:

```bash
pip install "le-loop-stack[bench,langgraph,crewai]>=0.1.0"
```

## Manual pins

```bash
pip install "le-loopforge>=0.2.1" "le-loopctl>=0.2.0" "loopgym>=0.1.2" loopbench
```

## From source (maintainers)

```bash
pip install -e loopforge -e loopctl -e stack
pip install loopgym loopbench
```

CLI entry points are unchanged after install: `loopforge`, `loopctl`, `loopbench`.

Registry: [ECOSYSTEM_VERSIONS.md](../ECOSYSTEM_VERSIONS.md)

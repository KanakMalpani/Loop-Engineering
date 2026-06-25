# PyPI package naming

Loop Engineering publishes under **`le-`** prefixed names because the short names on PyPI belong to unrelated projects.

| Install with pip | CLI command | PyPI page | Notes |
|------------------|-------------|-----------|-------|
| **`le-loopforge`** | `loopforge` | https://pypi.org/project/le-loopforge/ | Do **not** `pip install loopforge` — that is [fenderfonic/loopforge](https://pypi.org/project/loopforge/) |
| **`le-loopctl`** | `loopctl` | https://pypi.org/project/le-loopctl/ | Do **not** `pip install loopctl` — unrelated package at 0.0.9 |
| **`loopgym`** | (Python API) | https://pypi.org/project/loopgym/ | LoopGym runtime; **0.1.2+** emits Loop Trace 1.0 |
| **`loopbench`** | `loopbench` | https://pypi.org/project/loopbench/ | Public benchmark CLI |

## Recommended install (Golden Path)

```bash
pip install "le-loopforge>=0.2.0" "le-loopctl>=0.1.0" "loopgym>=0.1.2" loopbench
```

## From source (maintainers)

```bash
pip install -e loopforge -e loopctl
pip install loopgym loopbench
```

CLI entry points are unchanged after install: `loopforge`, `loopctl`, `loopbench`.

Registry: [ECOSYSTEM_VERSIONS.md](../ECOSYSTEM_VERSIONS.md)

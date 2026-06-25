# loopctl

Unified Loop Engineering toolchain CLI. Requires `loopforge>=0.2.0`.

```bash
pip install le-loopctl
loopctl validate my-loop.yaml
loopctl score --spec my-loop.yaml --json
loopctl trace validate trace.json
loopctl observed trace.json --json
```

When run from the discipline repo clone, `diagram`, `level`, and `bench` passthrough are also available.

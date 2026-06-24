# Maintainer sync — sibling repos

Use when updating cross-repo pointers (LoopNet version, REPRODUCE links, ECOSYSTEM table).

## Preferred: GitHub CLI

```bash
# Read current file
gh api repos/KanakMalpani/loopnet/readme --jq .content | base64 -d

# Update a file (get SHA first)
SHA=$(gh api repos/KanakMalpani/loopnet/contents/README.md --jq .sha)
gh api repos/KanakMalpani/loopnet/contents/README.md -X PUT \
  -f message="docs: align LoopNet v0.2 primary pointer" \
  -f content="$(base64 -w0 README.md)" \
  -f sha="$SHA"
```

On Windows PowerShell, use the Python helper below.

## Helper script

```bash
python scripts/push_github_file.py --repo loopnet --path README.md --file path/to/README.md --message "docs: ..."
```

See `scripts/push_github_file.py` for arguments.

## Checklist after sync

1. Verify [ECOSYSTEM_VERSIONS.md](../ECOSYSTEM_VERSIONS.md) matches live READMEs
2. Append row to [docs/AUDIT-2026-06.md](../docs/AUDIT-2026-06.md) if versions changed

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
2. **Adoption URL** present in every sibling README: `https://github.com/KanakMalpani/Loop-Engineering/discussions/10`
3. Run `python scripts/check_adoption_links.py` (also in daily check-in)
4. Run `python scripts/track_adoption_signals.py` — see [docs/adoption-tracker/](../docs/adoption-tracker/)
5. Community pack: [contributions/EXTERNAL_SUBMISSIONS.md](../contributions/EXTERNAL_SUBMISSIONS.md) · [LOOP_PLAYGROUND.md](../contributions/LOOP_PLAYGROUND.md)
6. Community platform status: [docs/maintainer/COMMUNITY_PLATFORM_STATUS.md](../docs/maintainer/COMMUNITY_PLATFORM_STATUS.md)
7. Partner outreach: `python scripts/adoption_wave11.py` · follow-up `adoption_wave12.py`
8. Append row to [docs/AUDIT-2026-06.md](../docs/AUDIT-2026-06.md) if versions changed

Local mirrors for sibling READMEs live in [docs/ecosystem-sync/](../docs/ecosystem-sync/) — edit there, then push with `push_github_file.py`.

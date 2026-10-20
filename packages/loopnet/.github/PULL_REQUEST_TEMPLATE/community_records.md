## Community LoopNet records

### Contributor

- **Handle:** <!-- your GitHub or Hugging Face handle -->
- **Records file:** `submissions/community/<!-- handle -->.jsonl`
- **Record count:** <!-- N -->
- **Capture method:** <!-- loopgym capture / loopotel / hand-authored -->

### Checklist

- [ ] Every record has `"source": "community"`
- [ ] Every record has `contributor.handle` matching my public handle
- [ ] No API keys, PII, or local file paths in JSONL
- [ ] I license these records under **CC BY 4.0** ([DATACARD.md](../../DATACARD.md))
- [ ] Local validation passes:

```bash
python scripts/validate_community.py submissions/community/MY-FILE.jsonl
```

### Notes

<!-- Optional: env ids, failure modes covered, redaction applied -->

See [guides/COMMUNITY-SUBMISSION.md](../../guides/COMMUNITY-SUBMISSION.md).

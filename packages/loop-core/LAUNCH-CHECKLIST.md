# Launch checklist — v0.1 public stack

Complete these once per machine/account. Automations in CI depend on GitHub secrets or PyPI trusted publishing.

## 1. Discipline repo

- [x] Push [Loop-Engineering](https://github.com/KanakMalpani/Loop-Engineering) narrative mirror

## 2. PyPI (LoopGym → LoopBench)

- [x] [loopgym 0.1.0](https://pypi.org/project/loopgym/) published via GitHub Actions
- [x] [loopbench 0.1.0](https://pypi.org/project/loopbench/) published via GitHub Actions
- [x] Verify: `pip install loopgym loopbench`

## 3. Hugging Face (LoopNet)

- [x] Add **`HF_TOKEN`** to [loopnet secrets](https://github.com/KanakMalpani/loopnet/settings/secrets/actions)
- [x] Upload dataset: [KanakMalpani/loopnet-seed-v0.1](https://huggingface.co/datasets/KanakMalpani/loopnet-seed-v0.1)
- [x] Verify:
   ```python
   from datasets import load_dataset
   ds = load_dataset("KanakMalpani/loopnet-seed-v0.1", split="train")
   ```

## 4. GitHub discoverability

- [x] Repository topics on all stack repos
- [x] **Pin repos on your profile** (manual — no public API): GitHub profile → Customize pins → add Loop Core Engineering, loopnet, LoopGym, LoopBench

## 5. Demo assets

- [x] `assets/demo.gif` on LoopBench README

"""verify.py BEFORE AFTER DECOY_PID REAPLOG... : prove reaper only killed tagged processes."""
import re, sys, os
before = {l.split()[0]: l.split()[1] for l in open(sys.argv[1]) if l.strip()}
after = {l.split()[0]: l.split()[1] for l in open(sys.argv[2]) if l.strip()}
decoy = sys.argv[3]
started, kills = set(), []
for f in sys.argv[4:]:
    for l in open(f):
        m = re.search(r"START tag=(\S+)", l)
        if m: started.add(m.group(1))
        m = re.search(r"KILL pid=(\d+) tag=(\S+) call=(\S+)", l)
        if m: kills.append(m.groups())
bad = [k for k in kills if k[1] not in started]
untagged_before = [p for p, t in before.items() if t == "-"]
killed_pids = {k[0] for k in kills}
untagged_killed = [p for p in untagged_before if p in killed_pids]
print(f"kills={len(kills)} tags_started={len(started)} kills_with_foreign_or_missing_tag={len(bad)} "
      f"untagged_pids_before={len(untagged_before)} untagged_killed={len(untagged_killed)} "
      f"decoy_{decoy}_alive={os.path.exists('/proc/'+decoy)} decoy_in_after={decoy in after}")
sys.exit(1 if bad or untagged_killed or not os.path.exists('/proc/'+decoy) else 0)

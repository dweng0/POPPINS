# Context Efficiency Findings

## Summary

Five categories: dead code, redundant prompt text, duplicate shell calls, fallback that defeats the goal, and minor waste.

---

## 1. Dead Code — `orchestrate.py`

### `run_worker` function (lines 413–617)
Never called. `main()` calls `run_pm_pipeline` from `pm_worker.py` (line 979). The entire function — including its 80-line prompt, subprocess management, and result dict — is unreachable.

**Impact:** ~200 lines of dead code with an embedded agent prompt. No runtime cost, but misleads readers and could cause confusion if `pm_worker.py` is ever replaced.

### `run_merge_agent` function (lines 35–61)
Also never called. `merge_worker_result` (line 717) calls `run_integration_tests` directly. `run_merge_agent` is orphaned.

**Fix:** Delete both functions.

---

## 2. Prompt Repetition — `evolve.sh` worktree prompt (lines 261–400)

The same three facts are stated **3+ times** in the worktree prompt:

| Fact | Stated at lines |
|------|----------------|
| "Read IDENTITY.md first, then BDD_SCENARIO.md" | 266–268, 294–296, 399 |
| "Do NOT read full BDD.md" | 273, 399 |
| "Your target scenario is `$TARGET_SCENARIO`" | 283–287, 319–321, 341, 356 |

The "CRITICAL ANTI-PATTERN" block (lines 326–349) is ~24 lines. The same TDD cycle is duplicated verbatim in the standard prompt (lines 493–513) and in `run_worker`'s dead prompt (orchestrate.py lines 454–490).

**Impact:** Each worktree agent receives ~40 extra lines of repeated instruction before it even starts reading source files. At Haiku pricing this is trivial per call; at scale (many agents, many sessions) it compounds.

**Fix:** Deduplicate into a single clear statement per fact. Move TDD cycle to `IDENTITY.md` so it's shared and not re-stated in every prompt.

---

## 3. Double GitHub API Call — `evolve.sh` lines 105–107

```bash
CI_CONCLUSION=$(gh run list ... --json conclusion --jq '.[0].conclusion')
if [ "$CI_CONCLUSION" = "failure" ]; then
    CI_RUN_ID=$(gh run list ... --json databaseId --jq '.[0].databaseId')
```

Two separate `gh run list` calls to fetch fields from the same run.

**Fix:**
```bash
CI_RUN=$(gh run list --repo "$REPO" --workflow ci.yml --limit 1 \
    --json conclusion,databaseId --jq '.[0]' 2>/dev/null || echo '{}')
CI_CONCLUSION=$(echo "$CI_RUN" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('conclusion','unknown'))")
CI_RUN_ID=$(echo "$CI_RUN" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('databaseId',''))")
```

---

## 4. Fallback Copies Full BDD.md — `evolve.sh` line 236, `orchestrate.py` lines 533, 942

If `extract_scenario.sh` fails, both files fall back to copying the full `BDD.md` (~130KB) as `BDD_SCENARIO.md`:

```bash
# evolve.sh:236
cp "$MAIN_DIR/BDD.md" "$WT_PATH/BDD_SCENARIO.md"

# orchestrate.py:533
run_cmd(f'cp "{main_dir}/BDD.md" "{wt_path}/BDD_SCENARIO.md"')
```

The entire prompt architecture exists to *prevent* agents from reading BDD.md. The fallback silently defeats this goal. An agent hitting the fallback will exhaust its context on a 130KB file it was explicitly told not to read.

**Fix:** On fallback, log a loud warning and `exit 1` (or skip the scenario) rather than silently loading the file that was banned.

---

## 5. Coverage Checker Called Twice — `orchestrate.py` lines 871 and 1150

```python
# line 871 — to find what to work on
uncovered = get_uncovered_scenarios(args.bdd)

# line 1150 — for the journal summary
coverage_out, _, _ = run_cmd("python3 scripts/check_bdd_coverage.py BDD.md", ...)
covered_count = len([l for l in coverage_out.splitlines() if "[x]" in l])
total_count   = len([l for l in coverage_out.splitlines() if "- [" in l])
```

`get_uncovered_scenarios` already parses BDD.md in-process (line 240). The second call re-shells out and re-parses the same file after the session ends.

**Fix:** Track covered/total counts from the first parse, or call `check_bdd_coverage.py` once and pass results forward.

---

## 6. Standard Prompt Reads Full BDD.md — `evolve.sh` line 409

The non-worktree (project-complete / CI-fix-only) prompt tells the agent:

```
2. BDD.md — the spec (this is the ONLY thing you build)
```

No guard against reading the full 130KB file. This path fires when all scenarios are covered or when there's only a CI fix — both situations where BDD.md content is irrelevant.

**Impact:** Low frequency, but when hit, costs a full context window read for no gain.

**Fix:** Either restrict this path to CI-fix-only (skip BDD.md read) or scope it with `BDD_SCENARIO.md` too.

---

## Priority Order

| # | Issue | File | Lines | Impact |
|---|-------|------|-------|--------|
| 1 | Dead `run_worker` + `run_merge_agent` | orchestrate.py | 35–61, 413–617 | Misleading, ~220 dead lines |
| 2 | Fallback copies full BDD.md silently | evolve.sh:236, orchestrate.py:533,942 | — | Silently defeats context guard |
| 3 | Prompt repetition (target, file order, TDD cycle) | evolve.sh | 261–400 | ~40 wasted lines per agent call |
| 4 | Double CI API call | evolve.sh | 105–107 | 1 extra network call per session |
| 5 | Coverage re-parsed twice | orchestrate.py | 871, 1150 | Minor — one extra subprocess |
| 6 | Standard prompt reads full BDD.md | evolve.sh | 409 | Low frequency but high cost when hit |

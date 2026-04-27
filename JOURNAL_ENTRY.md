## 2026-04-27 21:06 — Detect comment prefix by file extension

The PM designed a pure-function unit `detect_comment_prefix(filepath)` that maps file extensions to comment prefix strings (e.g. `.py` → `"#"`), explicitly skipping port/adapter since there is no I/O. The SE implemented the function in `scripts/add_bdd_markers.py` and added the test `test_detect_comment_prefix_by_file_extension` in `tests/test_add_bdd_markers.py` with the correct BDD marker. The tester confirmed all four acceptance criteria pass: marker present, all 139 tests green, coverage shows [x], and design matches the PLAN.

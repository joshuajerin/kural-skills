# Phase 1 verification

## Local evidence

- Tested in this repository's Python 3.12 environment.
- `python -m unittest discover -s tests -v`: **46 tests passed**.
- All 18 catalog entries validate and return explicit dry-run results.
- Tests cover direction signs, lift/gesture serialization, numeric bounds,
  agent schemas, JSON-lines errors, operation status, single active operation,
  cancellation, uncertain transport outcomes, and no automatic submission retry.
- Independent review found five edge cases. Fixes and regression tests cover
  huge integers, bounded backend history, single-snapshot history eviction,
  finite JSON evidence, and SDK-owned request snapshots for failure reporting.
- The seven MCP tests use a real local stdio `ClientSession`: initialization,
  exact 20-tool discovery, catalog schemas, valid wave/stop dry runs, malformed
  requests that leave the session usable, schema isolation, generic handler
  errors, and the installed `kural-skills-mcp --help` entrypoint.
- Python usage examples and documented CLI/JSON request examples ran in dry-run.
- The package builds as a wheel. `ci/github-actions.example.yml` is an optional
  CI template for Python 3.11/3.12/3.13. It is not an installed GitHub workflow;
  no remote test jobs are claimed. Current GitHub authentication lacks workflow
  permission, so publishing does not request broader token scopes.

## What was not tested or implemented

No robot motion, simulation execution through this SDK, hardware execution,
DIMOS live gateway, operator handoff, or physical stop/arrival verification.
Backend contract tests use a test double, not a robot service. No perception or
depth work was performed for this phase.

The current native controls remain separate. A reviewed single-owner runtime
bridge is still required before these skills can execute on the robot. See
[RUNTIME-CONTRACT.md](RUNTIME-CONTRACT.md).

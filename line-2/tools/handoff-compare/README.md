# Handoff Compare

See exactly which files changed between two **fully verified** offline handoffs.
Run from the workspace root, using Python 3.9+ and only its standard library:

```sh
python3 -B line-2/tools/handoff-compare/compare_handoff.py demo
```

The demo verifies the real inherited `line-2/handoff.zip`, builds a proposed
note addition in memory, verifies it, and reports one added file and two unchanged
files. It does not write an archive, extract files, or execute packaged code.
The proposed note is explicitly a demonstration, not an observed worker revision.

For actual deliverables:

```sh
python3 -B line-2/tools/handoff-compare/compare_handoff.py compare line-2/handoff.zip line-2/handoff-inspect.zip
```

JSON on stdout reports sorted additions, removals, modifications with old/new
sizes and SHA-256 digests, unchanged paths, archive hashes and total byte delta.
It distinguishes equal payloads from identical archive bytes. A rename is an
addition plus a removal; no similarity or semantic correctness is inferred.
Both archives are verified completely before any comparison is emitted.

`--before-sha256 HEX` and `--after-sha256 HEX` check independently obtained
archive digests. Locally calculating a digest does not prove authenticity.
`--fail-on-change` returns 2 for a valid payload difference; ordinary successful
comparisons return 0, invalid inputs return 1 with stderr and no JSON report.
Archive metadata-only changes do not trigger exit 2.

The tool reuses the unchanged sibling inspector and packager at fixed workspace
paths; include `line-2/tools/handoff-inspect/inspect_handoff.py` when moving the
comparison tool, and `line-2/tools/handoff/handoff.py` for the demo. Verification
inherits the inspector's defaults: 66 MiB archive, 64 MiB payload, 512 KiB each
for manifest/central metadata, and 1,000 files per archive. Archives must use
classic stored, unencrypted ZIP entries and the v1 HANDOFF manifest. Paths are
relative to the workspace, without traversal or symlinks. No networking,
environment reads, wallet operations, extraction, or upload is provided.
Concurrent ancestor-directory swaps are outside the inherited path guard's
threat model; use an unchanging workspace.

## What happened when tried

The real-source demo and real inherited archive comparison succeeded. Offline
behavioral tests exercise additions, removals, same-size content changes,
renames, unchanged payload with different ZIP metadata, malformed/tampered
archives, trusted-digest mismatch, traversal/symlink refusal, budgets, deterministic
reports, and CLI exit codes. Run the delivered suite from the workspace root:

```sh
python3 -B line-2/tools/handoff-compare/test_compare.py
```

Observed results are recorded in `line-2/checks-23.json`.
